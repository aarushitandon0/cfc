"""Single endpoint chaining forecast -> score -> recommend -> Gemini
summarize/draft, returning the full district payload the admin dashboard
renders in one call. Also implements the brief's explicit requirement to
"automatically flag underperforming or under-resourced centres to district
administrators" - stockout risk and low health scores become system-generated
Alerts, with Gemini only drafting their message text.

Gemini calls are best-effort: if GEMINI_API_KEY isn't configured (or a call
fails), the numeric pipeline still completes and a templated fallback message
is used instead of the LLM-drafted one, so the dashboard never goes blank for
a Gemini-layer problem alone.
"""

from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, Query

from api.db.repository import get_repository
from gemini.alert_drafter import draft_alert_message
from gemini.summarizer import summarize_centre
from ml.forecaster import run_forecaster
from ml.recommender import recommend_redistribution
from ml.scorer import compute_centre_metrics, score_centres

router = APIRouter(prefix="/orchestration", tags=["orchestration"])
logger = logging.getLogger(__name__)

LOW_HEALTH_SCORE_THRESHOLD = 30.0
STOCKOUT_HIGH_SEVERITY_RATIO = 0.5  # below half the reorder threshold -> "high"
METRICS_WINDOW_DAYS = 14


def _existing_open_alert_keys(repo) -> set[tuple]:
    """(centre_id, category, medicine_id) for currently-open alerts, used to
    avoid re-raising the same alert on every orchestration run."""
    keys = set()
    for alert in repo.list_alerts(status="open"):
        medicine_id = alert.get("source_metric", {}).get("medicine_id")
        keys.add((alert["centre_id"], alert["category"], medicine_id))
    return keys


def _existing_pending_recommendation_keys(repo) -> set[tuple]:
    """(medicine_id, from_centre_id, to_centre_id) for currently-pending
    recommendations, used to avoid re-suggesting the same transfer on every run."""
    return {
        (rec["medicine_id"], rec["from_centre_id"], rec["to_centre_id"])
        for rec in repo.list_recommendations(status="pending")
    }


def _draft_message(category: str, severity: str, centre_name: str, source_metric: dict, language: str) -> str:
    try:
        return draft_alert_message(category, severity, centre_name, source_metric, language=language)
    except Exception:
        logger.warning("Gemini alert drafting failed; using templated fallback", exc_info=True)
        return f"[{severity.upper()}] {category} flagged at {centre_name}: {source_metric}"


def _summarize(centre_name: str, health_score: float, z_scores: dict, stock_forecasts: list[dict], footfall_forecast: dict, language: str) -> str:
    try:
        return summarize_centre(centre_name, health_score, z_scores, stock_forecasts, footfall_forecast, language=language)
    except Exception:
        logger.warning("Gemini summarization failed; using templated fallback", exc_info=True)
        return f"{centre_name} has a health score of {health_score}/100 (Gemini summary unavailable)."


