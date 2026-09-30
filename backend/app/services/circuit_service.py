from __future__ import annotations

from app.schemas.circuits import CircuitDetail, CircuitSummary, HistoricalWinner
from app.services.data_store import DataStore


def _to_summary(row) -> CircuitSummary:
    return CircuitSummary(
        id=row.circuit_id,
        name=row.circuit_name,
        country=row.circuit_country,
        locality=row.circuit_locality,
        latitude=row.circuit_lat,
        longitude=row.circuit_long,
    )


def list_circuits(store: DataStore) -> list[CircuitSummary]:
    return [_to_summary(row) for row in store.circuits.sort_values("circuit_name").itertuples()]


def get_circuit_detail(store: DataStore, circuit_id: str) -> CircuitDetail | None:
    rows = store.circuits[store.circuits["circuit_id"] == circuit_id]
    if rows.empty:
        return None
    circuit = rows.iloc[0]

    races_at_circuit = store.races[store.races["circuit_id"] == circuit_id]
    results = store.race_results.merge(races_at_circuit[["season", "round"]], on=["season", "round"])

    winners_df = results[results["position"] == 1].merge(
        races_at_circuit[["season", "round"]], on=["season", "round"]
    ).sort_values("season", ascending=False)
    winners = [
        HistoricalWinner(season=int(r.season), driver_id=r.driver_id, constructor_id=r.constructor_id)
        for r in winners_df.itertuples()
    ]

    return CircuitDetail(
        **_to_summary(circuit).model_dump(),
        races_held=len(races_at_circuit),
        dnf_rate=float(results["dnf"].mean()) if not results.empty else None,
        historical_winners=winners,
    )
