"""Leakage-safe feature engineering.

The one rule that matters: every column here must be computable using only
information available *before* the target race started. Concretely, every
rolling/expanding/cumulative statistic is computed on a chronologically
sorted per-entity series and then `.shift(1)`-ed *before* the window
aggregation runs, so a race's own result never contributes to its own
feature row. See backend/tests/test_no_leakage.py for the tests that pin
this behavior down.

Two feature sets are produced from the same computation, differing only in
which columns are kept (see ml/features/feature_columns.py):
  - pre_weekend: driver/constructor form + circuit history only.
  - post_qualifying: pre_weekend + this weekend's actual grid position and
    qualifying gap-to-pole (both only knowable after qualifying happens).
"""

from __future__ import annotations

import pandas as pd

from ml.features.circuit_types import get_circuit_type

DRIVER_SHORT_WINDOW = 3
DRIVER_MEDIUM_WINDOW = 5
DRIVER_DNF_WINDOW = 10
CONSTRUCTOR_MEDIUM_WINDOW = 5
CONSTRUCTOR_DNF_WINDOW = 10
FORM_EWM_SPAN = 5


def _shifted_rolling(series: pd.Series, window: int) -> pd.Series:
    """Rolling mean over the window ending at the *previous* row."""
    return series.shift(1).rolling(window=window, min_periods=1).mean()


def _shifted_expanding(series: pd.Series) -> pd.Series:
    """Expanding (all-history) mean over rows strictly before the current one."""
    return series.shift(1).expanding(min_periods=1).mean()


def _build_driver_features(results: pd.DataFrame) -> pd.DataFrame:
    """One row per (season, round, driver_id) of driver-level rolling features.
    `results` must already be sorted by driver_id then chronologically."""
    df = results.copy()
    g = df.groupby("driver_id", group_keys=False)

    df["driver_recent_finish_mean_3"] = g["position"].apply(lambda s: _shifted_rolling(s, DRIVER_SHORT_WINDOW))
    df["driver_recent_finish_mean_5"] = g["position"].apply(lambda s: _shifted_rolling(s, DRIVER_MEDIUM_WINDOW))
    df["driver_recent_grid_mean_5"] = g["grid"].apply(lambda s: _shifted_rolling(s, DRIVER_MEDIUM_WINDOW))
    df["driver_recent_points_mean_5"] = g["points"].apply(lambda s: _shifted_rolling(s, DRIVER_MEDIUM_WINDOW))
    df["driver_dnf_rate_recent_10"] = g["dnf"].apply(
        lambda s: _shifted_rolling(s.astype(float), DRIVER_DNF_WINDOW)
    )
    df["driver_positions_gained_avg_5"] = g.apply(
        lambda grp: _shifted_rolling(grp["grid"] - grp["position"], DRIVER_MEDIUM_WINDOW),
        include_groups=False,
    )
    # Exponentially-weighted recent points: like recent_points_mean_5 but
    # weights the most recent races more heavily, so it reacts faster to a
    # driver trending up or down in form than a flat rolling average does.
    df["driver_recent_form_score"] = g["points"].apply(
        lambda s: s.shift(1).ewm(span=FORM_EWM_SPAN, min_periods=1).mean()
    )

    df["driver_season_points_before_race"] = (
        df.groupby(["driver_id", "season"], group_keys=False)["points"]
        .apply(lambda s: s.shift(1).cumsum())
        .fillna(0.0)
    )

    circuit_group = df.groupby(["driver_id", "circuit_id"], group_keys=False)
    df["driver_circuit_avg_finish"] = circuit_group["position"].apply(_shifted_expanding)

    return df


