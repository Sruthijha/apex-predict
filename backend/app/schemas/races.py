import datetime as dt

from pydantic import BaseModel

from app.schemas.circuits import CircuitSummary


class RaceSummary(BaseModel):
    race_id: str  # "{season}-r{round}-{circuit_id}"
    season: int
    round: int
    name: str
    date: dt.date
    circuit: CircuitSummary
    has_results: bool


class RaceDetail(RaceSummary):
    has_qualifying: bool


class ActualRaceResult(BaseModel):
    driver_id: str
    driver_name: str
    driver_code: str | None
    constructor_id: str
    constructor_name: str
    grid: int
    position: int
    points: float
    status: str
