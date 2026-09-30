"""Projects the rest of the season's championship fight from the current
standings and the next race's pre-weekend predictions. See
ml/simulation/championship.py for the simulation mechanics and the
stated "current form held constant" assumption.
"""

from __future__ import annotations

from app.schemas.championship import (
    ChampionshipProjectionResponse,
    ConstructorChampionshipProjection,
    DriverChampionshipProjection,
)
from app.services.data_store import DataStore
from app.services.prediction_core import prepare_prediction
from ml.simulation.championship import ChampionshipDriverInput, simulate_championship

ASSUMPTION = (
    "Assumes every driver's current predicted pace and DNF risk (this "
    "week's pre-weekend prediction) holds constant for every remaining "
    "race - form is not re-simulated race by race. A projection from "
    "today's snapshot, not a forecast of how form will change."
)


def get_championship_projection(
    store: DataStore, model_dir: str, n_trials: int, seed: int
) -> ChampionshipProjectionResponse | None:
    if store.races.empty:
        return None
    season = int(store.races["season"].max())
    season_results = store.race_results[store.race_results["season"] == season]
    if season_results.empty:
        return None

    last_completed_round = int(season_results["round"].max())
    remaining = store.races[(store.races["season"] == season) & (store.races["round"] > last_completed_round)]
    if remaining.empty:
        return None  # season is over - nothing left to project

    next_race = remaining.sort_values("round").iloc[0]
    next_race_id = store.race_slug(season, int(next_race["round"]), next_race["circuit_id"])

    prepared = prepare_prediction(store, model_dir, next_race_id, "pre_weekend")
    if prepared is None:
        return None

    current_points = season_results.groupby("driver_id")["points"].sum().to_dict()

    drivers_input = [
        ChampionshipDriverInput(
            driver_id=row.driver_id,
            constructor_id=row.constructor_id,
            predicted_position=row.predicted_position,
            dnf_probability=row.dnf_probability,
            current_points=current_points.get(row.driver_id, 0.0),
        )
        for row in prepared.predictions.itertuples()
    ]

    result = simulate_championship(
        drivers_input,
        residual_std=prepared.artifacts.residual_std,
        n_remaining_races=len(remaining),
        n_trials=n_trials,
        seed=seed,
    )

    driver_meta = store.drivers.set_index("driver_id")
    constructor_meta = store.constructors.set_index("constructor_id")

    driver_projections = [
        DriverChampionshipProjection(
            driver_id=row.driver_id,
            driver_name=f"{driver_meta.loc[row.driver_id, 'given_name']} {driver_meta.loc[row.driver_id, 'family_name']}",
            constructor_id=next(d.constructor_id for d in drivers_input if d.driver_id == row.driver_id),
            current_points=row.current_points,
            expected_final_points=row.expected_final_points,
            championship_win_probability=row.championship_win_probability,
            top3_championship_probability=row.top3_championship_probability,
        )
        for row in result["drivers"].itertuples()
    ]
    constructor_projections = [
        ConstructorChampionshipProjection(
            constructor_id=row.constructor_id,
            constructor_name=constructor_meta.loc[row.constructor_id, "name"],
            current_points=row.current_points,
            expected_final_points=row.expected_final_points,
            championship_win_probability=row.championship_win_probability,
            top3_championship_probability=row.top3_championship_probability,
        )
        for row in result["constructors"].itertuples()
    ]

    return ChampionshipProjectionResponse(
        season=season,
        last_completed_round=last_completed_round,
        remaining_races=len(remaining),
        n_trials=n_trials,
        seed=seed,
        assumption=ASSUMPTION,
        drivers=driver_projections,
        constructors=constructor_projections,
    )
