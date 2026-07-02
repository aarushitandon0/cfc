"""Greedy redistribution matcher: pairs surplus-stock centres with
predicted-deficit centres for a given medicine, ranked by urgency then
distance. Pure functions only - no Firestore/Gemini access.
"""

from __future__ import annotations

import math

SURPLUS_MULTIPLE = 2.0  # a centre counts as "surplus" above 2x its reorder threshold
REFILL_TARGET_MULTIPLE = 1.0  # deficits are refilled up to 1x their reorder threshold


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    earth_radius_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * earth_radius_km * math.asin(math.sqrt(a))


def recommend_redistribution(medicine_id: str, centre_states: list[dict]) -> list[dict]:
    """Greedily matches centres in deficit to the nearest centre with surplus,
    for one medicine.

    centre_states: [{"centre_id", "lat", "lng", "units_in_stock",
                      "avg_daily_consumption", "reorder_threshold_days"}, ...]
    A centre is in deficit if its days-of-stock-remaining is below its reorder
    threshold; it has surplus once that figure exceeds SURPLUS_MULTIPLE x
    threshold. Most-urgent deficits (lowest days remaining) are served first.
    """
    enriched = [
        {
            **c,
            "days_remaining": (
                c["units_in_stock"] / c["avg_daily_consumption"]
                if c["avg_daily_consumption"] > 0
                else float("inf")
            ),
        }
        for c in centre_states
    ]

    deficits = sorted(
        (c for c in enriched if c["days_remaining"] < c["reorder_threshold_days"]),
        key=lambda c: c["days_remaining"],
    )
    surplus_pool = {
        c["centre_id"]: dict(c)
        for c in enriched
        if c["days_remaining"] >= c["reorder_threshold_days"] * SURPLUS_MULTIPLE
    }

    recommendations = []
    for deficit in deficits:
        target_stock = (
            deficit["reorder_threshold_days"] * deficit["avg_daily_consumption"] * REFILL_TARGET_MULTIPLE
        )
        needed_units = target_stock - deficit["units_in_stock"]
        if needed_units <= 0 or not surplus_pool:
            continue

        urgency_score = round(
            max(0.0, min(100.0, 100 * (1 - deficit["days_remaining"] / deficit["reorder_threshold_days"]))),
            1,
        )

        candidates = sorted(
            surplus_pool.values(),
            key=lambda s: haversine_km(deficit["lat"], deficit["lng"], s["lat"], s["lng"]),
        )
        for surplus in candidates:
            available = (
                surplus["units_in_stock"]
                - surplus["reorder_threshold_days"] * surplus["avg_daily_consumption"] * SURPLUS_MULTIPLE
            )
            if available <= 0:
                continue

            transfer_units = round(min(needed_units, available), 1)
            if transfer_units <= 0:
                continue

            recommendations.append(
                {
                    "medicine_id": medicine_id,
                    "from_centre_id": surplus["centre_id"],
                    "to_centre_id": deficit["centre_id"],
                    "suggested_units": transfer_units,
                    "urgency_score": urgency_score,
                    "distance_km": round(
                        haversine_km(deficit["lat"], deficit["lng"], surplus["lat"], surplus["lng"]), 1
                    ),
                }
            )
            surplus_pool[surplus["centre_id"]]["units_in_stock"] -= transfer_units
            needed_units -= transfer_units
            if needed_units <= 0:
                break

    recommendations.sort(key=lambda r: (-r["urgency_score"], r["distance_km"]))
    return recommendations
