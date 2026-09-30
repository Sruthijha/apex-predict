from __future__ import annotations

import datetime as dt

from pydantic import BaseModel


class DriverExplanation(BaseModel):
    positive: list[str]
    risk: list[str]


class DriverPrediction(BaseModel):
    driver_id: str
    driver_name: str
    driver_code: str | None
    constructor_id: str
    constructor_name: str
    predicted_position: float
    win_probability: float
    podium_probability: float
    top5_probability: float
    points_probability: float
    dnf_probability: float
    expected_points: float
    confidence: str
    explanation: DriverExplanation


class RacePrediction(BaseModel):
    race_id: str
    season: int
    round: int
    prediction_mode: str
    model_version: str
    generated_at: dt.datetime
    drivers: list[DriverPrediction]  # sorted by predicted_position
    used_cached_data: bool = False
