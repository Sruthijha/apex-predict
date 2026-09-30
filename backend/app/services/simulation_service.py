"""The Race Lab: user-triggered Monte Carlo simulation with a chosen
simulation count and seed, persisted to simulation_runs/simulation_driver_results
so a run's provenance (model version, seed, count) is always traceable."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.ml import ModelVersion, SimulationDriverResult, SimulationRun
from app.models.motorsport import Race
from app.schemas.simulation import DriverSimulationOutcome, SimulationResponse
from app.services.data_store import DataStore
from app.services.prediction_core import prepare_prediction
from ml.inference.model_registry import model_version_string
from ml.simulation.monte_carlo import DriverSimulationInput, simulate_race


def run_race_simulation(
    db: Session,
    store: DataStore,
    model_dir: str,
    race_id: str,
    mode: str,
    n_simulations: int,
    seed: int,
) -> SimulationResponse | None:
    prepared = prepare_prediction(store, model_dir, race_id, mode)
    if prepared is None:
        return None

    preds, artifacts = prepared.predictions, prepared.artifacts
    driver_meta = store.drivers.set_index("driver_id")

    sim_inputs = [
        DriverSimulationInput(driver_id=r.driver_id, predicted_position=r.predicted_position, dnf_probability=r.dnf_probability)
        for r in preds.itertuples()
    ]
    result = simulate_race(sim_inputs, artifacts.residual_std, n_simulations=n_simulations, seed=seed)
    summary = result.summary.sort_values("win_probability", ascending=False)
    most_common_podium = result.most_common_podium()

    race_pk = db.query(Race).filter_by(season_year=prepared.season, round=prepared.round).first()
    if race_pk is not None:
        version = model_version_string(model_dir)
        model_version = db.query(ModelVersion).filter_by(version=version, prediction_mode=mode).first()
        if model_version is not None:
            run = SimulationRun(
                race_id=race_pk.id,
                model_version_id=model_version.id,
                prediction_mode=mode,
                n_simulations=n_simulations,
                seed=seed,
                most_common_podium=most_common_podium,
            )
            db.add(run)
            db.flush()
            db.add_all(
                SimulationDriverResult(
                    simulation_run_id=run.id,
                    driver_id=r.driver_id,
                    win_probability=float(r.win_probability),
                    podium_probability=float(r.podium_probability),
                    top5_probability=float(r.top5_probability),
                    points_probability=float(r.points_probability),
                    dnf_probability=float(r.dnf_probability),
                    expected_finish_position=float(r.expected_finish_position),
                )
                for r in summary.itertuples()
            )
            db.commit()

    outcomes = [
        DriverSimulationOutcome(
            driver_id=r.driver_id,
            driver_name=f"{driver_meta.loc[r.driver_id, 'given_name']} {driver_meta.loc[r.driver_id, 'family_name']}",
            win_probability=float(r.win_probability),
            podium_probability=float(r.podium_probability),
            top5_probability=float(r.top5_probability),
            points_probability=float(r.points_probability),
            dnf_probability=float(r.dnf_probability),
            expected_finish_position=float(r.expected_finish_position),
            expected_points=float(r.expected_points),
        )
        for r in summary.itertuples()
    ]

    return SimulationResponse(
        race_id=race_id,
        n_simulations=n_simulations,
        seed=seed,
        prediction_mode=mode,
        outcomes=outcomes,
        most_common_podium=most_common_podium,
    )
