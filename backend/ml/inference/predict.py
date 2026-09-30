"""Turns a mode's feature rows into position/DNF predictions using the
production model artifacts."""

from __future__ import annotations

import pandas as pd

from ml.inference.model_registry import ModeArtifacts


def predict_positions_and_dnf(artifacts: ModeArtifacts, feature_rows: pd.DataFrame) -> pd.DataFrame:
    predicted_position = artifacts.position_pipeline.predict(feature_rows)
    dnf_probability = artifacts.dnf_pipeline.predict_proba(feature_rows)[:, 1]

    return pd.DataFrame(
        {
            "driver_id": feature_rows["driver_id"].to_numpy(),
            "constructor_id": feature_rows["constructor_id"].to_numpy(),
            "predicted_position": predicted_position,
            "dnf_probability": dnf_probability,
        }
    )
