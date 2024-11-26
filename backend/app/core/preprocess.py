import pandas as pd
from sklearn.compose import ColumnTransformer

from app.core.transformer import get_transformer
from test import target_column


def convert_column_type(df: pd.DataFrame, col: str, col_type: str):
    try:
        if col_type == "numeric":
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif col_type == "datetime":
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif col_type == "category" or col_type == "boolean" or col_type == "ordinal":
            df[col] = df[col].astype("category")
        elif col_type == "text":
            df[col] = df[col].astype(str)
        else:
            print(f"Warning: Unsupported type '{col_type}' for column '{col}'. Skipping type conversion.")
    except Exception as e:
        print(f"Failed to convert column '{col}' to type '{col_type}'")
    
    return df


def treat_as_missing(df: pd.DataFrame, col: str, missing_values: list):
    try:
        if len(missing_values) > 0:
            df[col] = df[col].replace(missing_values, pd.NA)
    except Exception as e:
        print(f"Failed to treat missing values for column '{col}'")
    
    return df


def drop_columns(df: pd.DataFrame, columns: list):
    try:
        df = df.drop(columns=columns)
    except Exception as e:
        print(f"Failed to drop columns: {columns}")
    
    return df


def drop_duplicates(df: pd.DataFrame):
    try:
        df = df.drop_duplicates()
    except Exception as e:
        print("Failed to drop duplicates")
    
    return df


def handle_missing_values(df: pd.DataFrame):
    try:
        missing_percentages = df.isnull().mean() * 100
        high_missing_cols = missing_percentages[missing_percentages > 35].index.tolist()
        if len(high_missing_cols) > 0:
            print(f"Columns with high missing values: {high_missing_cols} will be dropped")

        df = df.drop(columns=high_missing_cols)
        low_missing_cols = missing_percentages[(missing_percentages > 0) & (missing_percentages < 5)].index.tolist()
        if len(low_missing_cols) > 0:
            print(f"Columns with low missing values: {low_missing_cols} will be handled using method dropna")
        df = df.dropna(subset=low_missing_cols)

        # Other will impute in ColumnTransformer
    except Exception as e:
        print(f"Failed to handle missing values")
    
    return df


def build_transformer(
    df: pd.DataFrame,
    features_metadata: list,
    target_metadata,
):

    feature_names = [column_metadata.column for column_metadata in features_metadata]
    target_name = target_metadata.column

    used_df = df[feature_names + [target_name]].copy()

    feature_transformers = []
    for column_metadata in features_metadata:
        col_name = column_metadata.column
        col_type = column_metadata.data_type
        transformer_name = column_metadata.transformation

        used_df = convert_column_type(used_df, col_name, col_type)

        transformer = get_transformer(transformer_name)
        feature_transformers.append((col_name, transformer, [col_name]))

    used_df = handle_missing_values(used_df)

    feature_column_transformer = ColumnTransformer(transformers=feature_transformers)
    feature_column_transformer.fit(used_df)

    target_transformer_name = target_metadata.transformation

    target_column_transformer = get_transformer(target_transformer_name)

    if target_column_transformer == "passthrough":
        target_column_transformer = None
    else:
        target_column_transformer.fit(df[[target_name]])

    return feature_column_transformer, target_column_transformer