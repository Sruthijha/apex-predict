"""Model versioning, stored predictions, and simulation results."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ModelVersion(Base):
    """Metadata for one trained model artifact, so every prediction can be traced
    back to exactly how it was produced (algorithm, training window, metrics)."""

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    prediction_mode: Mapped[str] = mapped_column(String(32))  # pre_weekend | post_qualifying
    algorithm: Mapped[str] = mapped_column(String(64))
    feature_version: Mapped[str] = mapped_column(String(32))
    train_seasons: Mapped[str] = mapped_column(String(64))  # e.g. "2018-2022"
    validation_season: Mapped[int] = mapped_column(Integer)
    test_season: Mapped[int] = mapped_column(Integer)
    metrics: Mapped[dict] = mapped_column(JSON)
    trained_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=True)


class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    __table_args__ = (
        UniqueConstraint("race_id", "driver_id", "model_version_id", "prediction_mode", name="uq_prediction"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), index=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("drivers.id"), index=True)
    model_version_id: Mapped[int] = mapped_column(ForeignKey("model_versions.id"), index=True)
    prediction_mode: Mapped[str] = mapped_column(String(32))

    predicted_position: Mapped[float] = mapped_column(Float)
    win_probability: Mapped[float] = mapped_column(Float)
    podium_probability: Mapped[float] = mapped_column(Float)
    top5_probability: Mapped[float] = mapped_column(Float)
    points_probability: Mapped[float] = mapped_column(Float)
    dnf_probability: Mapped[float] = mapped_column(Float)
    expected_points: Mapped[float] = mapped_column(Float)
    confidence: Mapped[str] = mapped_column(String(16))  # LOW | MEDIUM | HIGH
    explanation: Mapped[dict] = mapped_column(JSON)  # {"positive": [...], "risk": [...]}
    generated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), index=True)
    model_version_id: Mapped[int] = mapped_column(ForeignKey("model_versions.id"), index=True)
    prediction_mode: Mapped[str] = mapped_column(String(32))
    n_simulations: Mapped[int] = mapped_column(Integer)
    seed: Mapped[int] = mapped_column(Integer)
    most_common_podium: Mapped[list] = mapped_column(JSON)  # ordered list of driver_id
    generated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class SimulationDriverResult(Base):
    __tablename__ = "simulation_driver_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    simulation_run_id: Mapped[int] = mapped_column(ForeignKey("simulation_runs.id"), index=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("drivers.id"), index=True)

    win_probability: Mapped[float] = mapped_column(Float)
    podium_probability: Mapped[float] = mapped_column(Float)
    top5_probability: Mapped[float] = mapped_column(Float)
    points_probability: Mapped[float] = mapped_column(Float)
    dnf_probability: Mapped[float] = mapped_column(Float)
    expected_finish_position: Mapped[float] = mapped_column(Float)
