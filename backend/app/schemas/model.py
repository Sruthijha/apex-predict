from __future__ import annotations

from pydantic import BaseModel


class ModelModeMetrics(BaseModel):
    mode: str
    position_algorithm: str
    position_test_metrics: dict
    position_test_baselines: dict
    dnf_algorithm: str
    dnf_test_metrics: dict
    dnf_test_baseline: dict
    dnf_calibration_curve: list[dict]
    feature_importance: list[dict]


class ModelMetricsResponse(BaseModel):
    trained_at: str
    feature_version: str
    train_seasons: str
    validation_season: int
    test_season: int
    modes: list[ModelModeMetrics]
