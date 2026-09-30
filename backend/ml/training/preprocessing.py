"""Shared preprocessing: median-impute + scale numeric features, one-hot
encode categoricals. Fit only ever happens on the training split; validation
and test data are transformed with the already-fit preprocessor (rule: never
fit scalers/encoders on anything but training data).

The same preprocessing is used for every algorithm (baselines aside) so the
model comparison is apples-to-apples — XGBoost's native missing-value
handling is deliberately not exploited here, since giving one algorithm a
preprocessing advantage the others don't get would confound the comparison.
"""

from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml.features.feature_columns import CATEGORICAL_FEATURES


def build_preprocessor(numeric_features: list[str]) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )
