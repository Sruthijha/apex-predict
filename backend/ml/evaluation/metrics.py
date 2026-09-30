"""Evaluation metrics for the finishing-position ranking model and the
binary classifiers (DNF, and any other risk model). Kept dependency-light
and framework-agnostic: everything takes plain arrays/DataFrames.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error, mean_squared_error, roc_auc_score


def regression_metrics(df: pd.DataFrame, y_true_col: str, y_pred_col: str) -> dict:
    """MAE/RMSE plus per-race ranking quality, averaged across races.

    Ranking metrics are computed per (season, round) group because "did the
    model get the order right within this race" is the question that
    matters, not a MAE/RMSE-style pointwise comparison across all drivers in
    the whole test set at once.
    """
    mae = mean_absolute_error(df[y_true_col], df[y_pred_col])
    rmse = float(np.sqrt(mean_squared_error(df[y_true_col], df[y_pred_col])))

    spearman_scores, kendall_scores, top3_overlaps = [], [], []
    for _, race in df.groupby(["season", "round"]):
        if len(race) < 3:
            continue
        rho, _ = spearmanr(race[y_true_col], race[y_pred_col])
        tau, _ = kendalltau(race[y_true_col], race[y_pred_col])
        if not np.isnan(rho):
            spearman_scores.append(rho)
        if not np.isnan(tau):
            kendall_scores.append(tau)

        actual_top3 = set(race.sort_values(y_true_col).head(3).index)
        predicted_top3 = set(race.sort_values(y_pred_col).head(3).index)
        top3_overlaps.append(len(actual_top3 & predicted_top3) / 3.0)

    return {
        "mae": float(mae),
        "rmse": rmse,
        "spearman_mean": float(np.mean(spearman_scores)) if spearman_scores else None,
        "kendall_mean": float(np.mean(kendall_scores)) if kendall_scores else None,
        "top3_overlap_mean": float(np.mean(top3_overlaps)) if top3_overlaps else None,
        "n_races": len(spearman_scores),
    }


def classification_metrics(y_true: np.ndarray, y_prob: np.ndarray) -> dict:
    y_true = np.asarray(y_true)
    y_prob = np.clip(np.asarray(y_prob), 1e-6, 1 - 1e-6)
    metrics = {
        "log_loss": float(log_loss(y_true, y_prob, labels=[0, 1])),
        "brier_score": float(brier_score_loss(y_true, y_prob)),
    }
    metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob)) if len(set(y_true.tolist())) > 1 else None
    return metrics


def calibration_curve_points(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> list[dict]:
    """Reliability-diagram data: for each probability bin, the mean predicted
    probability vs. the observed frequency of the positive class."""
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.digitize(y_prob, bins[1:-1])

    points = []
    for b in range(n_bins):
        mask = bin_ids == b
        if not mask.any():
            continue
        points.append(
            {
                "bin_start": float(bins[b]),
                "bin_end": float(bins[b + 1]),
                "predicted_mean": float(y_prob[mask].mean()),
                "observed_rate": float(y_true[mask].mean()),
                "count": int(mask.sum()),
            }
        )
    return points
