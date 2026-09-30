from __future__ import annotations

import numpy as np
import pytest

from ml.simulation.monte_carlo import DriverSimulationInput, simulate_race


def _sample_drivers(n: int = 10) -> list[DriverSimulationInput]:
    return [
        DriverSimulationInput(driver_id=f"d{i}", predicted_position=float(i + 1), dnf_probability=0.1)
        for i in range(n)
    ]


def test_every_simulated_race_is_a_valid_permutation():
    result = simulate_race(_sample_drivers(8), residual_std=1.5, n_simulations=500, seed=1)
    positions = result.positions_matrix
    expected = set(range(1, 9))
    for row in positions:
        assert set(row.tolist()) == expected  # no duplicate/missing positions in any single race


def test_probabilities_sum_correctly():
    result = simulate_race(_sample_drivers(6), residual_std=1.0, n_simulations=5000, seed=7)
    summary = result.summary
    assert summary["win_probability"].sum() == pytest.approx(1.0)
    assert summary["podium_probability"].sum() == pytest.approx(3.0)


def test_reproducible_with_same_seed():
    a = simulate_race(_sample_drivers(10), residual_std=2.0, n_simulations=1000, seed=99)
    b = simulate_race(_sample_drivers(10), residual_std=2.0, n_simulations=1000, seed=99)
    np.testing.assert_array_equal(a.positions_matrix, b.positions_matrix)


def test_different_seeds_give_different_results():
    a = simulate_race(_sample_drivers(10), residual_std=2.0, n_simulations=1000, seed=1)
    b = simulate_race(_sample_drivers(10), residual_std=2.0, n_simulations=1000, seed=2)
    assert not np.array_equal(a.positions_matrix, b.positions_matrix)


def test_favorite_has_highest_win_probability():
    drivers = [
        DriverSimulationInput(driver_id="favorite", predicted_position=1.0, dnf_probability=0.05),
        DriverSimulationInput(driver_id="midfield", predicted_position=10.0, dnf_probability=0.1),
        DriverSimulationInput(driver_id="backmarker", predicted_position=18.0, dnf_probability=0.1),
    ]
    result = simulate_race(drivers, residual_std=2.0, n_simulations=5000, seed=3)
    summary = result.summary.set_index("driver_id")
    assert summary.loc["favorite", "win_probability"] > summary.loc["midfield", "win_probability"]
    assert summary.loc["midfield", "win_probability"] > summary.loc["backmarker", "win_probability"]


def test_higher_dnf_input_increases_simulated_dnf_rate():
    drivers = [
        DriverSimulationInput(driver_id="reliable", predicted_position=5.0, dnf_probability=0.02),
        DriverSimulationInput(driver_id="fragile", predicted_position=5.0, dnf_probability=0.5),
    ]
    result = simulate_race(drivers, residual_std=1.5, n_simulations=5000, seed=4)
    summary = result.summary.set_index("driver_id")
    assert summary.loc["fragile", "dnf_probability"] > summary.loc["reliable", "dnf_probability"]


def test_most_common_podium_returns_three_distinct_drivers():
    result = simulate_race(_sample_drivers(10), residual_std=1.0, n_simulations=2000, seed=5)
    podium = result.most_common_podium()
    assert len(podium) == 3
    assert len(set(podium)) == 3
