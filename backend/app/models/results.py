"""Session results: race classification and qualifying classification."""

from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RaceResult(Base):
    __tablename__ = "race_results"
    __table_args__ = (UniqueConstraint("race_id", "driver_id", name="uq_race_driver"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), index=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("drivers.id"), index=True)
    constructor_id: Mapped[str] = mapped_column(ForeignKey("constructors.id"), index=True)

    grid: Mapped[int] = mapped_column(Integer)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_text: Mapped[str | None] = mapped_column(String(8), nullable=True)
    points: Mapped[float] = mapped_column(Float, default=0.0)
    laps: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(64))
    finished: Mapped[bool] = mapped_column(Boolean, default=False)
    dnf: Mapped[bool] = mapped_column(Boolean, default=False)

    race: Mapped["Race"] = relationship()  # noqa: F821


class QualifyingResult(Base):
    __tablename__ = "qualifying_results"
    __table_args__ = (UniqueConstraint("race_id", "driver_id", name="uq_quali_race_driver"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), index=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("drivers.id"), index=True)
    constructor_id: Mapped[str] = mapped_column(ForeignKey("constructors.id"), index=True)

    position: Mapped[int] = mapped_column(Integer)
    q1_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    q2_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    q3_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    @property
    def best_time_seconds(self) -> float | None:
        for value in (self.q3_seconds, self.q2_seconds, self.q1_seconds):
            if value is not None:
                return value
        return None
