from gemini.alert_drafter import draft_alert_message
from gemini.tests.fakes import FakeGenaiClient


def test_draft_alert_message_uses_given_severity_and_category_verbatim():
    fake = FakeGenaiClient(response_text="Stock of M04 at Devgaon PHC is critically low.")
    result = draft_alert_message(
        category="stockout",
        severity="high",
        centre_name="Devgaon PHC",
        source_metric={"medicine_id": "M04", "days_to_stockout": 0.0},
        client=fake,
    )

    assert result == "Stock of M04 at Devgaon PHC is critically low."
    sent_prompt = fake.models.last_call["contents"]
    assert "stockout" in sent_prompt
    assert "high" in sent_prompt
    # explicitly instructs Gemini not to reinterpret severity/category
    assert "do not change" in sent_prompt.lower()
