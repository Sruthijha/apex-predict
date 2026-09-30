from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_store
from app.schemas.circuits import CircuitDetail, CircuitSummary
from app.services import circuit_service
from app.services.data_store import DataStore

router = APIRouter(prefix="/api/circuits", tags=["circuits"])


@router.get("", response_model=list[CircuitSummary])
def list_circuits(store: DataStore = Depends(get_store)) -> list[CircuitSummary]:
    return circuit_service.list_circuits(store)


@router.get("/{circuit_id}", response_model=CircuitDetail)
def get_circuit(circuit_id: str, store: DataStore = Depends(get_store)) -> CircuitDetail:
    circuit = circuit_service.get_circuit_detail(store, circuit_id)
    if circuit is None:
        raise HTTPException(status_code=404, detail=f"Circuit '{circuit_id}' not found.")
    return circuit
