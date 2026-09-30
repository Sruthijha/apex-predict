"""CLEANED DATA -> FEATURE TABLE. Runs the leakage-safe feature builder over
the processed parquet tables and writes race_features.parquet.
"""

from __future__ import annotations

import argparse
import logging

import pandas as pd

from ml.features.build_features import build_feature_table

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="../data/processed")
    args = parser.parse_args()

    races = pd.read_parquet(f"{args.data_dir}/races.parquet")
    results = pd.read_parquet(f"{args.data_dir}/race_results.parquet")
    qualifying = pd.read_parquet(f"{args.data_dir}/qualifying_results.parquet")
    drivers = pd.read_parquet(f"{args.data_dir}/drivers.parquet")

    features = build_feature_table(results, races, qualifying, drivers)
    out_path = f"{args.data_dir}/race_features.parquet"
    features.to_parquet(out_path, index=False)
    logger.info("Wrote %s (%d rows)", out_path, len(features))


if __name__ == "__main__":
    main()
