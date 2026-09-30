from __future__ import annotations

import pytest

from ml.simulation.championship import ChampionshipDriverInput, simulate_championship


def _drivers(**overrides) -> list[ChampionshipDriverInput]:
    base = [
        ChampionshipDriverInput("leader", "team_a", predicted_position=2.0, dnf_probability=0.1, current_points=250.0),
        ChampionshipDriverInput("chaser", "team_a", predicted_position=2.0, dnf_probability=0.1, current_points=100.0),
        ChampionshipDriverInput("backmarker", "team_b", predicted_position=15.0, dnf_probability=0.2, current_points=10.0),
    ]
    return base


def test_probabilities_sum_to_one_across_drivers():
    result = simulate_championship(_drivers(), residual_std=1.5, n_remaining_races=5, n_trials=2000, seed=1)
    drivers = result["drivers"]
    assert drivers["championship_win_probability"].sum() == pytest.approx(1.0, abs=1e-6)


def test_large_points_lead_with_equal_pace_gives_leader_the_edge():
    """A big current lead should translate into a higher title-win
    probability even when both drivers have identical predicted pace,
    since the chaser has fewer remaining points available to close the gap."""
    result = simulate_championship(_drivers(), residual_std=1.5, n_remaining_races=3, n_trials=3000, seed=2)
    drivers = result["drivers"].set_index("driver_id")
    assert drivers.loc["leader", "championship_win_probability"] > drivers.loc["chaser", "championship_win_probability"]


def test_expected_final_points_never_below_current_points():
    result = simulate_championship(_drivers(), residual_std=1.5, n_remaining_races=4, n_trials=1000, seed=3)
    drivers = result["drivers"].set_index("driver_id")
    for driver_id in ["leader", "chaser", "backmarker"]:
        assert drivers.loc[driver_id, "expected_final_points"] >= drivers.loc[driver_id, "current_points"]


def test_zero_remaining_races_leaves_standings_unchanged():
    result = simulate_championship(_drivers(), residual_std=1.5, n_remaining_races=0, n_trials=500, seed=4)
    drivers = result["drivers"].set_index("driver_id")
    assert drivers.loc["leader", "expected_final_points"] == pytest.approx(250.0)
    assert drivers.loc["leader", "championship_win_probability"] == pytest.approx(1.0)


def test_constructor_points_aggregate_their_drivers():
    result = simulate_championship(_drivers(), residual_std=1.5, n_remaining_races=0, n_trials=100, seed=5)
    constructors = result["constructors"].set_index("constructor_id")
    # team_a = leader (250) + chaser (100) before any remaining races
    assert constructors.loc["team_a", "current_points"] == pytest.approx(350.0)
    assert constructors.loc["team_b", "current_points"] == pytest.approx(10.0)


def test_constructor_probabilities_sum_to_one():
    result = simulate_championship(_drivers(), residual_std=1.5, n_remaining_races=5, n_trials=2000, seed=6)
    constructors = result["constructors"]
    assert constructors["championship_win_probability"].sum() == pytest.approx(1.0, abs=1e-6)