def run_orchestration(language: str = "English") -> dict:
    repo = get_repository()
    centres = {c["centre_id"]: c for c in repo.list_centres()}
    stock_items = repo.list_stock_items()
    thresholds = {item["medicine_id"]: item["reorder_threshold_days"] for item in stock_items}

    logs_by_centre: dict[str, list[dict]] = {}
    for log in repo.list_daily_logs():
        logs_by_centre.setdefault(log["centre_id"], []).append(log)

    # 1. forecast
    forecasts_by_centre = {
        centre_id: run_forecaster(logs) for centre_id, logs in logs_by_centre.items() if logs
    }

    # 2. score
    metrics_by_centre = {
        centre_id: compute_centre_metrics(logs, thresholds, window_days=METRICS_WINDOW_DAYS)
        for centre_id, logs in logs_by_centre.items()
        if logs
    }
    scores_by_centre = score_centres(metrics_by_centre) if len(metrics_by_centre) >= 2 else {}

    # 3. recommend (per medicine, using each centre's latest snapshot)
    new_recommendations = []
    for medicine_id in thresholds:
        centre_states = []
        for centre_id, logs in logs_by_centre.items():
            if not logs or centre_id not in centres:
                continue
            latest = max(logs, key=lambda log: log["log_date"])
            snap = next((s for s in latest["stock_snapshot"] if s["medicine_id"] == medicine_id), None)
            if snap is None:
                continue
            centre_states.append(
                {
                    "centre_id": centre_id,
                    "lat": centres[centre_id]["lat"],
                    "lng": centres[centre_id]["lng"],
                    "units_in_stock": snap["units_in_stock"],
                    "avg_daily_consumption": snap["avg_daily_consumption"],
                    "reorder_threshold_days": thresholds[medicine_id],
                }
            )
        new_recommendations.extend(recommend_redistribution(medicine_id, centre_states))

    existing_recommendation_keys = _existing_pending_recommendation_keys(repo)
    new_recommendations = [
        rec
        for rec in new_recommendations
        if (rec["medicine_id"], rec["from_centre_id"], rec["to_centre_id"]) not in existing_recommendation_keys
    ]

    today = date.today().isoformat()
    for rec in new_recommendations:
        # deterministic, not random: re-running orchestration overwrites the
        # same recommendation instead of risking a duplicate under concurrent
        # requests (e.g. React StrictMode firing the initial load twice)
        rec["recommendation_id"] = f"auto-{rec['medicine_id']}-{rec['from_centre_id']}-{rec['to_centre_id']}"
        rec["status"] = "pending"
        rec["created_at"] = today
        repo.upsert_recommendation(rec)

    # 4. Gemini: per-centre summaries + auto-flagged alerts for risk conditions
    existing_alert_keys = _existing_open_alert_keys(repo)
    new_alerts = []
    centre_payloads = []

    for centre_id, forecast in forecasts_by_centre.items():
        centre = centres[centre_id]
        score = scores_by_centre.get(centre_id)
        health_score = score["health_score"] if score else None
        z_scores = score["z_scores"] if score else {}

        summary = _summarize(
            centre["name"], health_score or 0.0, z_scores, forecast["stock_forecasts"], forecast["footfall_forecast"], language
        )

        for stock_forecast in forecast["stock_forecasts"]:
            days_left = stock_forecast["days_to_stockout"]
            medicine_id = stock_forecast["medicine_id"]
            threshold = thresholds[medicine_id]
            if days_left is None or days_left >= threshold:
                continue
            if (centre_id, "stockout", medicine_id) in existing_alert_keys:
                continue
            severity = "high" if days_left < threshold * STOCKOUT_HIGH_SEVERITY_RATIO else "medium"
            source_metric = {"medicine_id": medicine_id, "days_to_stockout": days_left}
            new_alerts.append(
                {
                    # deterministic, not random - see recommendation_id comment above
                    "alert_id": f"auto-{centre_id}-stockout-{medicine_id}",
                    "centre_id": centre_id,
                    "created_at": today,
                    "category": "stockout",
                    "severity": severity,
                    "status": "open",
                    "message": _draft_message("stockout", severity, centre["name"], source_metric, language),
                    "source_metric": source_metric,
                }
            )

        if health_score is not None and health_score < LOW_HEALTH_SCORE_THRESHOLD:
            if (centre_id, "underperforming", None) not in existing_alert_keys:
                source_metric = {"health_score": health_score, "z_scores": z_scores}
                new_alerts.append(
                    {
                        "alert_id": f"auto-{centre_id}-underperforming-na",
                        "centre_id": centre_id,
                        "created_at": today,
                        "category": "underperforming",
                        "severity": "high",
                        "status": "open",
                        "message": _draft_message(
                            "underperforming", "high", centre["name"], source_metric, language
                        ),
                        "source_metric": source_metric,
                    }
                )

        centre_payloads.append(
            {
                "centre_id": centre_id,
                "name": centre["name"],
                "type": centre["type"],
                "district_zone": centre["district_zone"],
                "health_score": health_score,
                "metrics": score["metrics"] if score else None,
                "z_scores": z_scores,
                "stock_forecasts": forecast["stock_forecasts"],
                "footfall_forecast": forecast["footfall_forecast"],
                "summary": summary,
            }
        )

    for alert in new_alerts:
        repo.upsert_alert(alert)

    return {
        "generated_at": today,
        "language": language,
        "centres": sorted(centre_payloads, key=lambda c: (c["health_score"] is None, c["health_score"] or 0)),
        "alerts_created": new_alerts,
        "recommendations_created": new_recommendations,
    }


@router.post("/run")
def run(language: str = Query(default="English")) -> dict:
    return run_orchestration(language=language)
