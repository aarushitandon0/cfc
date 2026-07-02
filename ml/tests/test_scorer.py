from ml.scorer import compute_centre_metrics, score_centres

THRESHOLDS = {"M01": 14}


def _log(date: str, units: float, consumption: float, attendance: bool, occupancy: float, test_ok: bool) -> dict:
    return {
        "log_date": date,
        "stock_snapshot": [{"medicine_id": "M01", "units_in_stock": units, "avg_daily_consumption": consumption}],
        "doctor_attendance": attendance,
        "bed_occupancy_pct": occupancy,
        "test_kits_available": test_ok,
    }


def test_compute_centre_metrics_well_stocked_centre():
    logs = [_log(f"2026-01-{d:02d}", units=200, consumption=5, attendance=True, occupancy=30, test_ok=True) for d in range(1, 15)]
    metrics = compute_centre_metrics(logs, THRESHOLDS)
    assert metrics["stock_availability"] == 1.0
    assert metrics["attendance_rate"] == 1.0
    assert metrics["test_availability"] == 1.0


def test_compute_centre_metrics_struggling_centre():
    logs = [_log(f"2026-01-{d:02d}", units=10, consumption=5, attendance=False, occupancy=95, test_ok=False) for d in range(1, 15)]
    metrics = compute_centre_metrics(logs, THRESHOLDS)
    # 10/5 = 2 days remaining vs 14-day threshold -> low ratio
    assert metrics["stock_availability"] < 0.2
    assert metrics["attendance_rate"] == 0.0
    assert metrics["bed_availability"] < 0.1
    assert metrics["test_availability"] == 0.0


def test_score_centres_ranks_struggling_centre_lower():
    good_logs = [_log(f"2026-01-{d:02d}", units=200, consumption=5, attendance=True, occupancy=30, test_ok=True) for d in range(1, 15)]
    bad_logs = [_log(f"2026-01-{d:02d}", units=10, consumption=5, attendance=False, occupancy=95, test_ok=False) for d in range(1, 15)]
    mid_logs = [_log(f"2026-01-{d:02d}", units=70, consumption=5, attendance=True, occupancy=50, test_ok=True) for d in range(1, 15)]

    metrics_by_centre = {
        "good": compute_centre_metrics(good_logs, THRESHOLDS),
        "bad": compute_centre_metrics(bad_logs, THRESHOLDS),
        "mid": compute_centre_metrics(mid_logs, THRESHOLDS),
    }
    scores = score_centres(metrics_by_centre)

    assert scores["good"]["health_score"] > scores["mid"]["health_score"] > scores["bad"]["health_score"]
    assert 0 <= scores["bad"]["health_score"] <= 100
    assert 0 <= scores["good"]["health_score"] <= 100
    # must be a plain float, not numpy.float64 - otherwise f-string interpolation
    # (e.g. in alert message drafting) renders it as "np.float64(27.9)"
    assert type(scores["good"]["health_score"]) is float


def test_score_centres_requires_multiple_centres():
    try:
        score_centres({"only_one": {"stock_availability": 1, "attendance_rate": 1, "bed_availability": 1, "test_availability": 1}})
        assert False, "expected ValueError"
    except ValueError:
        pass
