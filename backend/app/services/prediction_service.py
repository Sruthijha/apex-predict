"""Ties together live feature construction, the trained models, the Monte
Carlo simulator, and explanations into one race prediction.

Works for both an upcoming race (no results yet -> lineup assumed from the
most recent race) and a historical race (results exist -> the real lineup is
used, and the target race's own result is excluded from its own feature
computation) - the latter is what powers the "Model vs Reality" backtesting
view, using the exact same code path as a live prediction.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy.orm import Session

from app.models.ml import ModelPrediction, ModelVersion
from app.models.motorsport import Race
from app.schemas.predictions import DriverExplanation, DriverPrediction, RacePrediction
from app.services.data_store import DataStore
from app.services.prediction_core import prepare_prediction
from ml.inference.explain import confidence_label, explain_driver
from ml.inference.model_registry import model_version_string
from ml.simulation.monte_carlo import DriverSimulationInput, simulate_race

PREDICTION_SIMULATION_COUNT = 5000
PREDICTION_SEED = 42


def _get_or_create_model_version(db: Session, model_dir: str, mode: str, artifacts) -> ModelVersion:
    version = model_version_string(model_dir)
    existing = db.query(ModelVersion).filter_by(version=version, prediction_mode=mode).first()
    if existing:
        return existing
    mv = ModelVersion(
        version=version,
        prediction_mode=mode,
        algorithm=artifacts.algorithm,
        feature_version=version.split("-")[0],
        train_seasons="2015-2022",
        validation_season=2023,
        test_season=2024,
        metrics=artifacts.metrics,
    )
    db.add(mv)
    db.commit()
    db.refresh(mv)
    return mv


def build_race_prediction(
    db: Session, store: DataStore, model_dir: str, race_id: str, mode: str
) -> RacePrediction | None:
    prepared = prepare_prediction(store, model_dir, race_id, mode)
    if prepared is None:
        return None

    season, round_, preds, feature_rows, artifacts = (
        prepared.season,
        prepared.round,
        prepared.predictions,
        prepared.feature_rows,
        prepared.artifacts,
    )

    sim_inputs = [
        DriverSimulationInput(driver_id=r.driver_id, predicted_position=r.predicted_position, dnf_probability=r.dnf_probability)
        for r in preds.itertuples()
    ]
    sim_result = simulate_race(sim_inputs, artifacts.residual_std, n_simulations=PREDICTION_SIMULATION_COUNT, seed=PREDICTION_SEED)
    sim_by_driver = sim_result.summary.set_index("driver_id")

    feature_by_driver = feature_rows.set_index("driver_id")
    driver_meta = store.drivers.set_index("driver_id")
    constructor_meta = store.constructors.set_index("constructor_id")

    race_pk = db.query(Race).filter_by(season_year=season, round=round_).first()
    if race_pk is None:
        return None  # race not present in the seeded DB (out of sync with the parquet store)

    model_version = _get_or_create_model_version(db, model_dir, mode, artifacts)
    db.query(ModelPrediction).filter_by(
        race_id=race_pk.id, model_version_id=model_version.id, prediction_mode=mode
    ).delete()

    driver_predictions = []
    for pred_row in preds.itertuples():
        driver_id = pred_row.driver_id
        sim = sim_by_driver.loc[driver_id]
        feature_row = feature_by_driver.loc[driver_id]
        explanation = explain_driver(feature_row, feature_rows, mode)
        confidence = confidence_label(feature_row, artifacts.residual_std)
        driver = driver_meta.loc[driver_id]
        constructor = constructor_meta.loc[pred_row.constructor_id]

        db.add(
            ModelPrediction(
                race_id=race_pk.id,
                driver_id=driver_id,
                model_version_id=model_version.id,
                prediction_mode=mode,
                predicted_position=float(pred_row.predicted_position),
                win_probability=float(sim["win_probability"]),
                podium_probability=float(sim["podium_probability"]),
                top5_probability=float(sim["top5_probability"]),
                points_probability=float(sim["points_probability"]),
                dnf_probability=float(pred_row.dnf_probability),
                expected_points=float(sim["expected_points"]),
                confidence=confidence,
                explanation=explanation,
            )
        )

        driver_predictions.append(
            DriverPrediction(
                driver_id=driver_id,
                driver_name=f"{driver['given_name']} {driver['family_name']}",
                driver_code=driver["code"],
                constructor_id=pred_row.constructor_id,
                constructor_name=constructor["name"],
                predicted_position=float(pred_row.predicted_position),
                win_probability=float(sim["win_probability"]),
                podium_probability=float(sim["podium_probability"]),
                top5_probability=float(sim["top5_probability"]),
                points_probability=float(sim["points_probability"]),
                dnf_probability=float(pred_row.dnf_probability),
                expected_points=float(sim["expected_points"]),
                confidence=confidence,
                explanation=DriverExplanation(**explanation),
            )
        )

    db.commit()

    return RacePrediction(
        race_id=race_id,
        season=season,
        round=round_,
        prediction_mode=mode,
        model_version=model_version.version,
        generated_at=dt.datetime.utcnow(),
        drivers=driver_predictions,
    )
