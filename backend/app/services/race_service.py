from __future__ import annotations

import pandas as pd

from app.schemas.circuits import CircuitSummary
from app.schemas.races import RaceDetail, RaceSummary
from app.services.data_store import DataStore


def _races_with_results(store: DataStore) -> set[tuple[int, int]]:
    return set(map(tuple, store.race_results[["season", "round"]].drop_duplicates().to_numpy().tolist()))


def _races_with_qualifying(store: DataStore) -> set[tuple[int, int]]:
    return set(map(tuple, store.qualifying_results[["season", "round"]].drop_duplicates().to_numpy().tolist()))


def _to_summary(store: DataStore, row: pd.Series, results_keys: set[tuple[int, int]]) -> RaceSummary:
    circuit = store.circuits[store.circuits["circuit_id"] == row["circuit_id"]].iloc[0]
    return RaceSummary(
        race_id=store.race_slug(int(row["season"]), row["circuit_id"]),
        season=int(row["season"]),
        round=int(row["round"]),
        name=row["name"],
        date=row["date"],
        circuit=CircuitSummary(
            id=circuit["circuit_id"],
            name=circuit["circuit_name"],
            country=circuit["circuit_country"],
            locality=circuit["circuit_locality"],
            latitude=circuit["circuit_lat"],
            longitude=circuit["circuit_long"],
        ),
        has_results=(int(row["season"]), int(row["round"])) in results_keys,
    )


def list_races(store: DataStore, season: int | None = None) -> list[RaceSummary]:
    results_keys = _races_with_results(store)
    races = store.races if season is None else store.races[store.races["season"] == season]
    races = races.sort_values(["season", "round"])
    return [_to_summary(store, row, results_keys) for _, row in races.iterrows()]


def get_upcoming_race(store: DataStore) -> RaceSummary | None:
    results_keys = _races_with_results(store)
    upcoming = store.races[~store.races.apply(lambda r: (int(r["season"]), int(r["round"])) in results_keys, axis=1)]
    if upcoming.empty:
        return None
    upcoming = upcoming.sort_values(["season", "round"])
    return _to_summary(store, upcoming.iloc[0], results_keys)


def get_race(store: DataStore, race_id: str) -> RaceDetail | None:
    row = store.find_race(race_id)
    if row is None:
        return None
    results_keys = _races_with_results(store)
    qualifying_keys = _races_with_qualifying(store)
    summary = _to_summary(store, row, results_keys)
    return RaceDetail(
        **summary.model_dump(),
        has_qualifying=(int(row["season"]), int(row["round"])) in qualifying_keys,
    )
