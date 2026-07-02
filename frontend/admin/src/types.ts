// Mirrors api/models/schemas.py and the orchestration payload shape.

export interface Centre {
  centre_id: string
  name: string
  type: "PHC" | "CHC"
  district_zone: string
  lat: number
  lng: number
  bed_capacity: number
}

export interface StockItem {
  medicine_id: string
  name: string
  unit: string
  reorder_threshold_days: number
}

export interface MedicineStockSnapshot {
  medicine_id: string
  units_in_stock: number
  avg_daily_consumption: number
}

export interface DailyLog {
  log_id: string
  centre_id: string
  log_date: string
  stock_snapshot: MedicineStockSnapshot[]
  footfall_count: number
  bed_occupancy_pct: number
  doctor_attendance: boolean
  test_kits_available: boolean
}

export type Severity = "low" | "medium" | "high"
export type AlertStatus = "open" | "resolved"

export interface Alert {
  alert_id: string
  centre_id: string
  created_at: string
  category: string
  severity: Severity
  status: AlertStatus
  message: string
  source_metric: Record<string, unknown>
}

export type RecommendationStatus = "pending" | "approved" | "rejected"

export interface RedistributionRecommendation {
  recommendation_id: string
  medicine_id: string
  from_centre_id: string
  to_centre_id: string
  suggested_units: number
  urgency_score: number
  distance_km: number
  status: RecommendationStatus
  created_at: string
}

export interface StockForecast {
  medicine_id: string
  current_stock: number
  predicted_daily_consumption: number
  days_to_stockout: number | null
}

export interface FootfallForecast {
  daily_forecast: number[]
  total_7day_forecast: number
}

export interface CentrePayload {
  centre_id: string
  name: string
  type: "PHC" | "CHC"
  district_zone: string
  health_score: number | null
  metrics: Record<string, number> | null
  z_scores: Record<string, number>
  stock_forecasts: StockForecast[]
  footfall_forecast: FootfallForecast
  summary: string
}

export interface DistrictPayload {
  generated_at: string
  language: string
  centres: CentrePayload[]
  alerts_created: Alert[]
  recommendations_created: RedistributionRecommendation[]
}
