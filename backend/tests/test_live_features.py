"""Regression test for a real bug: `historical_races` is normally the full
season schedule, which already has a placeholder (no-results) row for a
future race. Naively appending another row for that same race silently fans
out every merge in build_feature_table (22 drivers -> 88 rows, 4x)."""

from __future__ import annotations

import pandas as pd

from ml.inference.live_features import DriverEntry, build_live_feature_rows


def test_live_feature_rows_one_per_driver_even_when_schedule_already_lists_the_race():
    races = pd.DataFrame(
        [
            {"season": 2030, "round": 1, "date": "2030-01-01", "circuit_id": "circuit_a"},
            # Schedule already lists round 2 (future race, no results yet) -
            # this is the realistic shape of a full season schedule table.
            {"season": 2030, "round": 2, "date": "2030-01-08", "circuit_id": "circuit_b"},
        ]
    )
    results = pd.DataFrame(
        [
            {
                "season": 2030, "round": 1, "driver_id": "d1", "constructor_id": "c1",
                "grid": 1, "position": 1, "points": 25.0, "laps": 50,
                "status": "Finished", "finished": True, "dnf": False,
            },
            {
                "season": 2030, "round": 1, "driver_id": "d2", "constructor_id": "c1",
                "grid": 2, "position": 2, "points": 18.0, "laps": 50,
                "status": "Finished", "finished": True, "dnf": False,
            },
        ]
    )
    qualifying = pd.DataFrame(columns=["season", "round", "driver_id", "constructor_id", "position", "q1_seconds", "q2_seconds", "q3_seconds"])
    drivers = pd.DataFrame(
        [
            {"driver_id": "d1", "date_of_birth": "1995-01-01"},
            {"driver_id": "d2", "date_of_birth": "1998-01-01"},
        ]
    )
    lineup = [DriverEntry(driver_id="d1", constructor_id="c1"), DriverEntry(driver_id="d2", constructor_id="c1")]

    feature_rows = build_live_feature_rows(
        results, races, qualifying, drivers, season=2030, round_=2, date="2030-01-08", circuit_id="circuit_b", lineup=lineup
    )

    assert len(feature_rows) == 2
    assert set(feature_rows["driver_id"]) == {"d1", "d2"}
