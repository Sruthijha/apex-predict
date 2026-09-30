#!/bin/sh
# Runs the full data + ML pipeline end to end: ingest -> preprocess ->
# features -> train -> feature importance -> DB migrate -> seed.
#
# Usage (from backend/): ./scripts/run_pipeline.sh [start_season] [end_season]
set -e

START_SEASON="${1:-2015}"
END_SEASON="${2:-2026}"
DATA_DIR="${DATA_DIR:-../data}"

echo "== 1/6: Ingesting raw data ($START_SEASON-$END_SEASON) =="
python -m ml.ingestion.pull_seasons --start "$START_SEASON" --end "$END_SEASON" --cache-dir "$DATA_DIR/raw"

echo "== 2/6: Building processed tables =="
python -m scripts.build_processed_data --start "$START_SEASON" --end "$END_SEASON" --out-dir "$DATA_DIR/processed"

echo "== 3/6: Building leakage-safe feature table =="
python -m scripts.build_features --data-dir "$DATA_DIR/processed"

echo "== 4/6: Training models (baselines, Linear/Logistic, RF, XGBoost) =="
python -m ml.training.train_all --feature-table "$DATA_DIR/processed/race_features.parquet" --output-dir "$DATA_DIR/models"

echo "== 5/6: Computing SHAP feature importance =="
python -m scripts.compute_feature_importance --feature-table "$DATA_DIR/processed/race_features.parquet" --model-dir "$DATA_DIR/models"

echo "== 6/6: Migrating and seeding the database =="
alembic upgrade head
python -m scripts.seed_db --data-dir "$DATA_DIR/processed"

echo "Pipeline complete."
