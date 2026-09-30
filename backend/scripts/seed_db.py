"""Seeds the relational database (seasons, circuits, drivers, constructors,
races, race_results, qualifying_results) from the processed parquet tables.

Reference/historical data is served from the DB (proper relational queries,
joins, indexes); the ML pipeline reads the same underlying data from parquet
directly, since that's its natural pipeline artifact. Generated predictions
and simulation runs are written back into the DB by the API at request time
(see app/services), each tagged with the model version that produced them.
"""

from __future__ import annotations

import argparse
import logging

import pandas as pd
from sqlalchemy.orm import Session

import app.models  # noqa: F401 (registers all tables on Base.metadata)
from app.db.session import SessionLocal
from app.models.motorsport import Circuit, Constructor, Driver, Race, Season
from app.models.results import QualifyingResult, RaceResult

logger = logging.getLogger(__name__)


def _load(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)


def seed(data_dir: str) -> None:
    """Assumes `alembic upgrade head` has already created the schema."""
    races_df = _load(f"{data_dir}/races.parquet")
    circuits_df = _load(f"{data_dir}/circuits.parquet")
    drivers_df = _load(f"{data_dir}/drivers.parquet")
    constructors_df = _load(f"{data_dir}/constructors.parquet")
    results_df = _load(f"{data_dir}/race_results.parquet")
    qualifying_df = _load(f"{data_dir}/qualifying_results.parquet")

    db: Session = SessionLocal()
    try:
        db.query(QualifyingResult).delete()
        db.query(RaceResult).delete()
        db.query(Race).delete()
        db.query(Driver).delete()
        db.query(Constructor).delete()
        db.query(Circuit).delete()
        db.query(Season).delete()
        db.commit()

        db.add_all([Season(year=int(y)) for y in races_df["season"].unique()])
        db.add_all(
            Circuit(
                id=row.circuit_id,
                name=row.circuit_name,
                country=row.circuit_country,
                locality=row.circuit_locality,
                latitude=row.circuit_lat,
                longitude=row.circuit_long,
                url=row.circuit_url,
            )
            for row in circuits_df.itertuples()
        )
        db.add_all(
            Driver(
                id=row.driver_id,
                code=row.code,
                permanent_number=None if pd.isna(row.permanent_number) else int(row.permanent_number),
                given_name=row.given_name,
                family_name=row.family_name,
                nationality=row.nationality,
                date_of_birth=None if pd.isna(row.date_of_birth) else pd.Timestamp(row.date_of_birth).date(),
                url=row.url,
            )
            for row in drivers_df.itertuples()
        )
        db.add_all(
            Constructor(id=row.constructor_id, name=row.name, nationality=row.nationality, url=row.url)
            for row in constructors_df.itertuples()
        )
        db.commit()

        race_id_by_season_round: dict[tuple[int, int], int] = {}
        for row in races_df.itertuples():
            race = Race(
                season_year=int(row.season),
                round=int(row.round),
                name=row.name,
                circuit_id=row.circuit_id,
                date=pd.Timestamp(row.date).date(),
                time=None,
                url=row.url,
            )
            db.add(race)
            db.flush()
            race_id_by_season_round[(int(row.season), int(row.round))] = race.id
        db.commit()

        db.add_all(
            RaceResult(
                race_id=race_id_by_season_round[(int(row.season), int(row.round))],
                driver_id=row.driver_id,
                constructor_id=row.constructor_id,
                grid=int(row.grid),
                position=None if pd.isna(row.position) else int(row.position),
                position_text=row.position_text,
                points=float(row.points),
                laps=int(row.laps),
                status=row.status,
                finished=bool(row.finished),
                dnf=bool(row.dnf),
            )
            for row in results_df.itertuples()
        )
        db.add_all(
            QualifyingResult(
                race_id=race_id_by_season_round[(int(row.season), int(row.round))],
                driver_id=row.driver_id,
                constructor_id=row.constructor_id,
                position=int(row.position),
                q1_seconds=None if pd.isna(row.q1_seconds) else float(row.q1_seconds),
                q2_seconds=None if pd.isna(row.q2_seconds) else float(row.q2_seconds),
                q3_seconds=None if pd.isna(row.q3_seconds) else float(row.q3_seconds),
            )
            for row in qualifying_df.itertuples()
        )
        db.commit()

        logger.info(
            "Seeded %d seasons, %d circuits, %d drivers, %d constructors, %d races, %d results, %d qualifying rows",
            races_df["season"].nunique(),
            len(circuits_df),
            len(drivers_df),
            len(constructors_df),
            len(races_df),
            len(results_df),
            len(qualifying_df),
        )
    finally:
        db.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="../data/processed")
    args = parser.parse_args()
    seed(args.data_dir)


if __name__ == "__main__":
    main()
