import datetime as dt

from pydantic import BaseModel, ConfigDict


class DriverSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str | None
    permanent_number: int | None
    given_name: str
    family_name: str
    nationality: str | None


class DriverDetail(DriverSummary):
    date_of_birth: dt.date | None
    current_team: str | None = None
    season_points: float = 0.0
    wins: int = 0
    podiums: int = 0
    dnfs: int = 0
    avg_finish: float | None = None
    avg_qualifying: float | None = None


class RecentResult(BaseModel):
    season: int
    round: int
    race_name: str
    circuit_id: str
    grid: int
    position: int | None
    points: float
    status: str