def _build_constructor_features(results: pd.DataFrame) -> pd.DataFrame:
    """One row per (season, round, constructor_id) of constructor-level rolling
    features, aggregated first across that constructor's drivers per race."""
    race_level = (
        results.groupby(["season", "round", "date", "circuit_id", "constructor_id"])
        .agg(
            constructor_race_points=("points", "sum"),
            constructor_race_avg_finish=("position", "mean"),
            constructor_race_dnf_rate=("dnf", "mean"),
        )
        .reset_index()
        .sort_values(["constructor_id", "date", "round"])
    )

    g = race_level.groupby("constructor_id", group_keys=False)
    race_level["constructor_recent_points_mean_5"] = g["constructor_race_points"].apply(
        lambda s: _shifted_rolling(s, CONSTRUCTOR_MEDIUM_WINDOW)
    )
    race_level["constructor_recent_finish_mean_5"] = g["constructor_race_avg_finish"].apply(
        lambda s: _shifted_rolling(s, CONSTRUCTOR_MEDIUM_WINDOW)
    )
    race_level["constructor_dnf_rate_recent_10"] = g["constructor_race_dnf_rate"].apply(
        lambda s: _shifted_rolling(s, CONSTRUCTOR_DNF_WINDOW)
    )
    race_level["constructor_season_points_before_race"] = (
        race_level.groupby(["constructor_id", "season"], group_keys=False)["constructor_race_points"]
        .apply(lambda s: s.shift(1).cumsum())
        .fillna(0.0)
    )
    circuit_group = race_level.groupby(["constructor_id", "circuit_id"], group_keys=False)
    race_level["constructor_circuit_avg_finish"] = circuit_group["constructor_race_avg_finish"].apply(
        _shifted_expanding
    )

    return race_level[
        [
            "season",
            "round",
            "constructor_id",
            "constructor_recent_points_mean_5",
            "constructor_recent_finish_mean_5",
            "constructor_dnf_rate_recent_10",
            "constructor_season_points_before_race",
            "constructor_circuit_avg_finish",
        ]
    ]


def build_feature_table(
    race_results: pd.DataFrame,
    races: pd.DataFrame,
    qualifying_results: pd.DataFrame,
    drivers: pd.DataFrame,
) -> pd.DataFrame:
    """Produce the full leakage-safe feature table, one row per (season, round, driver_id)."""
    races = races.copy()
    races["date"] = pd.to_datetime(races["date"])

    results = race_results.merge(
        races[["season", "round", "date", "circuit_id"]], on=["season", "round"], how="inner"
    )
    results = results.sort_values(["driver_id", "date", "round"]).reset_index(drop=True)

    driver_features = _build_driver_features(results)
    constructor_features = _build_constructor_features(results)

    feature_df = driver_features.merge(
        constructor_features, on=["season", "round", "constructor_id"], how="left"
    )

    # Championship position before this race: rank of season points-so-far
    # among all drivers active this round (1 = leader).
    feature_df["driver_championship_position_before_race"] = feature_df.groupby(["season", "round"])[
        "driver_season_points_before_race"
    ].rank(method="min", ascending=False)

    feature_df["circuit_type"] = feature_df["circuit_id"].apply(get_circuit_type)

    drivers_dob = drivers[["driver_id", "date_of_birth"]].copy()
    drivers_dob["date_of_birth"] = pd.to_datetime(drivers_dob["date_of_birth"])
    feature_df = feature_df.merge(drivers_dob, on="driver_id", how="left")
    feature_df["driver_age_years"] = (feature_df["date"] - feature_df["date_of_birth"]).dt.days / 365.25

    # Post-qualifying-only columns.
    quali = qualifying_results.copy()
    # A driver's grid-determining time is from the *last* session they reached
    # (Q3 for the top 10, Q2 for 11-15, Q1 for 16-20+) — coalesce q3 -> q2 -> q1.
    best_time = quali[["q3_seconds", "q2_seconds", "q1_seconds"]].astype(float).bfill(axis=1).iloc[:, 0]
    quali = quali.assign(best_time_seconds=best_time)
    pole_time = quali.groupby(["season", "round"])["best_time_seconds"].transform("min")
    quali["qualifying_gap_to_pole_seconds"] = quali["best_time_seconds"] - pole_time
    quali = quali.rename(columns={"position": "grid_position"})[
        ["season", "round", "driver_id", "grid_position", "qualifying_gap_to_pole_seconds"]
    ]
    feature_df = feature_df.merge(quali, on=["season", "round", "driver_id"], how="left")

    # grid_position falls back to the actual race-day grid (covers pit-lane
    # starts / grid penalties where qualifying position != starting grid).
    feature_df["grid_position"] = feature_df["grid_position"].astype(float).fillna(feature_df["grid"])

    return feature_df
