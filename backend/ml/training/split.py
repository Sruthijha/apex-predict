"""Chronological (never random) train/validation/test split.

Race data is a time series: shuffling races across the split would leak
future information (e.g. a driver's whole-career average) into the training
of a model meant to predict an earlier race. See docs/IMPLEMENTATION_PLAN.md
for the documented split.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

TRAIN_SEASONS = list(range(2015, 2023))  # 2015-2022 inclusive
VALIDATION_SEASON = 2023
TEST_SEASON = 2024
# 2025 + partial 2026 are held out entirely from training/tuning/testing here;
# they're used only for the live Model Performance History ("model vs
# reality") backtesting view, and to refit the production-serving model.


@dataclass(frozen=True)
class ChronologicalSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def chronological_split(df: pd.DataFrame) -> ChronologicalSplit:
    return ChronologicalSplit(
        train=df[df["season"].isin(TRAIN_SEASONS)].reset_index(drop=True),
        validation=df[df["season"] == VALIDATION_SEASON].reset_index(drop=True),
        test=df[df["season"] == TEST_SEASON].reset_index(drop=True),
    )
