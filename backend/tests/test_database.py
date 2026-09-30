"""Database operation tests: schema creation, constraints, relationships.
Uses a throwaway in-memory SQLite engine, independent of the app's
configured DATABASE_URL, so these tests never touch real data.
"""

from __future__ import annotations

import datetime as dt

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models  # noqa: F401 (registers all tables on Base.metadata)
from app.db.base import Base
from app.models.motorsport import Circuit, Constructor, Driver, Race, Season
from app.models.results import RaceResult


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _seed_minimal(session: Session) -> Race:
    session.add(Season(year=2024))
    session.add(Circuit(id="monza", name="Autodromo Nazionale di Monza", country="Italy"))
    session.add(Driver(id="d1", given_name="Test", family_name="Driver"))
    session.add(Constructor(id="c1", name="Test Team"))
    session.commit()

    race = Race(season_year=2024, round=1, name="Test Grand Prix", circuit_id="monza", date=dt.date(2024, 3, 1))
    session.add(race)
    session.commit()
    return race


def test_schema_creates_all_expected_tables(db_session: Session):
    table_names = set(Base.metadata.tables.keys())
    assert {
        "seasons", "circuits", "drivers", "constructors", "races",
        "race_results", "qualifying_results", "race_features",
        "model_versions", "model_predictions", "simulation_runs", "simulation_driver_results",
    }.issubset(table_names)


def test_insert_and_query_race_with_relationships(db_session: Session):
    _seed_minimal(db_session)

    fetched = db_session.query(Race).filter_by(season_year=2024, round=1).one()
    assert fetched.name == "Test Grand Prix"
    assert fetched.circuit.name == "Autodromo Nazionale di Monza"
    assert fetched.season.year == 2024


def test_race_result_unique_constraint_prevents_duplicate_driver_entries(db_session: Session):
    race = _seed_minimal(db_session)
    db_session.add(
        RaceResult(
            race_id=race.id, driver_id="d1", constructor_id="c1",
            grid=1, position=1, points=25.0, laps=50, status="Finished", finished=True, dnf=False,
        )
    )
    db_session.commit()

    db_session.add(
        RaceResult(
            race_id=race.id, driver_id="d1", constructor_id="c1",
            grid=2, position=2, points=18.0, laps=50, status="Finished", finished=True, dnf=False,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_race_result_cascade_free_delete_of_unrelated_race_is_safe(db_session: Session):
    """Deleting a race with no results shouldn't raise (sanity check that
    there's no unexpected FK constraint blocking normal operations)."""
    race = _seed_minimal(db_session)
    db_session.delete(race)
    db_session.commit()
    assert db_session.query(Race).count() == 0
