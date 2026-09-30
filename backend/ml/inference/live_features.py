"""Build a feature row for a race that hasn't happened yet (or hasn't
finished yet), by reusing the exact same leakage-safe feature builder used
for training.

The trick: a "future race" is appended to the historical races/results
tables as a placeholder (known lineup, unknown outcome). Because every
feature in ml/features/build_features.py is computed via `shift(1)` before
any rolling/expanding aggregation, the placeholder's own (nonexistent)
result never contributes to its own feature row — its features are built
purely from the real history that precedes it. This guarantees training/
serving parity: there is no second, hand-rolled "live feature" code path
that could silently drift from the training-time logic.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ml.features.build_features import build_feature_table


@dataclass
class DriverEntry:
    driver_id: str
    constructor_id: str
    grid_position: int | None = None  # known only once qualifying has happened


def build_live_feature_rows(
    historical_results: pd.DataFrame,
    historical_races: pd.DataFrame,
    historical_qualifying: pd.DataFrame,
    drivers: pd.DataFrame,
    season: int,
    round_: int,
    date: str,
    circuit_id: str,
    lineup: list[DriverEntry],
) -> pd.DataFrame:
    target_race = pd.DataFrame(
        [{"season": season, "round": round_, "name": "", "date": date, "time": None, "url": None, "circuit_id": circuit_id}]
    )
    # `historical_races` is typically the full season schedule, which already
    # has a (season, round) row for a future/in-progress race (with no
    # results yet). Replace it rather than appending, or the duplicate key
    # fans out through every merge in build_feature_table.
    other_races = historical_races[~((historical_races["season"] == season) & (historical_races["round"] == round_))]
    races = pd.concat([other_races, target_race], ignore_index=True)

    placeholder_results = pd.DataFrame(
        [
            {
                "season": season,
                "round": round_,
                "driver_id": entry.driver_id,
                "constructor_id": entry.constructor_id,
                "grid": entry.grid_position if entry.grid_position is not None else 0,
                "position_text": None,
                "position": None,
                "points": 0.0,
                "laps": 0,
                "status": "Unknown",
                "finished": False,
                "dnf": False,
            }
            for entry in lineup
        ]
    )
    results = pd.concat([historical_results, placeholder_results], ignore_index=True)

    qualifying = historical_qualifying
    known_grid_entries = [e for e in lineup if e.grid_position is not None]
    if known_grid_entries:
        placeholder_quali = pd.DataFrame(
            [
                {
                    "season": season,
                    "round": round_,
                    "driver_id": e.driver_id,
                    "constructor_id": e.constructor_id,
                    "position": e.grid_position,
                    "q1_seconds": None,
                    "q2_seconds": None,
                    "q3_seconds": None,
                }
                for e in known_grid_entries
            ]
        )
        qualifying = pd.concat([historical_qualifying, placeholder_quali], ignore_index=True)

    feature_table = build_feature_table(results, races, qualifying, drivers)
    return feature_table[(feature_table["season"] == season) & (feature_table["round"] == round_)].reset_index(
        drop=True
    )
