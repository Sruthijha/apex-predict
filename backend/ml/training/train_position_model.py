"""Bake-off for the finishing-position ranking model: baselines vs Linear
Regression vs Random Forest vs XGBoost, per prediction mode.

Algorithm/hyperparameter selection uses ONLY the validation season (2023);
the test season (2024) is scored exactly once per mode, with the already-
selected configuration, to report final numbers. See ml/training/split.py.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from ml.evaluation.metrics import regression_metrics
from ml.features.feature_columns import NUMERIC_FEATURES_BY_MODE
from ml.training.preprocessing import build_preprocessor
from ml.training.split import ChronologicalSplit

logger = logging.getLogger(__name__)

RF_GRID = [
    {"n_estimators": 200, "max_depth": 8, "min_samples_leaf": 5, "random_state": 42},
    {"n_estimators": 400, "max_depth": None, "min_samples_leaf": 2, "random_state": 42},
]
XGB_GRID = [
    {"n_estimators": 200, "max_depth": 3, "learning_rate": 0.1, "random_state": 42},
    {"n_estimators": 400, "max_depth": 4, "learning_rate": 0.05, "random_state": 42},
]


def _historical_average_baseline(df: pd.DataFrame, fallback: float) -> np.ndarray:
    return df["driver_recent_finish_mean_5"].fillna(fallback).to_numpy()


def _grid_baseline(df: pd.DataFrame) -> np.ndarray:
    return df["grid_position"].to_numpy(dtype=float)


def run_position_bakeoff(split: ChronologicalSplit, mode: str) -> dict:
    numeric_features = NUMERIC_FEATURES_BY_MODE[mode]
    y_train = split.train["target_position"]
    fallback_mean = float(y_train.mean())

    preprocessor = build_preprocessor(numeric_features)
    preprocessor.fit(split.train)
    X_train = preprocessor.transform(split.train)
    X_val = preprocessor.transform(split.validation)

    candidates: dict[str, object] = {"linear_regression": LinearRegression()}
    for i, params in enumerate(RF_GRID):
        candidates[f"random_forest_{i}"] = RandomForestRegressor(**params)
    for i, params in enumerate(XGB_GRID):
        candidates[f"xgboost_{i}"] = XGBRegressor(**params, objective="reg:squarederror")

    val_scores = {}
    fitted = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        fitted[name] = model
        preds = model.predict(X_val)
        metrics = regression_metrics(
            split.validation.assign(_pred=preds), "target_position", "_pred"
        )
        val_scores[name] = metrics
        logger.info("[%s] %s val MAE=%.3f spearman=%.3f", mode, name, metrics["mae"], metrics["spearman_mean"] or 0)

    best_name = min(val_scores, key=lambda n: val_scores[n]["mae"])
    best_model = fitted[best_name]

    baseline_val = {
        "historical_average": regression_metrics(
            split.validation.assign(_pred=_historical_average_baseline(split.validation, fallback_mean)),
            "target_position",
            "_pred",
        )
    }
    if mode == "post_qualifying":
        baseline_val["grid_position"] = regression_metrics(
            split.validation.assign(_pred=_grid_baseline(split.validation)), "target_position", "_pred"
        )

    X_test = preprocessor.transform(split.test)
    test_metrics = regression_metrics(
        split.test.assign(_pred=best_model.predict(X_test)), "target_position", "_pred"
    )
    baseline_test = {
        "historical_average": regression_metrics(
            split.test.assign(_pred=_historical_average_baseline(split.test, fallback_mean)),
            "target_position",
            "_pred",
        )
    }
    if mode == "post_qualifying":
        baseline_test["grid_position"] = regression_metrics(
            split.test.assign(_pred=_grid_baseline(split.test)), "target_position", "_pred"
        )

    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("model", best_model)])
    residual_std = float(
        np.std(split.validation["target_position"].to_numpy() - best_model.predict(X_val))
    )

    return {
        "mode": mode,
        "algorithm": best_name,
        "pipeline": pipeline,
        "residual_std": residual_std,
        "validation_scores": val_scores,
        "validation_baselines": baseline_val,
        "test_metrics": test_metrics,
        "test_baselines": baseline_test,
    }
