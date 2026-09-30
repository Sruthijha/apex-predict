from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_store
from app.schemas.drivers import DriverDetail, DriverSummary, RecentResult
from app.services import driver_service
from app.services.data_store import DataStore

router = APIRouter(prefix="/api/drivers", tags=["drivers"])


@router.get("", response_model=list[DriverSummary])
def list_drivers(store: DataStore = Depends(get_store)) -> list[DriverSummary]:
    return driver_service.list_drivers(store)


@router.get("/{driver_id}", response_model=DriverDetail)
def get_driver(driver_id: str, store: DataStore = Depends(get_store)) -> DriverDetail:
    driver = driver_service.get_driver_detail(store, driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail=f"Driver '{driver_id}' not found.")
    return driver


@router.get("/{driver_id}/results", response_model=list[RecentResult])
def get_driver_results(driver_id: str, store: DataStore = Depends(get_store)) -> list[RecentResult]:
    if driver_service.get_driver_detail(store, driver_id) is None:
        raise HTTPException(status_code=404, detail=f"Driver '{driver_id}' not found.")
    return driver_service.get_driver_recent_results(store, driver_id)
