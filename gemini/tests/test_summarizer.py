from gemini.summarizer import summarize_centre
from gemini.tests.fakes import FakeGenaiClient


def test_summarize_centre_prompt_contains_only_precomputed_numbers():
    fake = FakeGenaiClient(response_text="Devgaon PHC is at high risk.")
    result = summarize_centre(
        centre_name="Devgaon PHC",
        health_score=27.9,
        metric_breakdown={"stock_availability": -2.7, "attendance_rate": 0.5},
        stock_forecasts=[
            {"medicine_id": "M04", "days_to_stockout": 0.0},
            {"medicine_id": "M01", "days_to_stockout": 40.0},
        ],
        footfall_forecast={"total_7day_forecast": 234.3},
        language="Hindi",
        client=fake,
    )

    assert result == "Devgaon PHC is at high risk."
    sent_prompt = fake.models.last_call["contents"]
    assert "27.9" in sent_prompt
    assert "Hindi" in sent_prompt
    assert "M04" in sent_prompt and "0.0" in sent_prompt
    assert "234.3" in sent_prompt
    # the medicine well above the risk window should be excluded from the "at risk" list
    assert "M01" not in sent_prompt.split("Medicines at risk")[1].split("\n")[0]
    # explicitly instructs Gemini not to compute/recompute a score itself
    assert "do not invent numbers or recompute" in sent_prompt.lower()


def test_summarize_centre_handles_no_medicines_at_risk():
    fake = FakeGenaiClient(response_text="All good.")
    summarize_centre(
        centre_name="Raighar CHC",
        health_score=77.5,
        metric_breakdown={"stock_availability": 0.4},
        stock_forecasts=[{"medicine_id": "M01", "days_to_stockout": 120.0}],
        footfall_forecast={"total_7day_forecast": 611.7},
        client=fake,
    )
    sent_prompt = fake.models.last_call["contents"]
    assert "none" in sent_prompt
