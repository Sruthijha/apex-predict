"""Championship simulation: projects the rest of a season thousands of times
to estimate each driver's (and constructor's) final points distribution and
title-winning probability.

Stated assumption (surfaced to the API/UI, not hidden): each driver's
current predicted pace and DNF risk — the pre-weekend prediction for the
next race — is held constant across every remaining race. Real form
evolves race to race; re-simulating the feature pipeline after every
hypothetical result would let this compound correctly, but that is a much
larger undertaking than a portfolio project's "what does the title fight
look like from here" feature warrants. This is Monte Carlo over a frozen
snapshot of current form, not a forecast of how that form will change.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ml.simulation.monte_carlo import points_for_positions

DEFAULT_N_TRIALS = 5000


@dataclass(frozen=True)
class ChampionshipDriverInput:
    driver_id: str
    constructor_id: str
    predicted_position: float
    dnf_probability: float
    current_points: float


def simulate_championship(
    drivers: list[ChampionshipDriverInput],
    residual_std: float,
    n_remaining_races: int,
    n_trials: int = DEFAULT_N_TRIALS,
    seed: int = 42,
) -> dict:
    """Returns driver and constructor championship projections."""
    rng = np.random.default_rng(seed)
    n_drivers = len(drivers)
    driver_ids = [d.driver_id for d in drivers]
    predicted = np.array([d.predicted_position for d in drivers])
    dnf_prob = np.clip(np.array([d.dnf_probability for d in drivers]), 0.0, 0.95)
    current_points = np.array([d.current_points for d in drivers])

    total_points = np.zeros((n_trials, n_drivers))
    for _ in range(n_remaining_races):
        noise = rng.normal(0.0, max(residual_std, 0.5), size=(n_trials, n_drivers))
        scores = predicted[None, :] + noise
        dnf_draws = rng.random((n_trials, n_drivers)) < dnf_prob[None, :]
        dnf_penalty = np.where(dnf_draws, 1000.0 + rng.random((n_trials, n_drivers)) * 100.0, 0.0)
        positions = (scores + dnf_penalty).argsort(axis=1).argsort(axis=1) + 1
        total_points += points_for_positions(positions)

    final_points = total_points + current_points[None, :]
    driver_ranks = (-final_points).argsort(axis=1).argsort(axis=1) + 1  # 1 = champion

    driver_rows = []
    for i, driver_id in enumerate(driver_ids):
        driver_rows.append(
            {
                "driver_id": driver_id,
                "current_points": float(current_points[i]),
                "expected_final_points": float(np.mean(final_points[:, i])),
                "championship_win_probability": float(np.mean(driver_ranks[:, i] == 1)),
                "top3_championship_probability": float(np.mean(driver_ranks[:, i] <= 3)),
            }
        )
    driver_summary = pd.DataFrame(driver_rows).sort_values("expected_final_points", ascending=False)

    constructor_ids = sorted({d.constructor_id for d in drivers})
    constructor_index = {cid: [i for i, d in enumerate(drivers) if d.constructor_id == cid] for cid in constructor_ids}
    constructor_final_points = np.column_stack(
        [final_points[:, idxs].sum(axis=1) for idxs in constructor_index.values()]
    )
    constructor_ranks = (-constructor_final_points).argsort(axis=1).argsort(axis=1) + 1

    constructor_rows = []
    for j, constructor_id in enumerate(constructor_ids):
        idxs = constructor_index[constructor_id]
        constructor_rows.append(
            {
                "constructor_id": constructor_id,
                "current_points": float(current_points[idxs].sum()),
                "expected_final_points": float(np.mean(constructor_final_points[:, j])),
                "championship_win_probability": float(np.mean(constructor_ranks[:, j] == 1)),
                "top3_championship_probability": float(np.mean(constructor_ranks[:, j] <= 3)),
            }
        )
    constructor_summary = pd.DataFrame(constructor_rows).sort_values("expected_final_points", ascending=False)

    return {"drivers": driver_summary, "constructors": constructor_summary}
