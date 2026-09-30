"""Computes and saves SHAP feature importance for each mode's position model,
using the *evaluation* pipeline (fit on train only) so the explanation is
grounded in the same honestly-evaluated model reported in the Model Lab.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import joblib
import pandas as pd

from ml.evaluation.feature_importance import compute_feature_importance
from ml.training.dataset import add_targets
from ml.training.split import chronological_split

logger = logging.getLogger(__name__)
MODES = ["pre_weekend", "post_qualifying"]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature-table", default="../data/processed/race_features.parquet")
    parser.add_argument("--model-dir", default="../data/models")
    args = parser.parse_args()

    feature_table = pd.read_parquet(args.feature_table)
    df = add_targets(feature_table)
    model_dir = Path(args.model_dir)

    for mode in MODES:
        split = chronological_split(df)
        pipeline = joblib.load(model_dir / f"{mode}_position_eval.joblib")

        background = split.train.sample(min(200, len(split.train)), random_state=42)
        importance = compute_feature_importance(pipeline, background, split.test)

        out_path = model_dir / f"feature_importance_{mode}.json"
        out_path.write_text(json.dumps(importance, indent=2))
        logger.info("Wrote %s (top 5: %s)", out_path, [f["feature"] for f in importance[:5]])


if __name__ == "__main__":
    main()
