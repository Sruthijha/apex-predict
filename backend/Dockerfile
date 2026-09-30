FROM python:3.11-slim

# libgomp1: OpenMP runtime required by XGBoost at import time.
# curl: used by the container healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x scripts/run_pipeline.sh scripts/docker-entrypoint.sh

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DATA_CACHE_DIR=/app/data/raw \
    PROCESSED_DATA_DIR=/app/data/processed \
    MODEL_ARTIFACT_DIR=/app/data/models

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
