"""Natural-language centre summaries in the admin's chosen language, generated
from precomputed ml/ outputs only (health score, z-score breakdown, stock
forecasts, footfall forecast) - never raw daily_logs.
"""

from __future__ import annotations

from gemini.client import generate_text

STOCKOUT_RISK_WINDOW_DAYS = 14


def summarize_centre(
    centre_name: str,
    health_score: float,
    metric_breakdown: dict[str, float],
    stock_forecasts: list[dict],
    footfall_forecast: dict,
    language: str = "English",
    *,
    client=None,
) -> str:
    at_risk_medicines = [
        (f["medicine_id"], f["days_to_stockout"])
        for f in stock_forecasts
        if f["days_to_stockout"] is not None and f["days_to_stockout"] < STOCKOUT_RISK_WINDOW_DAYS
    ]
    prompt = (
        f"You are writing a short status summary for a district health official, "
        f"in {language}. Use only the data below; do not invent numbers or recompute "
        f"any score or forecast.\n\n"
        f"Centre: {centre_name}\n"
        f"Health score (0-100, higher is better): {health_score}\n"
        f"Metric breakdown (z-scores vs district peers): {metric_breakdown}\n"
        f"Medicines at risk of stockout within {STOCKOUT_RISK_WINDOW_DAYS} days "
        f"(medicine_id, days_to_stockout): {at_risk_medicines or 'none'}\n"
        f"7-day footfall forecast (total visits): {footfall_forecast['total_7day_forecast']}\n\n"
        f"Write 3-4 plain sentences, no markdown, no bullet points."
    )
    return generate_text(prompt, client=client)
