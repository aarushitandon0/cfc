import pytest

from gemini.incident_tagger import extract_incident_tags
from gemini.tests.fakes import FakeGenaiClient


def test_extract_incident_tags_parses_json_response():
    fake = FakeGenaiClient(
        response_text=(
            '{"category": "stockout", "severity": "medium", '
            '"mentioned_medicine_names": ["Paracetamol"], '
            '"summary": "Staff reported low paracetamol stock."}'
        )
    )
    result = extract_incident_tags(
        "Paracetamol bahut kam hai, kal tak khatam ho jayega.", client=fake
    )

    assert result["category"] == "stockout"
    assert result["severity"] == "medium"
    assert "Paracetamol" in result["mentioned_medicine_names"]
    # the raw note text was sent to Gemini (this is the one module allowed to read it)
    assert "Paracetamol bahut kam hai" in fake.models.last_call["contents"]
    # requested as constrained JSON output
    assert fake.models.last_call["config"] == {"response_mime_type": "application/json"}


def test_extract_incident_tags_rejects_empty_text():
    with pytest.raises(ValueError):
        extract_incident_tags("   ", client=FakeGenaiClient())
