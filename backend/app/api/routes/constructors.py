from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_store
from app.schemas.constructors import ConstructorDetail, ConstructorSummary
from app.services import constructor_service
from app.services.data_store import DataStore

router = APIRouter(prefix="/api/constructors", tags=["constructors"])


@router.get("", response_model=list[ConstructorSummary])
def list_constructors(store: DataStore = Depends(get_store)) -> list[ConstructorSummary]:
    return constructor_service.list_constructors(store)


@router.get("/{constructor_id}", response_model=ConstructorDetail)
def get_constructor(constructor_id: str, store: DataStore = Depends(get_store)) -> ConstructorDetail:
    constructor = constructor_service.get_constructor_detail(store, constructor_id)
    if constructor is None:
        raise HTTPException(status_code=404, detail=f"Constructor '{constructor_id}' not found.")
    return constructor
