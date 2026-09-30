from __future__ import annotations

from pydantic import BaseModel, Field

WEATHER_CONDITIONS = ("dry", "mixed", "wet")


class WhatIfRequest(BaseModel):
    prediction_mode: str = "post_qualifying"
    weather: str = "dry"
    grid_overrides: dict[str, int] = Field(default_factory=dict)
    dnf_overrides: dict[str, float] = Field(default_factory=dict)
    n_simulations: int = Field(default=5000, ge=100, le=20_000)
    seed: int = 42


class WhatIfDriverOutcome(BaseModel):
    driver_id: str
    driver_name: str
    baseline_win_probability: float
    scenario_win_probability: float
    baseline_podium_probability: float
    scenario_podium_probability: float
    baseline_dnf_probability: float
    scenario_dnf_probability: float
    baseline_expected_position: float
    scenario_expected_position: float


class WhatIfResponse(BaseModel):
    race_id: str
    prediction_mode: str
    weather: str
    applied_changes: list[str]
    disclaimer: str
    outcomes: list[WhatIfDriverOutcome]  # sorted by scenario_win_probability desc
