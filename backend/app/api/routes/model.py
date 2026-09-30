from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_model_dir
from app.schemas.model import ModelMetricsResponse
from app.services import model_metrics_service

router = APIRouter(prefix="/api/model", tags=["model"])


@router.get("/metrics", response_model=ModelMetricsResponse)
def get_model_metrics(model_dir: str = Depends(get_model_dir)) -> ModelMetricsResponse:
    return model_metrics_service.get_model_metrics(model_dir)
