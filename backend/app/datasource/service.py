from app.database import SIMPLEFLOW_DATABASE
from app.datasource.model import DataSource
from app.datasource.schema import DataSourceCreate, DataSourceUpdate
from app.datasource.model import OriginType
from pymongo.errors import PyMongoError
from bson import ObjectId
import sqlalchemy as sa


COLLECTION = "datasource"


def check_mysql_datasource(
    connection_detail: dict,
):
    try:
        host = connection_detail["host"]
        port = connection_detail["port"]
        username = connection_detail["username"]
        password = connection_detail["password"]
        database = connection_detail["database"]

    except KeyError:
        raise Exception("Missing required fields for origin MySQL")

    connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    engine = sa.create_engine(connection_string)

    try:
        # Only check if connection is successful
        with engine.connect():
            return True
    except Exception:
        raise Exception("Failed to connect to MySQL")
    finally:
        engine.dispose()


def create_datasource(
    item: DataSourceCreate
):
    data = None
    try:
        if item.origin == OriginType.MYSQL:
            if check_mysql_datasource(item.connection_detail):
                data = DataSource(**item.model_dump())
        else:
            raise Exception("Unsupported data source type")
    except Exception as e:
        raise e

    try:
        if data:
            SIMPLEFLOW_DATABASE[COLLECTION].insert_one(data.model_dump())
            return data
    except PyMongoError:
        raise Exception("Failed to create data source due to a database error.")
    

def get_all_datasources():
    try:
        result = list()
        data = SIMPLEFLOW_DATABASE[COLLECTION].find()

        for item in data:
            item["_id"] = str(item["_id"])
            result.append(DataSource(**item))

        return result
    except PyMongoError as e:
        print(e)
        raise Exception("Failed to get data sources due to a database error.")
    except Exception as e:
        print(e)
        raise Exception("Failed to get data sources due to an unexpected error.")
    

def get_datasource_by_id(id: str):
    try:
        data = SIMPLEFLOW_DATABASE[COLLECTION].find_one({"_id": ObjectId(id)})
        if data:
            data["_id"] = str(data["_id"])
            response = DataSource(**data)
            return response
        else:
            raise Exception("Data source not found")
    except PyMongoError:
        raise Exception("Failed to get data source due to a database error.")
    except Exception:
        raise Exception("Failed to get data source due to an unexpected error.")


def update_datasource_by_id(id: str, item: DataSourceUpdate):
    try:
        data = SIMPLEFLOW_DATABASE[COLLECTION].find_one({"_id": ObjectId(id)})
        if data:
            data.update(item.model_dump())
            SIMPLEFLOW_DATABASE[COLLECTION].update_one({"_id": ObjectId(id)}, {"$set": data})
            return DataSource(**data)
        else:
            raise Exception("Data source not found")
    except PyMongoError:
        raise Exception("Failed to update data source due to a database error.")
    except Exception:
        raise Exception("Failed to update data source due to an unexpected error.")


def delete_datasource_by_id(id: str):
    try:
        data = SIMPLEFLOW_DATABASE[COLLECTION].find_one({"_id": ObjectId(id)})
        if data:
            SIMPLEFLOW_DATABASE[COLLECTION].delete_one({"_id": ObjectId(id)})
            return DataSource(**data)
        else:
            raise Exception("Data source not found")
    except PyMongoError:
        raise Exception("Failed to delete data source due to a database error.")
    except Exception:
        raise Exception("Failed to delete data source due to an unexpected error.")