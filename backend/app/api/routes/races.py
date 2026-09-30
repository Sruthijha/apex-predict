from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_store
from app.schemas.races import ActualRaceResult, RaceDetail, RaceSummary
from app.services import race_service
from app.services.data_store import DataStore

router = APIRouter(prefix="/api/races", tags=["races"])


@router.get("", response_model=list[RaceSummary])
def list_races(season: int | None = None, store: DataStore = Depends(get_store)) -> list[RaceSummary]:
    return race_service.list_races(store, season)


@router.get("/upcoming", response_model=RaceSummary)
def upcoming_race(store: DataStore = Depends(get_store)) -> RaceSummary:
    race = race_service.get_upcoming_race(store)
    if race is None:
        raise HTTPException(status_code=404, detail="No upcoming race found in the loaded data.")
    return race


@router.get("/{race_id}", response_model=RaceDetail)
def get_race(race_id: str, store: DataStore = Depends(get_store)) -> RaceDetail:
    race = race_service.get_race(store, race_id)
    if race is None:
        raise HTTPException(status_code=404, detail=f"Race '{race_id}' not found.")
    return race


@router.get("/{race_id}/results", response_model=list[ActualRaceResult])
def get_actual_results(race_id: str, store: DataStore = Depends(get_store)) -> list[ActualRaceResult]:
    results = race_service.get_actual_results(store, race_id)
    if results is None:
        raise HTTPException(status_code=404, detail=f"No results for race '{race_id}' (it may not have happened yet).")
    return results
