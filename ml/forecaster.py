"""Statistical forecasting: per-medicine days-to-stockout and 7-day-ahead
footfall, both via exponential smoothing (statsmodels). Pure functions only -
no Firestore/Gemini access. Gemini never sees these numbers until after
they're computed here.
"""

from __future__ import annotations

import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing

MIN_HISTORY_FOR_SMOOTHING = 2
MIN_HISTORY_FOR_SEASONAL_FOOTFALL = 21  # >=3 full weekly cycles
FOOTFALL_SEASONAL_PERIOD = 7
FOOTFALL_FORECAST_HORIZON_DAYS = 7


def forecast_stockout(consumption_series: list[float], current_stock: float) -> dict:
    """Forecasts days-to-stockout for one medicine at one centre.

    consumption_series: chronological daily consumption (units/day), oldest
    first. Smoothed with simple exponential smoothing to get a stabilized
    next-day consumption estimate, which is then divided into current stock.
    """
    if len(consumption_series) < MIN_HISTORY_FOR_SMOOTHING:
        raise ValueError("need at least 2 days of consumption history to forecast")

    series = np.asarray(consumption_series, dtype=float)
    model = SimpleExpSmoothing(series, initialization_method="estimated").fit()
    predicted_daily_consumption = max(0.0, float(model.forecast(1)[0]))

    if predicted_daily_consumption <= 1e-6:
        return {"predicted_daily_consumption": 0.0, "days_to_stockout": None}

    days_to_stockout = current_stock / predicted_daily_consumption
    return {
        "predicted_daily_consumption": round(predicted_daily_consumption, 2),
        "days_to_stockout": round(days_to_stockout, 1),
    }


def forecast_footfall_7day(footfall_series: list[int]) -> dict:
    """7-day-ahead footfall forecast. Uses Holt-Winters with weekly seasonality
    once there's enough history (>=21 days); falls back to simple exponential
    smoothing otherwise so the forecaster still works on short histories.
    """
    series = np.asarray(footfall_series, dtype=float)

    if len(series) >= MIN_HISTORY_FOR_SEASONAL_FOOTFALL:
        model = ExponentialSmoothing(
            series,
            trend="add",
            seasonal="add",
            seasonal_periods=FOOTFALL_SEASONAL_PERIOD,
            initialization_method="estimated",
        ).fit()
    else:
        model = SimpleExpSmoothing(series, initialization_method="estimated").fit()

    forecast = np.clip(model.forecast(FOOTFALL_FORECAST_HORIZON_DAYS), 0, None)
    return {
        "daily_forecast": [round(float(x), 1) for x in forecast],
        "total_7day_forecast": round(float(forecast.sum()), 1),
    }


def run_forecaster(daily_logs_for_centre: list[dict]) -> dict:
    """Runs the full Forecaster step for one centre: a stock forecast per
    medicine present in its logs, plus a 7-day footfall forecast.

    daily_logs_for_centre: that centre's daily_logs, any order (sorted here).
    """
    logs = sorted(daily_logs_for_centre, key=lambda log: log["log_date"])
    if not logs:
        raise ValueError("no daily logs provided for this centre")

    medicine_ids = [snap["medicine_id"] for snap in logs[-1]["stock_snapshot"]]
    stock_forecasts = []
    for medicine_id in medicine_ids:
        consumption_series = [
            next(s for s in log["stock_snapshot"] if s["medicine_id"] == medicine_id)[
                "avg_daily_consumption"
            ]
            for log in logs
        ]
        current_stock = next(
            s for s in logs[-1]["stock_snapshot"] if s["medicine_id"] == medicine_id
        )["units_in_stock"]
        forecast = forecast_stockout(consumption_series, current_stock)
        stock_forecasts.append({"medicine_id": medicine_id, "current_stock": current_stock, **forecast})

    footfall_series = [log["footfall_count"] for log in logs]
    footfall_forecast = forecast_footfall_7day(footfall_series)

    return {
        "centre_id": logs[-1]["centre_id"],
        "stock_forecasts": stock_forecasts,
        "footfall_forecast": footfall_forecast,
    }
