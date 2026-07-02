"""Reference data for the fictional district used to generate synthetic data:
centre roster, medicine catalog, and the parameters that drive realistic
daily-log generation (seasonality, consumption rates, dropout probabilities)."""

from __future__ import annotations

DISTRICT_NAME = "Raighar District"

# 15 PHCs/CHCs spread across 4 zones, with varying bed capacity reflecting
# real-world PHC (smaller, no beds focus) vs CHC (larger, more beds) differences.
CENTRES = [
    {"centre_id": "C01", "name": "Ambapur PHC", "type": "PHC", "district_zone": "North", "lat": 21.62, "lng": 83.41, "bed_capacity": 6},
    {"centre_id": "C02", "name": "Bansipur PHC", "type": "PHC", "district_zone": "North", "lat": 21.68, "lng": 83.52, "bed_capacity": 6},
    {"centre_id": "C03", "name": "Raighar CHC", "type": "CHC", "district_zone": "North", "lat": 21.71, "lng": 83.47, "bed_capacity": 30},
    {"centre_id": "C04", "name": "Devgaon PHC", "type": "PHC", "district_zone": "North", "lat": 21.58, "lng": 83.38, "bed_capacity": 4},
    {"centre_id": "C05", "name": "Kantapalli PHC", "type": "PHC", "district_zone": "East", "lat": 21.49, "lng": 83.71, "bed_capacity": 8},
    {"centre_id": "C06", "name": "Salepada CHC", "type": "CHC", "district_zone": "East", "lat": 21.44, "lng": 83.66, "bed_capacity": 25},
    {"centre_id": "C07", "name": "Telinpada PHC", "type": "PHC", "district_zone": "East", "lat": 21.52, "lng": 83.78, "bed_capacity": 6},
    {"centre_id": "C08", "name": "Hatibari PHC", "type": "PHC", "district_zone": "South", "lat": 21.21, "lng": 83.49, "bed_capacity": 5},
    {"centre_id": "C09", "name": "Madhopur CHC", "type": "CHC", "district_zone": "South", "lat": 21.15, "lng": 83.55, "bed_capacity": 28},
    {"centre_id": "C10", "name": "Sundargarh PHC", "type": "PHC", "district_zone": "South", "lat": 21.18, "lng": 83.42, "bed_capacity": 6},
    {"centre_id": "C11", "name": "Pathargaon PHC", "type": "PHC", "district_zone": "South", "lat": 21.25, "lng": 83.61, "bed_capacity": 4},
    {"centre_id": "C12", "name": "Birpur PHC", "type": "PHC", "district_zone": "West", "lat": 21.55, "lng": 83.19, "bed_capacity": 6},
    {"centre_id": "C13", "name": "Lakhanpur CHC", "type": "CHC", "district_zone": "West", "lat": 21.49, "lng": 83.12, "bed_capacity": 22},
    {"centre_id": "C14", "name": "Nuagaon PHC", "type": "PHC", "district_zone": "West", "lat": 21.61, "lng": 83.08, "bed_capacity": 5},
    {"centre_id": "C15", "name": "Jharpalli PHC", "type": "PHC", "district_zone": "West", "lat": 21.57, "lng": 83.25, "bed_capacity": 6},
]

# 8 common PHC/CHC medicines with a stocking unit and the reorder threshold
# (days of stock remaining at which the forecaster should consider it at risk).
STOCK_ITEMS = [
    {"medicine_id": "M01", "name": "Paracetamol 500mg", "unit": "strip", "reorder_threshold_days": 10},
    {"medicine_id": "M02", "name": "ORS Sachets", "unit": "sachet", "reorder_threshold_days": 7},
    {"medicine_id": "M03", "name": "Amoxicillin 250mg", "unit": "strip", "reorder_threshold_days": 14},
    {"medicine_id": "M04", "name": "Iron Folic Acid Tablets", "unit": "strip", "reorder_threshold_days": 14},
    {"medicine_id": "M05", "name": "Oral Rehydration Zinc", "unit": "tablet", "reorder_threshold_days": 7},
    {"medicine_id": "M06", "name": "ASHA Antimalarial (ACT)", "unit": "kit", "reorder_threshold_days": 14},
    {"medicine_id": "M07", "name": "IV Fluids (Normal Saline)", "unit": "bottle", "reorder_threshold_days": 5},
    {"medicine_id": "M08", "name": "Diazepam Injection", "unit": "vial", "reorder_threshold_days": 21},
]

# Per-medicine baseline daily consumption (units/day) and noise, used to
# simulate stock depletion. CHCs (more footfall) consume roughly 2-3x a PHC.
MEDICINE_BASE_CONSUMPTION = {
    "M01": 8.0,
    "M02": 5.0,
    "M03": 4.0,
    "M04": 6.0,
    "M05": 3.0,
    "M06": 1.5,
    "M07": 2.0,
    "M08": 0.5,
}

NUM_HISTORY_DAYS = 90

# A handful of centres are deliberately scripted to be "problem centres" so the
# scorer/forecaster/recommender have something interesting to surface: chronic
# under-stocking, erratic doctor attendance, or persistent overcrowding.
PROBLEM_CENTRES = {
    "C04": "chronic_stockouts",       # small PHC, runs low on multiple medicines
    "C07": "erratic_attendance",       # doctor frequently absent
    "C11": "overcrowded",              # high footfall + bed occupancy
    "C14": "chronic_stockouts",
}

SURPLUS_CENTRES = {
    "C03": 1.6,   # large CHC, generally well-stocked -> good redistribution source
    "C09": 1.5,
    "C13": 1.4,
}
