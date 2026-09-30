from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_model_dir, get_store
from app.schemas.championship import ChampionshipProjectionResponse
from app.services import championship_service
from app.services.data_store import DataStore

router = APIRouter(prefix="/api/championship", tags=["championship"])


@router.get("", response_model=ChampionshipProjectionResponse)
def get_championship(
    n_trials: int = Query(default=5000, ge=100, le=20_000),
    seed: int = 42,
    store: DataStore = Depends(get_store),
    model_dir: str = Depends(get_model_dir),
) -> ChampionshipProjectionResponse:
    result = championship_service.get_championship_projection(store, model_dir, n_trials, seed)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No championship projection available (season may be complete, or no upcoming race data found).",
        )
    return result
