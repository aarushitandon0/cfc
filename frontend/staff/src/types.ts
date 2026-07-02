// Subset of api/models/schemas.py needed by the staff intake app.

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

export interface Alert {
  alert_id: string
  centre_id: string
  created_at: string
  category: string
  severity: "low" | "medium" | "high"
  status: "open" | "resolved"
  message: string
  source_metric: Record<string, unknown>
}
