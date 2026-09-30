import datetime as dt

from pydantic import BaseModel

from app.schemas.circuits import CircuitSummary


class RaceSummary(BaseModel):
    race_id: str  # "{season}-{circuit_id}"
    season: int
    round: int
    name: str
    date: dt.date
    circuit: CircuitSummary
    has_results: bool


class RaceDetail(RaceSummary):
    has_qualifying: bool
