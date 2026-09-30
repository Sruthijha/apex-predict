"""Regression test: in pre_weekend mode, grid_position is a placeholder
(qualifying hasn't happened) filled with a fallback value, not a real signal.
It must never surface as an explanation factor in that mode - only once
qualifying has actually happened (post_qualifying mode)."""

from __future__ import annotations

import pandas as pd
import pytest

from ml.inference.explain import _relative_rank_pct, explain_driver


def _field_with_grid_positions() -> pd.DataFrame:
    # Every metric is identical across the field EXCEPT grid_position, so
    # grid is the only factor that could possibly surface - isolating the
    # mode gate from the separate "top 3 factors" truncation.
    return pd.DataFrame(
        {
            "driver_recent_form_score": [5.0, 5.0, 5.0],
            "driver_recent_finish_mean_5": [8.0, 8.0, 8.0],
            "constructor_recent_points_mean_5": [10.0, 10.0, 10.0],
            "driver_circuit_avg_finish": [8.0, 8.0, 8.0],
            "driver_dnf_rate_recent_10": [0.1, 0.1, 0.1],
            "constructor_dnf_rate_recent_10": [0.1, 0.1, 0.1],
            # Every other driver has a "real" grid position except our subject,
            # whose value is the pre_weekend placeholder fallback (0).
            "grid_position": [5.0, 10.0, 15.0],
        }
    )


def test_grid_factor_never_appears_in_pre_weekend_mode():
    field = _field_with_grid_positions()
    row = field.iloc[0].copy()
    row["grid_position"] = 0.0  # placeholder value used when qualifying hasn't happened

    explanation = explain_driver(row, field, mode="pre_weekend")
    combined_text = " ".join(explanation["positive"] + explanation["risk"])
    assert "grid position" not in combined_text.lower()


def test_tying_the_entire_field_is_average_not_worst():
    """A value tied with every other value in the field is exactly average
    (0.5), not the worst (0.0) - a driver shouldn't get flagged as a risk
    factor just because their metric happens to equal everyone else's."""
    series = pd.Series([5.0, 5.0, 5.0, 5.0])
    assert _relative_rank_pct(5.0, series, higher_is_better=True) == pytest.approx(0.5)
    assert _relative_rank_pct(5.0, series, higher_is_better=False) == pytest.approx(0.5)


def test_grid_factor_can_appear_in_post_qualifying_mode():
    field = _field_with_grid_positions()
    row = field.iloc[2].copy()  # worst grid position (15) among the three

    explanation = explain_driver(row, field, mode="post_qualifying")
    combined_text = " ".join(explanation["positive"] + explanation["risk"])
    assert "grid position" in combined_text.lower()
