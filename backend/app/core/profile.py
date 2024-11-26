import pandas as pd


def _is_datetime(series):
    try:
        pd.to_datetime(series, errors='coerce')
        return True
    except ValueError:
        return False


def _classify_column(col_series: pd.Series):
    unique_values = col_series.unique()
    num_unique_values = len(unique_values)

    if num_unique_values == 2:
        return "boolean"
    elif col_series.dtype in ["int64", "int32", "float64", "float32"]:
        return "numeric"
    elif num_unique_values / len(col_series) < 0.5:
        return "category"
    elif col_series.dtype == "datetime64[ns]" or _is_datetime(col_series):
        return "datetime"
    else:
        return "text"
    

def classify_columns(df: pd.DataFrame):
    return {col: _classify_column(df[col]) for col in df.columns}


