"""Rule-based, per-driver prediction explanations.

Every explanation is derived directly from that driver's actual feature
values, compared against the rest of the field in the *same* race (so
"strong recent form" means relative to this specific grid, not an arbitrary
fixed threshold). Nothing here is fabricated text unconnected to the model's
actual inputs — see ml/features/feature_columns.py for what these columns
mean and how they're computed.

Global feature importance (which columns matter most overall) is a separate,
SHAP-based analysis computed once during training/evaluation — see
ml/evaluation/feature_importance.py and the Model Lab page.
"""

from __future__ import annotations

import pandas as pd

MAX_FACTORS_PER_SIDE = 3


def _relative_rank_pct(value: float, series: pd.Series, higher_is_better: bool) -> float:
    """0.0 (worst in field) .. 1.0 (best in field). Ties count as half-better,
    half-worse (a value tied with the entire field is exactly average - 0.5 -
    not the worst, which a naive strict-inequality count would wrongly give)."""
    valid = series.dropna()
    if pd.isna(value) or valid.empty:
        return 0.5
    better = (valid < value).sum() if higher_is_better else (valid > value).sum()
    worse = (valid > value).sum() if higher_is_better else (valid < value).sum()
    tied = len(valid) - better - worse
    return float((better + 0.5 * tied) / len(valid))


def explain_driver(row: pd.Series, field: pd.DataFrame, mode: str) -> dict:
    """`row` is one driver's feature+prediction row; `field` is every driver
    in the same race (used to judge "strong" / "weak" relative to the grid).
    `mode` gates the grid-position factor: in pre_weekend mode grid_position
    is a meaningless placeholder (qualifying hasn't happened), not a real
    value, so it must never surface as an explanation there."""
    candidates: list[tuple[float, str, str]] = []  # (strength 0-1, direction, text)

    def add(value, series, higher_is_better, good_text, bad_text, threshold=0.65):
        pct = _relative_rank_pct(value, series, higher_is_better)
        if pct >= threshold:
            candidates.append((pct, "positive", good_text))
        elif pct <= 1 - threshold:
            candidates.append((1 - pct, "risk", bad_text))

    add(
        row.get("driver_recent_form_score"),
        field["driver_recent_form_score"],
        True,
        "Strong recent scoring form",
        "Below-average recent scoring form",
    )
    add(
        row.get("driver_recent_finish_mean_5"),
        field["driver_recent_finish_mean_5"],
        False,  # lower finish position number = better
        "Consistently finishing well over the last 5 races",
        "Inconsistent recent finishes",
    )
    add(
        row.get("constructor_recent_points_mean_5"),
        field["constructor_recent_points_mean_5"],
        True,
        "Car scoring well in recent races",
        "Constructor underperforming recently",
    )
    if mode == "post_qualifying" and pd.notna(row.get("grid_position")):
        add(
            row.get("grid_position"),
            field["grid_position"],
            False,
            "Strong grid position",
            "Difficult grid position to recover from",
        )
    add(
        row.get("driver_circuit_avg_finish"),
        field["driver_circuit_avg_finish"],
        False,
        "Historically strong result at this circuit",
        "Historically weaker result at this circuit",
    )
    add(
        row.get("driver_dnf_rate_recent_10"),
        field["driver_dnf_rate_recent_10"],
        False,  # higher dnf rate = worse, so "lower is better" framing
        "Reliable recent finishing record",
        "Elevated recent DNF rate",
    )
    add(
        row.get("constructor_dnf_rate_recent_10"),
        field["constructor_dnf_rate_recent_10"],
        False,
        "Constructor reliability trending well",
        "Constructor reliability risk",
    )

    positives = sorted([c for c in candidates if c[1] == "positive"], key=lambda c: -c[0])[:MAX_FACTORS_PER_SIDE]
    risks = sorted([c for c in candidates if c[1] == "risk"], key=lambda c: -c[0])[:MAX_FACTORS_PER_SIDE]

    return {
        "positive": [text for _, _, text in positives],
        "risk": [text for _, _, text in risks],
    }


DATA_COMPLETENESS_COLUMNS = [
    "driver_recent_finish_mean_5",
    "driver_recent_points_mean_5",
    "driver_circuit_avg_finish",
    "constructor_recent_points_mean_5",
    "constructor_circuit_avg_finish",
]


def confidence_label(row: pd.Series, residual_std: float) -> str:
    """Systematically derived, not vibes: starts from the model's own
    residual uncertainty for this mode, then downgrades a tier for every
    missing piece of this specific driver's history (e.g. a rookie's first
    race, or a first visit to this circuit) — exactly the situations where a
    prediction genuinely has less to go on."""
    missing = sum(1 for col in DATA_COMPLETENESS_COLUMNS if pd.isna(row.get(col)))

    if residual_std < 2.5:
        tier = 2  # HIGH
    elif residual_std < 4.0:
        tier = 1  # MEDIUM
    else:
        tier = 0  # LOW

    if missing >= 3:
        tier -= 2
    elif missing >= 1:
        tier -= 1

    return ["LOW", "MEDIUM", "HIGH"][max(0, min(2, tier))]
