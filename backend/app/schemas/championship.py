from __future__ import annotations

from pydantic import BaseModel


class DriverChampionshipProjection(BaseModel):
    driver_id: str
    driver_name: str
    constructor_id: str
    current_points: float
    expected_final_points: float
    championship_win_probability: float
    top3_championship_probability: float


class ConstructorChampionshipProjection(BaseModel):
    constructor_id: str
    constructor_name: str
    current_points: float
    expected_final_points: float
    championship_win_probability: float
    top3_championship_probability: float


class ChampionshipProjectionResponse(BaseModel):
    season: int
    last_completed_round: int
    remaining_races: int
    n_trials: int
    seed: int
    assumption: str
    drivers: list[DriverChampionshipProjection]
    constructors: list[ConstructorChampionshipProjection]
