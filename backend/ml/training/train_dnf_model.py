"""Bake-off for the DNF (did-not-finish) risk classifier, per prediction mode.

DNF is modeled separately from finishing position: it's driven by mechanical
reliability and incident risk, not relative pace, so it doesn't fit naturally
into a ranking/regression target. Its probability feeds the Monte Carlo
simulation (ml/simulation) as the chance a driver fails to finish at all.

As with the position model, algorithm selection uses only the validation
season; the test season is scored once with the selected configuration.
"""

from __future__ import annotations

import logging

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from ml.evaluation.metrics import calibration_curve_points, classification_metrics
from ml.features.feature_columns import NUMERIC_FEATURES_BY_MODE
from ml.training.preprocessing import build_preprocessor
from ml.training.split import ChronologicalSplit

logger = logging.getLogger(__name__)

RF_GRID = [{"n_estimators": 300, "max_depth": 6, "min_samples_leaf": 10, "random_state": 42}]
XGB_GRID = [
    {"n_estimators": 200, "max_depth": 3, "learning_rate": 0.1, "random_state": 42},
    {"n_estimators": 300, "max_depth": 4, "learning_rate": 0.05, "random_state": 42},
]


def run_dnf_bakeoff(split: ChronologicalSplit, mode: str) -> dict:
    numeric_features = NUMERIC_FEATURES_BY_MODE[mode]
    y_train = split.train["target_dnf"]
    base_rate = float(y_train.mean())

    preprocessor = build_preprocessor(numeric_features)
    preprocessor.fit(split.train)
    X_train = preprocessor.transform(split.train)
    X_val = preprocessor.transform(split.validation)
    y_val = split.validation["target_dnf"].to_numpy()

    candidates: dict[str, object] = {"logistic_regression": LogisticRegression(max_iter=1000)}
    for i, params in enumerate(RF_GRID):
        candidates[f"random_forest_{i}"] = RandomForestClassifier(**params)
    for i, params in enumerate(XGB_GRID):
        candidates[f"xgboost_{i}"] = XGBClassifier(**params, eval_metric="logloss")

    val_scores, fitted = {}, {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        fitted[name] = model
        proba = model.predict_proba(X_val)[:, 1]
        metrics = classification_metrics(y_val, proba)
        val_scores[name] = metrics
        logger.info("[%s] %s val log_loss=%.4f brier=%.4f", mode, name, metrics["log_loss"], metrics["brier_score"])

    baseline_proba_val = np.full_like(y_val, fill_value=base_rate, dtype=float)
    baseline_val = classification_metrics(y_val, baseline_proba_val)

    best_name = min(val_scores, key=lambda n: val_scores[n]["log_loss"])
    best_raw_model = fitted[best_name]

    # Calibrate the chosen model's probabilities using the validation set.
    calibrated = CalibratedClassifierCV(best_raw_model, method="sigmoid", cv="prefit")
    calibrated.fit(X_val, y_val)

    X_test = preprocessor.transform(split.test)
    y_test = split.test["target_dnf"].to_numpy()
    test_proba = calibrated.predict_proba(X_test)[:, 1]
    test_metrics = classification_metrics(y_test, test_proba)
    baseline_proba_test = np.full_like(y_test, fill_value=base_rate, dtype=float)
    baseline_test = classification_metrics(y_test, baseline_proba_test)
    calibration_curve = calibration_curve_points(y_test, test_proba)

    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("model", calibrated)])

    return {
        "mode": mode,
        "algorithm": best_name,
        "pipeline": pipeline,
        "base_rate": base_rate,
        "validation_scores": val_scores,
        "validation_baseline": baseline_val,
        "test_metrics": test_metrics,
        "test_baseline": baseline_test,
        "calibration_curve": calibration_curve,
    }
