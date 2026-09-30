from __future__ import annotations

import json
from pathlib import Path

from app.schemas.model import ModelMetricsResponse, ModelModeMetrics


def _strip_prefix(feature_name: str) -> str:
    return feature_name.split("__", 1)[-1]


def get_model_metrics(model_dir: str) -> ModelMetricsResponse:
    base = Path(model_dir)
    registry = json.loads((base / "model_registry.json").read_text())

    modes = []
    for mode, mode_data in registry["modes"].items():
        importance_path = base / f"feature_importance_{mode}.json"
        importance = json.loads(importance_path.read_text()) if importance_path.exists() else []
        importance = [{"feature": _strip_prefix(f["feature"]), "importance": f["mean_abs_shap"]} for f in importance]

        modes.append(
            ModelModeMetrics(
                mode=mode,
                position_algorithm=mode_data["position_model"]["algorithm"],
                position_test_metrics=mode_data["position_model"]["test_metrics"],
                position_test_baselines=mode_data["position_model"]["test_baselines"],
                dnf_algorithm=mode_data["dnf_model"]["algorithm"],
                dnf_test_metrics=mode_data["dnf_model"]["test_metrics"],
                dnf_test_baseline=mode_data["dnf_model"]["test_baseline"],
                dnf_calibration_curve=mode_data["dnf_model"]["calibration_curve"],
                feature_importance=importance,
            )
        )

    return ModelMetricsResponse(
        trained_at=registry["trained_at"],
        feature_version=registry["feature_version"],
        train_seasons=registry["train_seasons"],
        validation_season=registry["validation_season"],
        test_season=registry["test_season"],
        modes=modes,
    )
