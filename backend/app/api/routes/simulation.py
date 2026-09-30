from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_model_dir, get_store
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.services import simulation_service
from app.services.data_store import DataStore

router = APIRouter(prefix="/api/simulate", tags=["simulation"])


@router.post("/{race_id}", response_model=SimulationResponse)
def simulate(
    race_id: str,
    request: SimulationRequest,
    db: Session = Depends(get_db),
    store: DataStore = Depends(get_store),
    model_dir: str = Depends(get_model_dir),
) -> SimulationResponse:
    result = simulation_service.run_race_simulation(
        db, store, model_dir, race_id, request.prediction_mode, request.n_simulations, request.seed
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Could not simulate race '{race_id}' in this mode.")
    return result
