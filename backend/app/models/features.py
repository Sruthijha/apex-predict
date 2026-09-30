"""Materialized, leakage-safe feature table: one row per (race, driver).

Every column here is computed from information available strictly *before*
the target race (see backend/ml/features). Columns prefixed `grid_`/`quali_`
are only known post-qualifying and are therefore null-safe: the pre-weekend
model is trained/served without them.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RaceFeatures(Base):
    __tablename__ = "race_features"
    __table_args__ = (UniqueConstraint("race_id", "driver_id", "feature_version", name="uq_race_driver_featver"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), index=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("drivers.id"), index=True)
    constructor_id: Mapped[str] = mapped_column(ForeignKey("constructors.id"), index=True)
    feature_version: Mapped[str] = mapped_column(String(32), index=True)

    season_year: Mapped[int] = mapped_column(Integer)
    round: Mapped[int] = mapped_column(Integer)
    circuit_id: Mapped[str] = mapped_column(String(64))
    circuit_type: Mapped[str] = mapped_column(String(32))

    # Driver form (pre-weekend safe: all shifted/rolling over prior races only)
    driver_recent_finish_mean_3: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_recent_finish_mean_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_recent_grid_mean_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_recent_points_mean_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_season_points_before_race: Mapped[float] = mapped_column(Float, default=0.0)
    driver_championship_position_before_race: Mapped[int | None] = mapped_column(Integer, nullable=True)
    driver_circuit_avg_finish: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_dnf_rate_recent_10: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_positions_gained_avg_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_recent_form_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_age_years: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Constructor form (pre-weekend safe)
    constructor_recent_points_mean_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    constructor_recent_finish_mean_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    constructor_dnf_rate_recent_10: Mapped[float | None] = mapped_column(Float, nullable=True)
    constructor_season_points_before_race: Mapped[float] = mapped_column(Float, default=0.0)
    constructor_circuit_avg_finish: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Post-qualifying only (null until qualifying happens; excluded from pre-weekend model)
    grid_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    qualifying_gap_to_pole_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    computed_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
