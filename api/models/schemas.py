"""Pydantic schemas for the 5 Firestore collections. Single source of truth
for both the API layer and the synthetic data generator/seeder."""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class CentreType(str, Enum):
    PHC = "PHC"
    CHC = "CHC"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AlertStatus(str, Enum):
    open = "open"
    resolved = "resolved"


class RecommendationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


# --- centres ---------------------------------------------------------------

class Centre(BaseModel):
    centre_id: str
    name: str
    type: CentreType
    district_zone: str
    lat: float
    lng: float
    bed_capacity: int = Field(gt=0)


# --- stock_items -------------------------------------------------------------

class StockItem(BaseModel):
    medicine_id: str
    name: str
    unit: str  # e.g. "strip", "vial", "bottle"
    reorder_threshold_days: int = Field(
        gt=0, description="Days of stock remaining at which a reorder alert should fire"
    )


# --- daily_logs --------------------------------------------------------------

class MedicineStockSnapshot(BaseModel):
    medicine_id: str
    units_in_stock: float = Field(ge=0)
    avg_daily_consumption: float = Field(
        ge=0, description="Rolling average daily consumption used as the forecaster's baseline"
    )


class DailyLog(BaseModel):
    log_id: str  # f"{centre_id}_{log_date.isoformat()}"
    centre_id: str
    log_date: date
    stock_snapshot: list[MedicineStockSnapshot]
    footfall_count: int = Field(ge=0)
    bed_occupancy_pct: float = Field(ge=0, le=100)
    doctor_attendance: bool
    test_kits_available: bool


# --- alerts --------------------------------------------------------------

class Alert(BaseModel):
    alert_id: str
    centre_id: str
    created_at: date
    category: str  # "stockout" | "footfall" | "bed_capacity" | "attendance" | "test_availability"
    severity: Severity
    status: AlertStatus = AlertStatus.open
    message: str  # human-readable, may be Gemini-drafted
    source_metric: dict = Field(
        default_factory=dict, description="Raw numeric values that triggered the alert"
    )


# --- redistribution_recommendations -------------------------------------------

class RedistributionRecommendation(BaseModel):
    recommendation_id: str
    medicine_id: str
    from_centre_id: str
    to_centre_id: str
    suggested_units: float = Field(gt=0)
    urgency_score: float = Field(ge=0, le=100)
    distance_km: float = Field(ge=0)
    status: RecommendationStatus = RecommendationStatus.pending
    created_at: date
