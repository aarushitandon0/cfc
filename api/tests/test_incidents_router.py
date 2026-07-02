import pytest
from fastapi.testclient import TestClient

from api.db.repository import get_repository
from api.main import app


@pytest.fixture(autouse=True)
def isolated_local_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_BACKEND", "local")
    monkeypatch.setenv("LOCAL_DB_PATH", str(tmp_path / "db.json"))
    get_repository.cache_clear()
    yield
    get_repository.cache_clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_submit_text_incident_creates_alert(client, monkeypatch):
    # Gemini tagging itself is covered by gemini/tests; here we monkeypatch it
    # so the incidents pipeline can be verified without a live API key.
    monkeypatch.setattr(
        "api.routers.incidents.extract_incident_tags",
        lambda translated_text: {
            "category": "stockout",
            "severity": "medium",
            "mentioned_medicine_names": ["Paracetamol"],
            "summary": "Staff reported low paracetamol stock.",
        },
    )

    response = client.post(
        "/incidents/text",
        json={"centre_id": "C04", "language_code": "hi-IN", "text": "दवाई कम है"},
    )
    assert response.status_code == 200
    alert = response.json()
    assert alert["centre_id"] == "C04"
    assert alert["category"] == "stockout"
    assert alert["severity"] == "medium"
    assert alert["status"] == "open"
    assert alert["message"] == "Staff reported low paracetamol stock."
    # original-language text preserved for staff-facing display, alongside
    # the English translation that was actually used for Gemini tagging
    assert alert["source_metric"]["original_text"] == "दवाई कम है"
    assert alert["source_metric"]["translated_text"] == "Medicine stock is low"

    listed = client.get("/alerts", params={"status": "open"}).json()
    assert any(a["alert_id"] == alert["alert_id"] for a in listed)


def test_submit_voice_incident_creates_alert(client, monkeypatch):
    monkeypatch.setattr(
        "api.routers.incidents.extract_incident_tags",
        lambda translated_text: {
            "category": "staffing",
            "severity": "high",
            "mentioned_medicine_names": [],
            "summary": "The doctor did not come in today.",
        },
    )

    response = client.post(
        "/incidents/voice",
        data={"centre_id": "C07", "language_code": "hi-IN"},
        files={"audio": ("note.txt", "डॉक्टर साहब आज नहीं आये".encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 200
    alert = response.json()
    assert alert["centre_id"] == "C07"
    assert alert["category"] == "staffing"
    assert alert["source_metric"]["original_text"] == "डॉक्टर साहब आज नहीं आये"
    assert alert["source_metric"]["translated_text"] == "The doctor did not come in today"


def test_submit_text_incident_falls_back_when_gemini_unavailable(client, monkeypatch):
    # without a configured GEMINI_API_KEY, extract_incident_tags raises - the
    # incident must still be captured as an untagged alert, not a 500
    def raise_no_key(translated_text):
        raise RuntimeError("GEMINI_API_KEY is not set")

    monkeypatch.setattr("api.routers.incidents.extract_incident_tags", raise_no_key)

    response = client.post(
        "/incidents/text",
        json={"centre_id": "C04", "language_code": "en-IN", "text": "Bed sheets are out of stock."},
    )
    assert response.status_code == 200
    alert = response.json()
    assert alert["category"] == "other"
    assert alert["severity"] == "medium"
    assert alert["message"] == "Bed sheets are out of stock."
