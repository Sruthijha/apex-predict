#!/bin/sh
# Container startup: builds the data/ML pipeline on first run (persisted to
# a volume so restarts are instant), then always migrates the DB schema,
# seeds/re-seeds reference data, and starts the API.
set -e

DATA_DIR="${DATA_DIR:-/app/data}"

if [ ! -f "$DATA_DIR/models/model_registry.json" ]; then
  echo "No trained models found - running the full pipeline once (ingest, features, train)..."
  DATA_DIR="$DATA_DIR" ./scripts/run_pipeline.sh
else
  echo "Found existing trained models - skipping ingestion/training."
  alembic upgrade head
  python -m scripts.seed_db --data-dir "$DATA_DIR/processed"
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
