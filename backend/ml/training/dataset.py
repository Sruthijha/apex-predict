"""Attach prediction targets to the leakage-safe feature table.

`position` is always populated in this dataset (Ergast/Jolpica classifies
every starter, including retirements, by distance completed), so no
imputation or row-dropping is needed for the regression target.
"""

from __future__ import annotations

import pandas as pd


def add_targets(feature_table: pd.DataFrame) -> pd.DataFrame:
    df = feature_table.copy()
    df["target_position"] = df["position"].astype(float)
    df["target_win"] = (df["position"] == 1).astype(int)
    df["target_podium"] = (df["position"] <= 3).astype(int)
    df["target_top5"] = (df["position"] <= 5).astype(int)
    df["target_points"] = (df["points"] > 0).astype(int)
    df["target_dnf"] = df["dnf"].astype(int)
    return df
