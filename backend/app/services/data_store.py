"""In-process cache of the processed parquet tables (the ML pipeline's data
warehouse). Loaded once per process; the relational DB holds the same
reference data for the CRUD-style read endpoints, while this cache feeds the
prediction/simulation services (which need full DataFrames, not ORM rows, to
call directly into the ml/ package's feature-engineering and inference code).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class DataStore:
    races: pd.DataFrame
    circuits: pd.DataFrame
    drivers: pd.DataFrame
    constructors: pd.DataFrame
    race_results: pd.DataFrame
    qualifying_results: pd.DataFrame

    def race_slug(self, season: int, circuit_id: str) -> str:
        return f"{season}-{circuit_id}"

    def find_race(self, race_id: str) -> pd.Series | None:
        try:
            season_str, circuit_id = race_id.split("-", 1)
            season = int(season_str)
        except ValueError:
            return None
        matches = self.races[(self.races["season"] == season) & (self.races["circuit_id"] == circuit_id)]
        return matches.iloc[0] if not matches.empty else None

    def latest_lineup(self, before_season: int, before_round: int) -> pd.DataFrame:
        """The most recent race's driver/constructor pairings strictly before
        the given (season, round) — used as the assumed entry list for a race
        that hasn't happened yet, since Ergast/Jolpica doesn't expose a
        separate pre-race entry list endpoint."""
        prior = self.race_results.merge(self.races[["season", "round", "date"]], on=["season", "round"])
        prior = prior[
            (prior["season"] < before_season)
            | ((prior["season"] == before_season) & (prior["round"] < before_round))
        ]
        if prior.empty:
            return prior
        last_key = prior.sort_values(["season", "round"]).iloc[-1][["season", "round"]]
        return prior[(prior["season"] == last_key["season"]) & (prior["round"] == last_key["round"])][
            ["driver_id", "constructor_id"]
        ].drop_duplicates()


@lru_cache
def get_data_store(processed_dir: str) -> DataStore:
    base = Path(processed_dir)
    return DataStore(
        races=pd.read_parquet(base / "races.parquet"),
        circuits=pd.read_parquet(base / "circuits.parquet"),
        drivers=pd.read_parquet(base / "drivers.parquet"),
        constructors=pd.read_parquet(base / "constructors.parquet"),
        race_results=pd.read_parquet(base / "race_results.parquet"),
        qualifying_results=pd.read_parquet(base / "qualifying_results.parquet"),
    )
