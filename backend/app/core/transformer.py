import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import (
    KBinsDiscretizer,
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
    Normalizer,
    OneHotEncoder,
    OrdinalEncoder,
    LabelEncoder,
    FunctionTransformer,
    Binarizer,
    QuantileTransformer,
    PowerTransformer,
    PolynomialFeatures,
)


def date_difference(x, reference_date="2000-01-01"):
    return (pd.to_datetime(x) - pd.Timestamp(reference_date)).dt.days.values.reshape(-1, 1)


def cyclic_datetime(x):
    dates = pd.to_datetime(x.squeeze(), errors="coerce")
    yday = dates.dt.dayofyear

    df = pd.DataFrame()

    yday_rad = 2 * np.pi * yday / 365.25
    df["yday_sin"] = np.sin(yday_rad)
    df["yday_cos"] = np.cos(yday_rad)

    seconds_in_day = dates.dt.hour * 3600 + dates.dt.minute * 60 + dates.dt.second
    time_rad = 2 * np.pi * seconds_in_day / 86400
    df["time_sin"] = np.sin(time_rad)
    df["time_cos"] = np.cos(time_rad)


TRANSFORMERS = {
    "standard_scaler": StandardScaler(),
    "min_max_scaler": MinMaxScaler(),
    "robust_scaler": RobustScaler(),
    "normalizer": Normalizer(),

    "one_hot_encoder": OneHotEncoder(sparse_output=False, handle_unknown="ignore"),
    "ordinal_encoder": OrdinalEncoder(),
    "label_encoder": FunctionTransformer(lambda x: LabelEncoder().fit_transform(x.ravel()).reshape(-1, 1)),

    "simple_imputer": SimpleImputer(),
    "knn_imputer": KNNImputer(),

    "binarizer": Binarizer(),
    "kbins_discretizer": KBinsDiscretizer(),

    "quantile_transformer": QuantileTransformer(),
    "power_transformer": PowerTransformer(),
    "polynomial_features": PolynomialFeatures(),

    # Custom transformers
    "log_transformer": FunctionTransformer(np.log1p, validate=True),
    "sqrt_transform": FunctionTransformer(np.sqrt, validate=True),
    "square_transform": FunctionTransformer(np.square, validate=True),
    "reciprocal_transform": FunctionTransformer(lambda x: 1 / x, validate=True),

    "date_difference": FunctionTransformer(date_difference, validate=True),
    "passthrough": "passthrough",
}


def get_transformer(name, **kwargs):
    transformer = TRANSFORMERS.get(name)

    if transformer is None:
        raise ValueError(f"Invalid transformer name: {name}")

    if kwargs:
        transformer.set_params(**kwargs)

    return transformer