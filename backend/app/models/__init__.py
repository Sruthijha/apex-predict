"""Import every ORM model so Base.metadata is fully populated for create_all/Alembic."""

from app.models.features import RaceFeatures
from app.models.ml import ModelPrediction, ModelVersion, SimulationDriverResult, SimulationRun
from app.models.motorsport import Circuit, Constructor, Driver, Race, Season
from app.models.results import QualifyingResult, RaceResult

__all__ = [
    "Season",
    "Circuit",
    "Driver",
    "Constructor",
    "Race",
    "RaceResult",
    "QualifyingResult",
    "RaceFeatures",
    "ModelVersion",
    "ModelPrediction",
    "SimulationRun",
    "SimulationDriverResult",
]
