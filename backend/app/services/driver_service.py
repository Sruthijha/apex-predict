from __future__ import annotations

import pandas as pd

from app.schemas.drivers import DriverDetail, DriverSummary, RecentResult
from app.services.data_store import DataStore

RECENT_RESULTS_LIMIT = 10


def list_drivers(store: DataStore) -> list[DriverSummary]:
    return [
        DriverSummary(
            id=row.driver_id,
            code=row.code,
            permanent_number=None if pd.isna(row.permanent_number) else int(row.permanent_number),
            given_name=row.given_name,
            family_name=row.family_name,
            nationality=row.nationality,
        )
        for row in store.drivers.sort_values("family_name").itertuples()
    ]


def get_driver_detail(store: DataStore, driver_id: str) -> DriverDetail | None:
    driver_rows = store.drivers[store.drivers["driver_id"] == driver_id]
    if driver_rows.empty:
        return None
    driver = driver_rows.iloc[0]

    results = store.race_results[store.race_results["driver_id"] == driver_id].merge(
        store.races[["season", "round", "date", "name", "circuit_id"]], on=["season", "round"]
    )
    results = results.sort_values(["season", "round"])

    current_team = None
    season_points = 0.0
    if not results.empty:
        latest_season = int(results["season"].max())
        current_team = results[results["season"] == latest_season].iloc[-1]["constructor_id"]
        season_points = float(results[results["season"] == latest_season]["points"].sum())

    qualifying = store.qualifying_results[store.qualifying_results["driver_id"] == driver_id]

    return DriverDetail(
        id=driver.driver_id,
        code=driver.code,
        permanent_number=None if pd.isna(driver.permanent_number) else int(driver.permanent_number),
        given_name=driver.given_name,
        family_name=driver.family_name,
        nationality=driver.nationality,
        date_of_birth=None if pd.isna(driver.date_of_birth) else pd.Timestamp(driver.date_of_birth).date(),
        current_team=current_team,
        season_points=season_points,
        wins=int((results["position"] == 1).sum()),
        podiums=int((results["position"] <= 3).sum()),
        dnfs=int(results["dnf"].sum()),
        avg_finish=float(results["position"].mean()) if not results.empty else None,
        avg_qualifying=float(qualifying["position"].mean()) if not qualifying.empty else None,
    )


def get_driver_recent_results(store: DataStore, driver_id: str, limit: int = RECENT_RESULTS_LIMIT) -> list[RecentResult]:
    results = store.race_results[store.race_results["driver_id"] == driver_id].merge(
        store.races[["season", "round", "name", "circuit_id"]], on=["season", "round"]
    )
    results = results.sort_values(["season", "round"], ascending=False).head(limit)
    return [
        RecentResult(
            season=int(r.season),
            round=int(r.round),
            race_name=r.name,
            circuit_id=r.circuit_id,
            grid=int(r.grid),
            position=None if pd.isna(r.position) else int(r.position),
            points=float(r.points),
            status=r.status,
        )
        for r in results.itertuples()
    ]
