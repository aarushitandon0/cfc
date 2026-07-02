from ml.forecaster import forecast_footfall_7day, forecast_stockout, run_forecaster


def test_forecast_stockout_basic():
    # steady consumption of 5 units/day, 50 units left -> ~10 days
    result = forecast_stockout([5.0] * 10, current_stock=50.0)
    assert result["days_to_stockout"] is not None
    assert 8 <= result["days_to_stockout"] <= 12


def test_forecast_stockout_zero_consumption():
    result = forecast_stockout([0.0] * 5, current_stock=100.0)
    assert result["predicted_daily_consumption"] == 0.0
    assert result["days_to_stockout"] is None


def test_forecast_stockout_rising_consumption_shortens_runway():
    rising = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    flat = [4.0] * len(rising)
    rising_days = forecast_stockout(rising, current_stock=40.0)["days_to_stockout"]
    flat_days = forecast_stockout(flat, current_stock=40.0)["days_to_stockout"]
    assert rising_days < flat_days


def test_forecast_stockout_requires_min_history():
    try:
        forecast_stockout([5.0], current_stock=10.0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_forecast_footfall_7day_shape():
    series = [30, 32, 28, 35, 31, 20, 15] * 4  # 28 days, weekly pattern
    result = forecast_footfall_7day(series)
    assert len(result["daily_forecast"]) == 7
    assert all(v >= 0 for v in result["daily_forecast"])
    assert result["total_7day_forecast"] >= 0


def test_run_forecaster_end_to_end():
    logs = [
        {
            "centre_id": "C01",
            "log_date": f"2026-01-{day:02d}",
            "footfall_count": 30 + day,
            "stock_snapshot": [
                {"medicine_id": "M01", "units_in_stock": 100 - day * 5, "avg_daily_consumption": 5.0},
            ],
        }
        for day in range(1, 15)
    ]
    result = run_forecaster(logs)
    assert result["centre_id"] == "C01"
    assert len(result["stock_forecasts"]) == 1
    assert result["stock_forecasts"][0]["medicine_id"] == "M01"
    assert "days_to_stockout" in result["stock_forecasts"][0]
    assert len(result["footfall_forecast"]["daily_forecast"]) == 7
