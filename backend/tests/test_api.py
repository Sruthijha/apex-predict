"""API endpoint tests.

These run against the app's actual configured SQLite DB and data
directories (an integration-test tier, not fully isolated unit tests) -
they assume `alembic upgrade head`, `scripts/seed_db.py`,
`scripts/build_processed_data.py`, and `ml/training/train_all.py` have
already been run, exactly as a real deployment would require. They skip
gracefully if that data isn't present (e.g. a fresh checkout before the
data pipeline has run).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.motorsport import Race

settings = get_settings()
_data_ready = Path(settings.processed_data_dir, "races.parquet").exists()
_models_ready = Path(settings.model_artifact_dir, "model_registry.json").exists()
_db_ready = False
if _data_ready:
    try:
        with SessionLocal() as session:
            _db_ready = session.query(Race).count() > 0
    except Exception:
        _db_ready = False

pytestmark = pytest.mark.skipif(
    not (_data_ready and _models_ready and _db_ready),
    reason="Requires seeded DB + processed data + trained models (see backend/README or DEPLOYMENT.md).",
)


@pytest.fixture(scope="module")
def client():
    from app.main import app

    return TestClient(app)


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_races(client: TestClient):
    response = client.get("/api/races")
    assert response.status_code == 200
    races = response.json()
    assert len(races) > 0
    assert "race_id" in races[0]
    assert "circuit" in races[0]


def test_upcoming_race(client: TestClient):
    response = client.get("/api/races/upcoming")
    assert response.status_code == 200
    assert response.json()["has_results"] is False


def test_get_race_not_found(client: TestClient):
    response = client.get("/api/races/1999-nonexistent")
    assert response.status_code == 404


def test_actual_results_for_upcoming_race_is_404(client: TestClient):
    upcoming = client.get("/api/races/upcoming").json()
    response = client.get(f"/api/races/{upcoming['race_id']}/results")
    assert response.status_code == 404


def test_actual_results_for_a_past_race_are_sorted_by_position(client: TestClient):
    response = client.get("/api/races/2024-r16-monza/results")
    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0
    assert body[0]["position"] == 1
    positions = [r["position"] for r in body]
    assert positions == sorted(positions)


def test_list_and_get_driver(client: TestClient):
    drivers = client.get("/api/drivers").json()
    assert len(drivers) > 0

    detail = client.get(f"/api/drivers/{drivers[0]['id']}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["wins"] >= 0
    assert body["podiums"] >= body["wins"]  # every win is also a podium


def test_get_driver_not_found(client: TestClient):
    response = client.get("/api/drivers/not_a_real_driver")
    assert response.status_code == 404


def test_list_constructors(client: TestClient):
    response = client.get("/api/constructors")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_list_circuits(client: TestClient):
    response = client.get("/api/circuits")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_prediction_for_upcoming_race_has_probabilities_summing_to_one(client: TestClient):
    upcoming = client.get("/api/races/upcoming").json()
    response = client.get(f"/api/predictions/{upcoming['race_id']}", params={"mode": "pre_weekend"})
    assert response.status_code == 200
    body = response.json()
    assert body["prediction_mode"] == "pre_weekend"
    win_total = sum(d["win_probability"] for d in body["drivers"])
    assert win_total == pytest.approx(1.0, abs=0.01)
    # sorted by predicted position ascending
    positions = [d["predicted_position"] for d in body["drivers"]]
    assert positions == sorted(positions)


def test_prediction_invalid_mode_returns_400(client: TestClient):
    upcoming = client.get("/api/races/upcoming").json()
    response = client.get(f"/api/predictions/{upcoming['race_id']}", params={"mode": "not_a_mode"})
    assert response.status_code == 400


def test_simulate_upcoming_race(client: TestClient):
    upcoming = client.get("/api/races/upcoming").json()
    response = client.post(
        f"/api/simulate/{upcoming['race_id']}",
        json={"n_simulations": 500, "seed": 1, "prediction_mode": "pre_weekend"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["n_simulations"] == 500
    assert len(body["most_common_podium"]) == 3
    assert len(set(body["most_common_podium"])) == 3


def test_model_metrics(client: TestClient):
    response = client.get("/api/model/metrics")
    assert response.status_code == 200
    body = response.json()
    assert len(body["modes"]) == 2
    for mode_metrics in body["modes"]:
        assert mode_metrics["position_test_metrics"]["mae"] > 0


def test_championship_projection(client: TestClient):
    response = client.get("/api/championship", params={"n_trials": 500})
    assert response.status_code == 200
    body = response.json()
    assert body["remaining_races"] > 0
    driver_total = sum(d["championship_win_probability"] for d in body["drivers"])
    assert driver_total == pytest.approx(1.0, abs=0.01)
    constructor_total = sum(c["championship_win_probability"] for c in body["constructors"])
    assert constructor_total == pytest.approx(1.0, abs=0.01)
    # every driver's projected final tally is at least their current points
    for d in body["drivers"]:
        assert d["expected_final_points"] >= d["current_points"]
