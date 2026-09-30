"""Pins down the single most important correctness property of this project:
a feature row for race N must never be influenced by anything that happened
in race N itself (or later). See ml/features/build_features.py.
"""

from __future__ import annotations

import pandas as pd
import pytest

from ml.features.build_features import build_feature_table
from ml.features.feature_columns import POST_QUALIFYING_ONLY_FEATURES, PRE_WEEKEND_FEATURES


def _toy_dataset() -> dict[str, pd.DataFrame]:
    """Two drivers, one constructor each, four races, hand-computable stats."""
    races = pd.DataFrame(
        [
            {"season": 2020, "round": 1, "date": "2020-01-01", "circuit_id": "circuit_a"},
            {"season": 2020, "round": 2, "date": "2020-01-08", "circuit_id": "circuit_b"},
            {"season": 2020, "round": 3, "date": "2020-01-15", "circuit_id": "circuit_a"},
            {"season": 2020, "round": 4, "date": "2020-01-22", "circuit_id": "circuit_b"},
        ]
    )
    results = pd.DataFrame(
        [
            {"season": 2020, "round": 1, "driver_id": "d1", "constructor_id": "c1", "grid": 1, "position": 1, "points": 25.0, "laps": 50, "status": "Finished", "finished": True, "dnf": False},
            {"season": 2020, "round": 1, "driver_id": "d2", "constructor_id": "c2", "grid": 2, "position": 2, "points": 18.0, "laps": 50, "status": "Finished", "finished": True, "dnf": False},
            {"season": 2020, "round": 2, "driver_id": "d1", "constructor_id": "c1", "grid": 3, "position": 5, "points": 10.0, "laps": 50, "status": "Finished", "finished": True, "dnf": False},
            {"season": 2020, "round": 2, "driver_id": "d2", "constructor_id": "c2", "grid": 1, "position": 1, "points": 25.0, "laps": 50, "status": "Finished", "finished": True, "dnf": False},
            {"season": 2020, "round": 3, "driver_id": "d1", "constructor_id": "c1", "grid": 2, "position": None, "points": 0.0, "laps": 10, "status": "Engine", "finished": False, "dnf": True},
            {"season": 2020, "round": 3, "driver_id": "d2", "constructor_id": "c2", "grid": 3, "position": 3, "points": 15.0, "laps": 50, "status": "Finished", "finished": True, "dnf": False},
            {"season": 2020, "round": 4, "driver_id": "d1", "constructor_id": "c1", "grid": 4, "position": 4, "points": 12.0, "laps": 50, "status": "Finished", "finished": True, "dnf": False},
            {"season": 2020, "round": 4, "driver_id": "d2", "constructor_id": "c2", "grid": 2, "position": 2, "points": 18.0, "laps": 50, "status": "Finished", "finished": True, "dnf": False},
        ]
    )
    qualifying = pd.DataFrame(
        [
            {"season": s, "round": r, "driver_id": d, "position": 1, "q1_seconds": 90.0, "q2_seconds": None, "q3_seconds": None}
            for s in [2020]
            for r in [1, 2, 3, 4]
            for d in ["d1", "d2"]
        ]
    )
    drivers = pd.DataFrame(
        [
            {"driver_id": "d1", "date_of_birth": "1995-01-01"},
            {"driver_id": "d2", "date_of_birth": "1998-01-01"},
        ]
    )
    return {"races": races, "results": results, "qualifying": qualifying, "drivers": drivers}


def _features_for(driver_id: str, round_: int, feats: pd.DataFrame) -> pd.Series:
    row = feats[(feats["driver_id"] == driver_id) & (feats["round"] == round_)]
    assert len(row) == 1
    return row.iloc[0]


def test_first_race_has_no_prior_history():
    data = _toy_dataset()
    feats = build_feature_table(data["results"], data["races"], data["qualifying"], data["drivers"])

    round1_d1 = _features_for("d1", 1, feats)
    assert pd.isna(round1_d1.driver_recent_finish_mean_3)
    assert pd.isna(round1_d1.driver_recent_finish_mean_5)
    assert pd.isna(round1_d1.driver_circuit_avg_finish)
    assert round1_d1.driver_season_points_before_race == 0.0


def test_rolling_stat_uses_only_prior_races():
    data = _toy_dataset()
    feats = build_feature_table(data["results"], data["races"], data["qualifying"], data["drivers"])

    # d1 finished P1 (round1), P5 (round2), DNF (round3). Round 4's rolling
    # mean-of-3 must equal mean(1, 5) skipping the DNF's null position —
    # never including round 4's own result.
    round4_d1 = _features_for("d1", 4, feats)
    assert round4_d1.driver_recent_finish_mean_3 == pytest.approx((1 + 5) / 2)

    # Season points before round 3 for d1 = sum of rounds 1-2 only (25 + 10),
    # excluding round 3's own (irrelevant, DNF=0 anyway) or later points.
    round3_d1 = _features_for("d1", 3, feats)
    assert round3_d1.driver_season_points_before_race == 25.0 + 10.0


def test_mutating_a_races_own_outcome_does_not_change_its_own_features():
    """The defining leakage check: if race N's result changes, every feature
    row for race N itself must be byte-for-byte identical (those features are
    built entirely from races < N) — only race N+1's features may move."""
    data = _toy_dataset()
    baseline = build_feature_table(data["results"], data["races"], data["qualifying"], data["drivers"])

    mutated_results = data["results"].copy()
    mask = (
        (mutated_results["season"] == 2020)
        & (mutated_results["round"] == 3)
        & (mutated_results["driver_id"] == "d2")
    )
    mutated_results.loc[mask, "position"] = 1
    mutated_results.loc[mask, "points"] = 25.0
    mutated = build_feature_table(mutated_results, data["races"], data["qualifying"], data["drivers"])

    feature_cols = [c for c in PRE_WEEKEND_FEATURES if c != "circuit_type"]

    round3_before = _features_for("d2", 3, baseline)[feature_cols]
    round3_after = _features_for("d2", 3, mutated)[feature_cols]
    pd.testing.assert_series_equal(round3_before, round3_after, check_names=False)

    # But round 4 (which now sees d2's improved round-3 result in its rolling
    # window) must have changed.
    round4_before = _features_for("d2", 4, baseline)[feature_cols]
    round4_after = _features_for("d2", 4, mutated)[feature_cols]
    assert not round4_before.equals(round4_after)


def test_pre_weekend_features_exclude_post_qualifying_information():
    """The pre-weekend feature set must not be able to see grid position or
    qualifying pace — those aren't known until qualifying has happened."""
    for leaking_col in POST_QUALIFYING_ONLY_FEATURES:
        assert leaking_col not in PRE_WEEKEND_FEATURES


def test_championship_position_ranks_by_points_before_race():
    data = _toy_dataset()
    feats = build_feature_table(data["results"], data["races"], data["qualifying"], data["drivers"])

    # Before round 3, d1 has 35 pts (25+10), d2 has 43 pts (18+25) -> d2 leads.
    round3_d1 = _features_for("d1", 3, feats)
    round3_d2 = _features_for("d2", 3, feats)
    assert round3_d2.driver_championship_position_before_race < round3_d1.driver_championship_position_before_race
