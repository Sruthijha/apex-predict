"""Shared core: race lineup -> leakage-safe live features -> position/DNF
predictions. Used by both the prediction endpoint (which also runs a fixed,
small simulation for its win/podium numbers) and the simulate endpoint
(which runs a user-chosen, larger simulation) - factored out so there is
exactly one place that builds the lineup and calls build_live_feature_rows.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.services.data_store import DataStore
from ml.inference.live_features import DriverEntry, build_live_feature_rows
from ml.inference.model_registry import ModeArtifacts, load_mode_artifacts
from ml.inference.predict import predict_positions_and_dnf


@dataclass(frozen=True)
class PreparedPrediction:
    season: int
    round: int
    predictions: pd.DataFrame  # driver_id, constructor_id, predicted_position, dnf_probability
    feature_rows: pd.DataFrame
    artifacts: ModeArtifacts


def _build_lineup(store: DataStore, season: int, round_: int, mode: str) -> list[DriverEntry]:
    actual_results = store.race_results[(store.race_results["season"] == season) & (store.race_results["round"] == round_)]
    actual_quali = store.qualifying_results[
        (store.qualifying_results["season"] == season) & (store.qualifying_results["round"] == round_)
    ]

    if not actual_results.empty:
        pairs = actual_results[["driver_id", "constructor_id"]].drop_duplicates()
        grid_by_driver = actual_results.set_index("driver_id")["grid"].to_dict()
    else:
        pairs = store.latest_lineup(season, round_)
        grid_by_driver = {}

    quali_grid_by_driver = dict(zip(actual_quali["driver_id"], actual_quali["position"]))

    lineup = []
    for row in pairs.itertuples(index=False):
        grid_position = None
        if mode == "post_qualifying":
            grid_position = quali_grid_by_driver.get(row.driver_id) or grid_by_driver.get(row.driver_id)
        lineup.append(DriverEntry(driver_id=row.driver_id, constructor_id=row.constructor_id, grid_position=grid_position))
    return lineup


def _exclude_target_race(store: DataStore, season: int, round_: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    def is_target(df: pd.DataFrame) -> pd.Series:
        return (df["season"] == season) & (df["round"] == round_)

    return (
        store.races[~is_target(store.races)],
        store.race_results[~is_target(store.race_results)],
        store.qualifying_results[~is_target(store.qualifying_results)],
    )


def prepare_prediction(store: DataStore, model_dir: str, race_id: str, mode: str) -> PreparedPrediction | None:
    row = store.find_race(race_id)
    if row is None:
        return None

    season, round_, circuit_id = int(row["season"]), int(row["round"]), row["circuit_id"]
    date_str = pd.Timestamp(row["date"]).strftime("%Y-%m-%d")

    lineup = _build_lineup(store, season, round_, mode)
    if not lineup:
        return None
    if mode == "post_qualifying" and all(e.grid_position is None for e in lineup):
        return None  # qualifying hasn't happened yet

    hist_races, hist_results, hist_quali = _exclude_target_race(store, season, round_)
    feature_rows = build_live_feature_rows(
        hist_results, hist_races, hist_quali, store.drivers, season, round_, date_str, circuit_id, lineup
    )
    if feature_rows.empty:
        return None

    artifacts = load_mode_artifacts(model_dir, mode)
    predictions = predict_positions_and_dnf(artifacts, feature_rows).sort_values("predicted_position").reset_index(drop=True)

    return PreparedPrediction(
        season=season, round=round_, predictions=predictions, feature_rows=feature_rows, artifacts=artifacts
    )
