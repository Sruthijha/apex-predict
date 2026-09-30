from __future__ import annotations

from app.schemas.constructors import ConstructorDetail, ConstructorSummary
from app.services.data_store import DataStore


def list_constructors(store: DataStore) -> list[ConstructorSummary]:
    return [
        ConstructorSummary(id=row.constructor_id, name=row.name, nationality=row.nationality)
        for row in store.constructors.sort_values("name").itertuples()
    ]


def get_constructor_detail(store: DataStore, constructor_id: str) -> ConstructorDetail | None:
    rows = store.constructors[store.constructors["constructor_id"] == constructor_id]
    if rows.empty:
        return None
    constructor = rows.iloc[0]

    results = store.race_results[store.race_results["constructor_id"] == constructor_id]
    season_points = 0.0
    if not results.empty:
        latest_season = int(results["season"].max())
        season_points = float(results[results["season"] == latest_season]["points"].sum())

    qualifying = store.qualifying_results[store.qualifying_results["constructor_id"] == constructor_id]
    driver_ids = sorted(results["driver_id"].unique().tolist()) if not results.empty else []

    return ConstructorDetail(
        id=constructor["constructor_id"],
        name=constructor["name"],
        nationality=constructor["nationality"],
        season_points=season_points,
        wins=int((results["position"] == 1).sum()),
        podiums=int((results["position"] <= 3).sum()),
        dnf_rate=float(results["dnf"].mean()) if not results.empty else None,
        avg_finish=float(results["position"].mean()) if not results.empty else None,
        avg_qualifying=float(qualifying["position"].mean()) if not qualifying.empty else None,
        drivers=driver_ids,
    )
