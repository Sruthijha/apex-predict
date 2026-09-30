"""Orchestrates the full training run for both prediction modes and saves:

  - An "evaluation" record per mode: honest MAE/Spearman/LogLoss/Brier/etc.
    computed on the 2024 test season, using models fit on 2015-2022 only and
    tuned against 2023 only. These are the numbers shown on the Model Lab
    page — never fabricated, never touched by the test set during fitting.
  - A "production" pipeline per mode: the same winning algorithm/hyperparams,
    refit on ALL available history (2015 through the most recent completed
    race) so live predictions for the upcoming Grand Prix use every result
    we actually have. This is standard practice (evaluate honestly on a
    frozen holdout, then refit the validated recipe on everything before
    shipping) and is documented as such rather than conflated with the
    evaluation numbers.
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

from ml.evaluation.metrics import classification_metrics, regression_metrics
from ml.features.feature_columns import FEATURE_VERSION, NUMERIC_FEATURES_BY_MODE
from ml.training.dataset import add_targets
from ml.training.preprocessing import build_preprocessor
from ml.training.split import TEST_SEASON, TRAIN_SEASONS, VALIDATION_SEASON, chronological_split
from ml.training.train_dnf_model import run_dnf_bakeoff
from ml.training.train_position_model import run_position_bakeoff

logger = logging.getLogger(__name__)
MODES = ["pre_weekend", "post_qualifying"]


def _refit_production_position(df: pd.DataFrame, mode: str, algorithm) -> Pipeline:
    numeric_features = NUMERIC_FEATURES_BY_MODE[mode]
    preprocessor = build_preprocessor(numeric_features)
    X = preprocessor.fit_transform(df)
    model = clone(algorithm)
    model.fit(X, df["target_position"])
    return Pipeline(steps=[("preprocess", preprocessor), ("model", model)])


def _refit_production_dnf(df: pd.DataFrame, mode: str, algorithm) -> Pipeline:
    numeric_features = NUMERIC_FEATURES_BY_MODE[mode]
    preprocessor = build_preprocessor(numeric_features)
    X = preprocessor.fit_transform(df)
    y = df["target_dnf"]
    calibrated = CalibratedClassifierCV(clone(algorithm), method="sigmoid", cv=5)
    calibrated.fit(X, y)
    return Pipeline(steps=[("preprocess", preprocessor), ("model", calibrated)])


def train_all(feature_table_path: str, output_dir: str) -> dict:
    feature_table = pd.read_parquet(feature_table_path)
    df = add_targets(feature_table)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    registry = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feature_version": FEATURE_VERSION,
        "train_seasons": f"{TRAIN_SEASONS[0]}-{TRAIN_SEASONS[-1]}",
        "validation_season": VALIDATION_SEASON,
        "test_season": TEST_SEASON,
        "modes": {},
    }

    for mode in MODES:
        logger.info("=== Training mode: %s ===", mode)
        split = chronological_split(df)

        position_result = run_position_bakeoff(split, mode)
        dnf_result = run_dnf_bakeoff(split, mode)

        joblib.dump(position_result["pipeline"], output_path / f"{mode}_position_eval.joblib")
        joblib.dump(dnf_result["pipeline"], output_path / f"{mode}_dnf_eval.joblib")

        # Production refit: same chosen algorithm, all available history.
        all_rows = df.dropna(subset=["target_position"])
        production_position = _refit_production_position(
            all_rows, mode, position_result["pipeline"].named_steps["model"]
        )
        production_dnf = _refit_production_dnf(
            all_rows, mode, dnf_result["pipeline"].named_steps["model"].estimator
        )
        joblib.dump(production_position, output_path / f"{mode}_position_production.joblib")
        joblib.dump(production_dnf, output_path / f"{mode}_dnf_production.joblib")

        registry["modes"][mode] = {
            "position_model": {
                "algorithm": position_result["algorithm"],
                "residual_std": position_result["residual_std"],
                "validation_scores": position_result["validation_scores"],
                "validation_baselines": position_result["validation_baselines"],
                "test_metrics": position_result["test_metrics"],
                "test_baselines": position_result["test_baselines"],
            },
            "dnf_model": {
                "algorithm": dnf_result["algorithm"],
                "base_rate": dnf_result["base_rate"],
                "validation_scores": dnf_result["validation_scores"],
                "validation_baseline": dnf_result["validation_baseline"],
                "test_metrics": dnf_result["test_metrics"],
                "test_baseline": dnf_result["test_baseline"],
                "calibration_curve": dnf_result["calibration_curve"],
            },
        }

        logger.info(
            "[%s] position best=%s test MAE=%.3f | dnf best=%s test log_loss=%.4f",
            mode,
            position_result["algorithm"],
            position_result["test_metrics"]["mae"],
            dnf_result["algorithm"],
            dnf_result["test_metrics"]["log_loss"],
        )

    registry_path = output_path / "model_registry.json"
    registry_path.write_text(json.dumps(registry, indent=2))
    logger.info("Wrote %s", registry_path)
    return registry


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature-table", default="../data/processed/race_features.parquet")
    parser.add_argument("--output-dir", default="../data/models")
    args = parser.parse_args()
    train_all(args.feature_table, args.output_dir)


if __name__ == "__main__":
    main()
