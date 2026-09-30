"""Loads trained model artifacts + their metadata, with a small in-process
cache so a running API server doesn't re-read joblib files on every request.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class ModeArtifacts:
    mode: str
    position_pipeline: Pipeline
    dnf_pipeline: Pipeline
    residual_std: float
    algorithm: str
    metrics: dict


@lru_cache
def _load_registry(model_dir: str) -> dict:
    return json.loads((Path(model_dir) / "model_registry.json").read_text())


@lru_cache
def load_mode_artifacts(model_dir: str, mode: str) -> ModeArtifacts:
    registry = _load_registry(model_dir)
    mode_meta = registry["modes"][mode]

    position_pipeline = joblib.load(Path(model_dir) / f"{mode}_position_production.joblib")
    dnf_pipeline = joblib.load(Path(model_dir) / f"{mode}_dnf_production.joblib")

    return ModeArtifacts(
        mode=mode,
        position_pipeline=position_pipeline,
        dnf_pipeline=dnf_pipeline,
        residual_std=mode_meta["position_model"]["residual_std"],
        algorithm=mode_meta["position_model"]["algorithm"],
        metrics=mode_meta,
    )


def model_version_string(model_dir: str) -> str:
    registry = _load_registry(model_dir)
    return f"{registry['feature_version']}-{registry['trained_at'][:10]}"
