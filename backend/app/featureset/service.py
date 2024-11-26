from bson import ObjectId
from minio import S3Error
from app.datasource import service as datasource_service
from app.datasource.model import DataSource, OriginType
from app.featureset.model import FeatureSet
from app.database import SIMPLEFLOW_DATABASE, MINIO_CLIENT
import app.core.profile as profile
import app.core.preprocess as preprocess
import pandas as pd 
import sqlalchemy as sa
import io
from urllib3.exceptions import NewConnectionError, MaxRetryError

from app.featureset.schema import FeatureSetProfiling, FeatureSetCreate


def extract_mysql_to_df(
    connection_detail: dict,
    extract: str
):
    try:
        host = connection_detail["host"]
        port = connection_detail["port"]
        username = connection_detail["username"]
        password = connection_detail["password"]
        database = connection_detail["database"]

        connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        engine = sa.create_engine(connection_string)

        query = extract
        data = pd.read_sql(query, engine)

        return data
    except KeyError:
        raise Exception("Invalid connection details")
    except Exception:
        raise Exception("Failed to extract data")


def profiling(item: FeatureSetProfiling):
    try:
        datasource = datasource_service.get_datasource_by_id(item.datasource_id)

        data = None
        if datasource.origin == OriginType.MYSQL:
            data = extract_mysql_to_df(datasource.connection_detail, item.extract)

        if data is None:
            raise Exception("Failed to profiling data")

        result = list()
        col_types = profile.classify_columns(data)
        for col, col_type in col_types.items():
            col_data = {
                "column": col,
                "type": col_type,
                "count": int(data[col].count()),
                "unique": data[col].nunique(),
                "missing": data[col].isnull().mean() * 100,
                "mean_mode": data[col].mean() if col_type == "numeric" else data[col].mode().values[0],
                "frequency_top5": data[col].value_counts().head(5).to_dict(),
            }
            if col_type == "numeric":
                col_data["suggest_transformer"] = "standard_scaler"
            elif col_type == "category" or col_type == "boolean":
                col_data["suggest_transformer"] = "one_hot_encoder"
            elif col_type == "datetime":
                col_data["suggest_transformer"] = "date_difference"
            elif col_type == "text":
                col_data["suggest_transformer"] = "passthrough"
            else:
                col_data["suggest_transformer"] = "passthrough"

            result.append(col_data)
        return result
    except Exception as e:
        print(e)
        raise Exception("Failed to profiling data")
    

def _transform_featureset(
    item: FeatureSetCreate
):
    try:
        datasource = datasource_service.get_datasource_by_id(item.datasource_id)
    except Exception:
        raise Exception("Failed to get data source")

    try:
        data = None
        if datasource.origin == OriginType.MYSQL:
            data = extract_mysql_to_df(datasource.connection_detail, item.extract)

        if data is None:
            raise Exception("Failed to extract data")

        feature_transformers, target_transformer = preprocess.build_transformer(
            df=data,
            features_metadata=item.features,
            target_metadata=item.target,
        )

        X_transformed = feature_transformers.transform(data)
        feature_names = list()
        for name in feature_transformers.get_feature_names_out():
            feature_names.append(name.split("__")[1])
        X_transformed_df = pd.DataFrame(X_transformed, columns=feature_names)

        target_name = item.target.column
        if target_transformer:
            y_transformed = target_transformer.transform(data)
            y_transformed_df = pd.DataFrame(y_transformed, columns=[target_name])
        else:
            y_transformed_df = data[[target_name]].reset_index(drop=True)

        df_transformed = pd.concat([X_transformed_df, y_transformed_df], axis=1)
        return df_transformed

    except Exception:
        raise Exception("Failed to transform data")


def create_featureset(
    item: FeatureSetCreate
):
    try:
        featureset = FeatureSet(**item.model_dump())
        res = SIMPLEFLOW_DATABASE["featureset"].insert_one(featureset.model_dump())
        featureset.id = str(res.inserted_id)
    except Exception:
        raise Exception("Failed to save feature set")

    data = _transform_featureset(item)

    csv_buffer = io.BytesIO()
    data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    try:
        bucket_name = "simpleflow"
        if not MINIO_CLIENT.bucket_exists(bucket_name):
            MINIO_CLIENT.make_bucket(bucket_name)

        MINIO_CLIENT.put_object(
            bucket_name=bucket_name,
            object_name=f"featureset/{featureset.id}",
            data=csv_buffer,
            length=csv_buffer.getbuffer().nbytes,
            content_type="application/csv",
        )

    except (S3Error, ConnectionError, NewConnectionError, MaxRetryError) as e:
        print(e)
        SIMPLEFLOW_DATABASE["featureset"].delete_one({"_id": ObjectId(featureset.id)})
        raise Exception("Failed to save transformed data")
        
    return data.head().to_json()

    

def get_all_featuresets():
    try:
        result = list()
        data = SIMPLEFLOW_DATABASE["featureset"].find()

        for item in data:
            item["_id"] = str(item["_id"])
            result.append(FeatureSet(**item))

        return result
    except Exception:
        raise Exception("Failed to get feature sets due to an unexpected error.")
    

def get_featureset_by_id(id: str):
    try:
        data = SIMPLEFLOW_DATABASE["featureset"].find_one({"_id": ObjectId(id)})
        data["_id"] = str(data["_id"])
        return FeatureSet(
            **data
        )
    except Exception:
        raise Exception("Failed to get feature set due to an unexpected error.")


def delete_featureset_by_id(id: str):
    try:
        SIMPLEFLOW_DATABASE["featureset"].delete_one({"_id": ObjectId(id)})
    except Exception:
        raise Exception("Failed to delete feature set due to an unexpected error.")

    try:
        MINIO_CLIENT.remove_object("simpleflow", f"featureset/{id}")
    except (S3Error, ConnectionError, NewConnectionError, MaxRetryError) as e:
        print(e)
        raise Exception("Failed to delete feature set data")