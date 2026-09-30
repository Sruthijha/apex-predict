from __future__ import annotations

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    n_simulations: int = Field(default=10_000, ge=100, le=50_000)
    seed: int = 42
    prediction_mode: str = "pre_weekend"


class DriverSimulationOutcome(BaseModel):
    driver_id: str
    driver_name: str
    win_probability: float
    podium_probability: float
    top5_probability: float
    points_probability: float
    dnf_probability: float
    expected_finish_position: float
    expected_points: float


class SimulationResponse(BaseModel):
    race_id: str
    n_simulations: int
    seed: int
    prediction_mode: str
    outcomes: list[DriverSimulationOutcome]  # sorted by win_probability desc
    most_common_podium: list[str]
