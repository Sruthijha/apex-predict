"""Model inference tests against the real trained production artifacts
(data/models/, produced by ml/training/train_all.py). These don't retrain
anything - they confirm the saved pipelines load and produce sane,
well-formed predictions on hand-built feature rows.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.features.feature_columns import CATEGORICAL_FEATURES, NUMERIC_FEATURES_BY_MODE
from ml.inference.model_registry import load_mode_artifacts
from ml.inference.predict import predict_positions_and_dnf

MODEL_DIR = str(Path(__file__).resolve().parents[2] / "data" / "models")

pytestmark = pytest.mark.skipif(
    not (Path(MODEL_DIR) / "model_registry.json").exists(),
    reason="Trained model artifacts not present - run ml/training/train_all.py first.",
)


def _synthetic_feature_rows(mode: str, n: int = 5) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    columns = NUMERIC_FEATURES_BY_MODE[mode]
    data = {col: rng.uniform(0, 20, size=n) for col in columns}
    data["driver_id"] = [f"driver_{i}" for i in range(n)]
    data["constructor_id"] = [f"team_{i % 2}" for i in range(n)]
    for cat in CATEGORICAL_FEATURES:
        data[cat] = "permanent"
    return pd.DataFrame(data)


@pytest.mark.parametrize("mode", ["pre_weekend", "post_qualifying"])
def test_predict_returns_one_row_per_driver_with_valid_ranges(mode: str):
    artifacts = load_mode_artifacts(MODEL_DIR, mode)
    feature_rows = _synthetic_feature_rows(mode)

    predictions = predict_positions_and_dnf(artifacts, feature_rows)

    assert len(predictions) == len(feature_rows)
    assert set(predictions["driver_id"]) == set(feature_rows["driver_id"])
    assert (predictions["dnf_probability"] >= 0).all()
    assert (predictions["dnf_probability"] <= 1).all()
    assert predictions["predicted_position"].notna().all()


def test_post_qualifying_grid_position_meaningfully_shifts_prediction():
    """Sanity check that the model actually uses grid_position: two otherwise
    identical drivers with very different grid slots should get different
    predicted positions in post_qualifying mode."""
    artifacts = load_mode_artifacts(MODEL_DIR, "post_qualifying")
    rows = _synthetic_feature_rows("post_qualifying", n=2)
    rows.loc[0, "grid_position"] = 1
    rows.loc[1, "grid_position"] = 20
    # keep every other feature identical so grid_position is the only difference
    for col in rows.columns:
        if col not in ("driver_id", "constructor_id", "grid_position"):
            rows.loc[1, col] = rows.loc[0, col]

    predictions = predict_positions_and_dnf(artifacts, rows).set_index("driver_id")
    front_row_pred = predictions.loc["driver_0", "predicted_position"]
    back_row_pred = predictions.loc["driver_1", "predicted_position"]
    assert front_row_pred < back_row_pred
