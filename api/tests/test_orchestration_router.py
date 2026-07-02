import pytest
from fastapi.testclient import TestClient

from api.db.repository import get_repository
from api.main import app
from data.seed.constants import CENTRES
from data.seed.generate_synthetic_data import generate


@pytest.fixture(autouse=True)
def seeded_local_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_BACKEND", "local")
    monkeypatch.setenv("LOCAL_DB_PATH", str(tmp_path / "db.json"))
    get_repository.cache_clear()

    repo = get_repository()
    dataset = generate()
    for centre in dataset["centres"]:
        repo.upsert_centre(centre)
    for item in dataset["stock_items"]:
        repo.upsert_stock_item(item)
    for log in dataset["daily_logs"]:
        repo.upsert_daily_log(log)

    yield
    get_repository.cache_clear()


@pytest.fixture(autouse=True)
def stub_gemini(monkeypatch):
    monkeypatch.setattr(
        "api.routers.orchestration.summarize_centre", lambda *a, **k: "stub summary"
    )
    monkeypatch.setattr(
        "api.routers.orchestration.draft_alert_message", lambda *a, **k: "stub alert message"
    )


@pytest.fixture
def client():
    return TestClient(app)


def test_orchestration_run_returns_full_district_payload(client):
    response = client.post("/orchestration/run")
    assert response.status_code == 200
    payload = response.json()

    assert len(payload["centres"]) == len(CENTRES)
    # centres are sorted by health score ascending (worst-first for triage)
    scores = [c["health_score"] for c in payload["centres"]]
    assert scores == sorted(scores)
    assert payload["alerts_created"]
    assert payload["recommendations_created"]
    assert all(c["summary"] == "stub summary" for c in payload["centres"])

    repo = get_repository()
    assert len(repo.list_alerts(status="open")) == len(payload["alerts_created"])
    assert len(repo.list_recommendations(status="pending")) == len(payload["recommendations_created"])


def test_orchestration_run_is_idempotent(client):
    first = client.post("/orchestration/run").json()
    second = client.post("/orchestration/run").json()

    assert first["alerts_created"]
    assert second["alerts_created"] == []
    assert second["recommendations_created"] == []
