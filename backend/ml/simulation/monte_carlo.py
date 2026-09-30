"""Monte Carlo race simulator.

Turns a per-driver predicted finishing position + DNF probability into a
distribution over race outcomes by simulating the race thousands of times.
Each simulated race is a single valid finishing-order permutation (no
duplicate positions, DNF'd drivers always classified behind every finisher)
built from:

  1. A performance sample per driver: predicted_position + Normal(0, sigma)
     noise, where sigma is the position model's residual std on the
     validation season (i.e. genuine, measured pace uncertainty, not a
     made-up constant).
  2. A DNF draw per driver from the calibrated DNF model's probability.

This is not "random for show" — every simulated race is driven directly by
the trained models' own outputs, so tighter model predictions/lower DNF risk
produce visibly tighter probability distributions, and the whole thing is
reproducible via `seed`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# Modern F1 points scheme, positions 1-10 (fastest-lap point omitted: it
# depends on lap-by-lap race state this project doesn't simulate).
POINTS_TABLE = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
DEFAULT_N_SIMULATIONS = 10_000


@dataclass(frozen=True)
class DriverSimulationInput:
    driver_id: str
    predicted_position: float
    dnf_probability: float


def points_for_positions(positions: np.ndarray) -> np.ndarray:
    """Shared by the single-race simulator and the championship simulator
    (ml/simulation/championship.py), so both use the exact same scoring."""
    points = np.zeros_like(positions, dtype=float)
    for pos, pts in POINTS_TABLE.items():
        points[positions == pos] = pts
    return points


@dataclass(frozen=True)
class SimulationResult:
    summary: pd.DataFrame  # one row per driver: win/podium/.../expected_* probabilities
    positions_matrix: np.ndarray  # (n_simulations, n_drivers) finishing position per sim
    driver_ids: list[str]
    n_simulations: int
    seed: int

    def most_common_podium(self, top_n: int = 3) -> list[str]:
        """The single most frequent exact top-`top_n` finishing combination
        across all simulated races (order-sensitive: P1/P2/P3)."""
        driver_ids = np.array(self.driver_ids)
        podium_indices = np.argsort(self.positions_matrix, axis=1)[:, :top_n]
        podium_tuples = np.array([driver_ids[row] for row in podium_indices])
        unique, counts = np.unique(podium_tuples, axis=0, return_counts=True)
        return list(unique[np.argmax(counts)])


def simulate_race(
    drivers: list[DriverSimulationInput],
    residual_std: float,
    n_simulations: int = DEFAULT_N_SIMULATIONS,
    seed: int = 42,
) -> SimulationResult:
    """Run the Monte Carlo simulation and return aggregated per-driver
    probabilities plus the raw positions matrix (for most_common_podium)."""
    rng = np.random.default_rng(seed)
    n_drivers = len(drivers)
    driver_ids = [d.driver_id for d in drivers]
    predicted = np.array([d.predicted_position for d in drivers])
    dnf_prob = np.clip(np.array([d.dnf_probability for d in drivers]), 0.0, 0.95)

    noise = rng.normal(loc=0.0, scale=max(residual_std, 0.5), size=(n_simulations, n_drivers))
    performance_scores = predicted[None, :] + noise

    dnf_draws = rng.random((n_simulations, n_drivers)) < dnf_prob[None, :]
    # DNF'd drivers are always classified behind every finisher; a small
    # random tiebreak keeps their *relative* order among each other random
    # rather than fixed by array position.
    dnf_penalty = np.where(dnf_draws, 1000.0 + rng.random((n_simulations, n_drivers)) * 100.0, 0.0)
    final_scores = performance_scores + dnf_penalty

    # rank 1..n_drivers per simulated race (ties broken by score order, which
    # is already randomized via the noise/tiebreak above).
    positions = final_scores.argsort(axis=1).argsort(axis=1) + 1

    points = points_for_positions(positions)

    rows = []
    for i, driver_id in enumerate(driver_ids):
        driver_positions = positions[:, i]
        driver_dnf = dnf_draws[:, i]
        rows.append(
            {
                "driver_id": driver_id,
                "win_probability": float(np.mean(driver_positions == 1)),
                "podium_probability": float(np.mean(driver_positions <= 3)),
                "top5_probability": float(np.mean(driver_positions <= 5)),
                "points_probability": float(np.mean((driver_positions <= 10) & ~driver_dnf)),
                "dnf_probability": float(np.mean(driver_dnf)),
                "expected_finish_position": float(np.mean(driver_positions)),
                "expected_points": float(np.mean(points[:, i])),
            }
        )

    return SimulationResult(
        summary=pd.DataFrame(rows),
        positions_matrix=positions,
        driver_ids=driver_ids,
        n_simulations=n_simulations,
        seed=seed,
    )
