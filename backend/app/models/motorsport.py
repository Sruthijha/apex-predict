"""Core reference entities: seasons, circuits, races, drivers, constructors."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Season(Base):
    __tablename__ = "seasons"

    year: Mapped[int] = mapped_column(Integer, primary_key=True)

    races: Mapped[list["Race"]] = relationship(back_populates="season")


class Circuit(Base):
    __tablename__ = "circuits"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    country: Mapped[str | None] = mapped_column(String(128), nullable=True)
    locality: Mapped[str | None] = mapped_column(String(128), nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    races: Mapped[list["Race"]] = relationship(back_populates="circuit")


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    code: Mapped[str | None] = mapped_column(String(8), nullable=True, index=True)
    permanent_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    given_name: Mapped[str] = mapped_column(String(128))
    family_name: Mapped[str] = mapped_column(String(128))
    nationality: Mapped[str | None] = mapped_column(String(128), nullable=True)
    date_of_birth: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    @property
    def full_name(self) -> str:
        return f"{self.given_name} {self.family_name}"


class Constructor(Base):
    __tablename__ = "constructors"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    nationality: Mapped[str | None] = mapped_column(String(128), nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)


class Race(Base):
    __tablename__ = "races"
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_year: Mapped[int] = mapped_column(ForeignKey("seasons.year"), index=True)
    round: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    circuit_id: Mapped[str] = mapped_column(ForeignKey("circuits.id"), index=True)
    date: Mapped[dt.date] = mapped_column(Date, index=True)
    time: Mapped[dt.time | None] = mapped_column(Time, nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    season: Mapped[Season] = relationship(back_populates="races")
    circuit: Mapped[Circuit] = relationship(back_populates="races")
