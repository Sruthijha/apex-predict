from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_model_dir, get_store
from app.schemas.predictions import RacePrediction
from app.services import prediction_service
from app.services.data_store import DataStore

router = APIRouter(prefix="/api/predictions", tags=["predictions"])
VALID_MODES = {"pre_weekend", "post_qualifying"}


@router.get("/{race_id}", response_model=RacePrediction)
def get_prediction(
    race_id: str,
    mode: str = Query(default="pre_weekend"),
    db: Session = Depends(get_db),
    store: DataStore = Depends(get_store),
    model_dir: str = Depends(get_model_dir),
) -> RacePrediction:
    if mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail=f"mode must be one of {sorted(VALID_MODES)}")

    prediction = prediction_service.build_race_prediction(db, store, model_dir, race_id, mode)
    if prediction is None:
        detail = (
            f"No prediction available for race '{race_id}' in mode '{mode}'. "
            "If mode is 'post_qualifying', qualifying may not have happened yet - try 'pre_weekend'."
        )
        raise HTTPException(status_code=404, detail=detail)
    return prediction
