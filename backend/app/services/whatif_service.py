"""What-If scenario tool: grid position changes, manual DNF overrides, and a
weather heuristic layered on top of the real trained models and simulator.

Grid-position overrides are genuine: they modify the feature row fed to the
actual trained post-qualifying model and re-run inference, so the resulting
shift in predicted position is a real model response, not a fabrication.

Weather is different and is labeled as such everywhere it appears: this
project has no historical weather data (see README "Limitations"), so there
is no trained weather feature to flip. Instead, "wet"/"mixed" apply a
documented multiplier to DNF probability and to the simulator's pace-
variance (residual_std) - a defensible way to say "conditions got less
predictable and more crash-prone" without pretending the model learned
anything about rain.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.schemas.whatif import WhatIfDriverOutcome, WhatIfRequest, WhatIfResponse
from app.services.data_store import DataStore
from app.services.prediction_core import prepare_prediction
from ml.simulation.monte_carlo import DriverSimulationInput, simulate_race

WEATHER_DNF_MULTIPLIER = {"dry": 1.0, "mixed": 1.4, "wet": 2.0}
WEATHER_VARIANCE_MULTIPLIER = {"dry": 1.0, "mixed": 1.3, "wet": 1.7}

DISCLAIMER = (
    "This is an interactive scenario tool, not an official forecast. "
    "Grid-position changes re-run the real trained model. Weather effects "
    "are a documented heuristic (DNF-risk and pace-variance multipliers) - "
    "this project has no historical weather data, so there is no trained "
    "weather model behind them."
)


def _sim_inputs(preds: pd.DataFrame) -> list[DriverSimulationInput]:
    return [
        DriverSimulationInput(driver_id=r.driver_id, predicted_position=r.predicted_position, dnf_probability=r.dnf_probability)
        for r in preds.itertuples()
    ]


def run_whatif(store: DataStore, model_dir: str, race_id: str, request: WhatIfRequest) -> WhatIfResponse | None:
    mode = request.prediction_mode
    prepared = prepare_prediction(store, model_dir, race_id, mode)
    if prepared is None and mode == "post_qualifying":
        mode = "pre_weekend"
        prepared = prepare_prediction(store, model_dir, race_id, mode)
    if prepared is None:
        return None

    baseline_preds = prepared.predictions
    scenario_preds = baseline_preds.copy()
    applied_changes: list[str] = []

    if request.grid_overrides:
        if mode != "post_qualifying":
            applied_changes.append(
                "Grid position changes only affect the post-qualifying model - ignored in pre-weekend mode."
            )
        else:
            modified_features = prepared.feature_rows.copy()
            valid_drivers = set(modified_features["driver_id"])
            for driver_id, new_grid in request.grid_overrides.items():
                if driver_id not in valid_drivers:
                    continue
                modified_features.loc[modified_features["driver_id"] == driver_id, "grid_position"] = float(new_grid)
                applied_changes.append(f"{driver_id}: grid position set to P{new_grid}")
            if applied_changes:
                # `modified_features` and `scenario_preds` are NOT necessarily
                # in the same row order (prepare_prediction's `predictions`
                # is sorted by predicted_position, feature_rows isn't) - align
                # the freshly-predicted values back by driver_id explicitly
                # rather than assuming positional order matches.
                new_positions = pd.Series(
                    prepared.artifacts.position_pipeline.predict(modified_features),
                    index=modified_features["driver_id"].to_numpy(),
                )
                scenario_preds["predicted_position"] = scenario_preds["driver_id"].map(new_positions)

    weather = request.weather if request.weather in WEATHER_DNF_MULTIPLIER else "dry"
    dnf_multiplier = WEATHER_DNF_MULTIPLIER[weather]
    variance_multiplier = WEATHER_VARIANCE_MULTIPLIER[weather]
    if weather != "dry":
        applied_changes.append(
            f"Weather scenario: {weather} - DNF risk x{dnf_multiplier}, pace variance x{variance_multiplier} (heuristic)"
        )
    scenario_preds["dnf_probability"] = np.clip(scenario_preds["dnf_probability"] * dnf_multiplier, 0.0, 0.95)

    for driver_id, prob in request.dnf_overrides.items():
        if driver_id in scenario_preds["driver_id"].values:
            scenario_preds.loc[scenario_preds["driver_id"] == driver_id, "dnf_probability"] = float(np.clip(prob, 0.0, 1.0))
            applied_changes.append(f"{driver_id}: DNF probability manually set to {prob:.0%}")

    if not applied_changes:
        applied_changes.append("No changes applied - this is the baseline prediction.")

    baseline_result = simulate_race(
        _sim_inputs(baseline_preds), prepared.artifacts.residual_std, n_simulations=request.n_simulations, seed=request.seed
    )
    scenario_result = simulate_race(
        _sim_inputs(scenario_preds),
        prepared.artifacts.residual_std * variance_multiplier,
        n_simulations=request.n_simulations,
        seed=request.seed,
    )

    baseline_by_driver = baseline_result.summary.set_index("driver_id")
    scenario_by_driver = scenario_result.summary.set_index("driver_id")
    driver_meta = store.drivers.set_index("driver_id")

    outcomes = []
    for driver_id in baseline_preds["driver_id"]:
        b, s = baseline_by_driver.loc[driver_id], scenario_by_driver.loc[driver_id]
        outcomes.append(
            WhatIfDriverOutcome(
                driver_id=driver_id,
                driver_name=f"{driver_meta.loc[driver_id, 'given_name']} {driver_meta.loc[driver_id, 'family_name']}",
                baseline_win_probability=float(b["win_probability"]),
                scenario_win_probability=float(s["win_probability"]),
                baseline_podium_probability=float(b["podium_probability"]),
                scenario_podium_probability=float(s["podium_probability"]),
                baseline_dnf_probability=float(b["dnf_probability"]),
                scenario_dnf_probability=float(s["dnf_probability"]),
                baseline_expected_position=float(b["expected_finish_position"]),
                scenario_expected_position=float(s["expected_finish_position"]),
            )
        )
    outcomes.sort(key=lambda o: -o.scenario_win_probability)

    return WhatIfResponse(
        race_id=race_id,
        prediction_mode=mode,
        weather=weather,
        applied_changes=applied_changes,
        disclaimer=DISCLAIMER,
        outcomes=outcomes,
    )
