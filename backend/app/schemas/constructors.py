from pydantic import BaseModel, ConfigDict


class ConstructorSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    nationality: str | None


class ConstructorDetail(ConstructorSummary):
    season_points: float = 0.0
    wins: int = 0
    podiums: int = 0
    dnf_rate: float | None = None
    avg_finish: float | None = None
    avg_qualifying: float | None = None
    drivers: list[str] = []
