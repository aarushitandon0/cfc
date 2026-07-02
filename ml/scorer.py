"""Composite z-score health scorer: per-centre metrics compared against the
district peer average across stock availability, attendance, bed
availability, and test-kit availability, mapped to a 0-100 health score.
Pure functions only - no Firestore/Gemini access.
"""

from __future__ import annotations

import statistics

from scipy.stats import norm

METRIC_NAMES = ("stock_availability", "attendance_rate", "bed_availability", "test_availability")


def _stock_availability_ratio(stock_snapshot: list[dict], reorder_thresholds: dict[str, int]) -> float:
    """Per-medicine ratio of actual days-of-stock-remaining to its reorder
    threshold, capped at 1.0 (fully stocked) and averaged across medicines.
    """
    ratios = []
    for snap in stock_snapshot:
        threshold = reorder_thresholds[snap["medicine_id"]]
        consumption = snap["avg_daily_consumption"]
        days_remaining = snap["units_in_stock"] / consumption if consumption > 0 else float("inf")
        ratios.append(min(1.0, days_remaining / threshold))
    return statistics.mean(ratios) if ratios else 1.0


def compute_centre_metrics(
    daily_logs_for_centre: list[dict], reorder_thresholds: dict[str, int], window_days: int = 14
) -> dict[str, float]:
    """Averages the 4 raw (0-1) metrics over the most recent `window_days` of logs."""
    recent = sorted(daily_logs_for_centre, key=lambda log: log["log_date"])[-window_days:]
    if not recent:
        raise ValueError("no daily logs provided for this centre")

    return {
        "stock_availability": statistics.mean(
            _stock_availability_ratio(log["stock_snapshot"], reorder_thresholds) for log in recent
        ),
        "attendance_rate": statistics.mean(1.0 if log["doctor_attendance"] else 0.0 for log in recent),
        "bed_availability": statistics.mean(
            max(0.0, 1 - log["bed_occupancy_pct"] / 100) for log in recent
        ),
        "test_availability": statistics.mean(
            1.0 if log["test_kits_available"] else 0.0 for log in recent
        ),
    }


def score_centres(metrics_by_centre: dict[str, dict[str, float]]) -> dict[str, dict]:
    """Computes a composite z-score and 0-100 health score per centre,
    relative to the district peer average for each of the 4 metrics.

    metrics_by_centre: {centre_id: {metric_name: value}}, as produced by
    compute_centre_metrics, for every centre being compared as one district.
    """
    if len(metrics_by_centre) < 2:
        raise ValueError("need at least 2 centres to compute peer z-scores")

    z_scores: dict[str, dict[str, float]] = {cid: {} for cid in metrics_by_centre}
    for name in METRIC_NAMES:
        values = [m[name] for m in metrics_by_centre.values()]
        mean = statistics.mean(values)
        stdev = statistics.pstdev(values) or 1e-9
        for centre_id, metrics in metrics_by_centre.items():
            z_scores[centre_id][name] = (metrics[name] - mean) / stdev

    results = {}
    for centre_id, metrics in metrics_by_centre.items():
        composite_z = statistics.mean(z_scores[centre_id].values())
        results[centre_id] = {
            "metrics": metrics,
            "z_scores": {k: round(v, 3) for k, v in z_scores[centre_id].items()},
            "composite_z": round(composite_z, 3),
            "health_score": float(round(norm.cdf(composite_z) * 100, 1)),
        }
    return results
