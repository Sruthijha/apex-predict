from pydantic import BaseModel, ConfigDict


class CircuitSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    country: str | None
    locality: str | None
    latitude: float | None
    longitude: float | None


class HistoricalWinner(BaseModel):
    season: int
    driver_id: str
    constructor_id: str


class CircuitDetail(CircuitSummary):
    races_held: int
    dnf_rate: float | None
    historical_winners: list[HistoricalWinner]
