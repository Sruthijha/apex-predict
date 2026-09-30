"""Apex Predict API — FastAPI entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import circuits, constructors, drivers, model, predictions, races, simulation
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Apex Predict API",
    description="Formula 1 race intelligence: leakage-safe ML predictions and Monte Carlo simulation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(races.router)
app.include_router(drivers.router)
app.include_router(constructors.router)
app.include_router(circuits.router)
app.include_router(predictions.router)
app.include_router(simulation.router)
app.include_router(model.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
