"""Generates 90 days of realistic daily_logs for every centre in the fictional
Raighar District, plus the static centres/stock_items collections.

Pure stdlib (random) - no numpy/pandas dependency here so the generator can
run anywhere without installing the ML stack. Writes JSON to data/seed/output/.

Run: python -m data.seed.generate_synthetic_data
"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

from data.seed.constants import (
    CENTRES,
    MEDICINE_BASE_CONSUMPTION,
    NUM_HISTORY_DAYS,
    PROBLEM_CENTRES,
    STOCK_ITEMS,
    SURPLUS_CENTRES,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
SEED = 42
TODAY = date.today()


def _centre_size_multiplier(centre: dict) -> float:
    """CHCs see roughly 2.5x the footfall/consumption of a PHC."""
    return 2.6 if centre["type"] == "CHC" else 1.0


def _simulate_stock_series(
    rng: random.Random, centre_id: str, medicine_id: str, base_consumption: float, days: int
) -> list[dict]:
    """Simulate a daily stock snapshot with periodic resupply and gradual depletion.

    Problem centres (chronic_stockouts) get longer resupply gaps and higher
    consumption variance so they plausibly breach reorder thresholds.
    """
    profile = PROBLEM_CENTRES.get(centre_id)
    surplus_factor = SURPLUS_CENTRES.get(centre_id, 1.0)

    resupply_interval = rng.randint(12, 18)
    if profile == "chronic_stockouts":
        resupply_interval = rng.randint(20, 28)

    target_days_of_stock = rng.uniform(18, 26) * surplus_factor
    if profile == "chronic_stockouts":
        target_days_of_stock *= 0.55

    stock = base_consumption * target_days_of_stock
    days_since_resupply = rng.randint(0, resupply_interval - 1)

    series: list[dict] = []
    consumption_window: list[float] = []

    for day_idx in range(days):
        weekday = (TODAY - timedelta(days=days - day_idx)).weekday()
        weekend_dip = 0.7 if weekday in (5, 6) else 1.0
        noise = rng.uniform(0.8, 1.2)
        consumption = max(0.0, base_consumption * weekend_dip * noise)

        if profile == "chronic_stockouts":
            consumption *= rng.uniform(1.05, 1.25)

        stock = max(0.0, stock - consumption)
        days_since_resupply += 1

        if days_since_resupply >= resupply_interval:
            restock_amount = base_consumption * target_days_of_stock
            if profile == "chronic_stockouts" and rng.random() < 0.3:
                restock_amount *= 0.4  # a delayed/partial resupply truck
            stock += restock_amount
            days_since_resupply = 0

        consumption_window.append(consumption)
        if len(consumption_window) > 7:
            consumption_window.pop(0)
        avg_consumption = sum(consumption_window) / len(consumption_window)

        series.append(
            {
                "medicine_id": medicine_id,
                "units_in_stock": round(stock, 1),
                "avg_daily_consumption": round(avg_consumption, 2),
            }
        )
    return series


def _simulate_footfall(rng: random.Random, centre: dict, day_idx: int, days: int) -> int:
    base = 35 * _centre_size_multiplier(centre)
    weekday = (TODAY - timedelta(days=days - day_idx)).weekday()
    weekly_seasonality = {0: 1.25, 1: 1.1, 2: 1.0, 3: 1.0, 4: 1.05, 5: 0.75, 6: 0.5}[weekday]
    profile = PROBLEM_CENTRES.get(centre["centre_id"])
    overcrowd_factor = 1.6 if profile == "overcrowded" else 1.0
    noise = rng.uniform(0.85, 1.15)
    return max(0, round(base * weekly_seasonality * overcrowd_factor * noise))


def _simulate_bed_occupancy(rng: random.Random, centre: dict, footfall: int) -> float:
    profile = PROBLEM_CENTRES.get(centre["centre_id"])
    capacity = centre["bed_capacity"]
    expected_admissions = footfall * 0.08 * (1.5 if profile == "overcrowded" else 1.0)
    occupancy_pct = min(100.0, (expected_admissions / capacity) * 100 * rng.uniform(0.7, 1.3))
    return round(occupancy_pct, 1)


def _simulate_attendance(rng: random.Random, centre_id: str) -> bool:
    profile = PROBLEM_CENTRES.get(centre_id)
    present_probability = 0.65 if profile == "erratic_attendance" else 0.94
    return rng.random() < present_probability


def _simulate_test_availability(rng: random.Random, centre_id: str) -> bool:
    profile = PROBLEM_CENTRES.get(centre_id)
    available_probability = 0.75 if profile == "chronic_stockouts" else 0.95
    return rng.random() < available_probability


def generate() -> dict:
    rng = random.Random(SEED)
    daily_logs: list[dict] = []

    for centre in CENTRES:
        size_mult = _centre_size_multiplier(centre)
        stock_series_by_medicine = {
            item["medicine_id"]: _simulate_stock_series(
                rng,
                centre["centre_id"],
                item["medicine_id"],
                MEDICINE_BASE_CONSUMPTION[item["medicine_id"]] * size_mult,
                NUM_HISTORY_DAYS,
            )
            for item in STOCK_ITEMS
        }

        for day_idx in range(NUM_HISTORY_DAYS):
            log_date = TODAY - timedelta(days=NUM_HISTORY_DAYS - day_idx)
            footfall = _simulate_footfall(rng, centre, day_idx, NUM_HISTORY_DAYS)
            daily_logs.append(
                {
                    "log_id": f"{centre['centre_id']}_{log_date.isoformat()}",
                    "centre_id": centre["centre_id"],
                    "log_date": log_date.isoformat(),
                    "stock_snapshot": [
                        stock_series_by_medicine[item["medicine_id"]][day_idx]
                        for item in STOCK_ITEMS
                    ],
                    "footfall_count": footfall,
                    "bed_occupancy_pct": _simulate_bed_occupancy(rng, centre, footfall),
                    "doctor_attendance": _simulate_attendance(rng, centre["centre_id"]),
                    "test_kits_available": _simulate_test_availability(rng, centre["centre_id"]),
                }
            )

    return {"centres": CENTRES, "stock_items": STOCK_ITEMS, "daily_logs": daily_logs}


def main() -> None:
    dataset = generate()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for key, records in dataset.items():
        path = OUTPUT_DIR / f"{key}.json"
        path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        print(f"wrote {len(records)} records to {path}")


if __name__ == "__main__":
    main()
