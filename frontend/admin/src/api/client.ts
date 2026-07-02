import axios from "axios"
import type {
  Alert,
  Centre,
  DailyLog,
  DistrictPayload,
  RedistributionRecommendation,
  StockItem,
} from "../types"

// In dev, Vite proxies /api -> the FastAPI backend (see vite.config.ts).
// In production, set VITE_API_BASE_URL to the deployed Cloud Run URL.
const baseURL = import.meta.env.VITE_API_BASE_URL ?? "/api"

const client = axios.create({ baseURL })

export const api = {
  listCentres: () => client.get<Centre[]>("/centres").then((r) => r.data),

  listDailyLogs: (centreId: string) =>
    client.get<DailyLog[]>("/daily-logs", { params: { centre_id: centreId } }).then((r) => r.data),

  listStockItems: () => client.get<StockItem[]>("/stock-items").then((r) => r.data),

  listAlerts: (status?: "open" | "resolved") =>
    client.get<Alert[]>("/alerts", { params: status ? { status } : {} }).then((r) => r.data),

  resolveAlert: (alertId: string) =>
    client.patch<Alert>(`/alerts/${alertId}/resolve`).then((r) => r.data),

  listRecommendations: (status?: "pending" | "approved" | "rejected") =>
    client
      .get<RedistributionRecommendation[]>("/recommendations", { params: status ? { status } : {} })
      .then((r) => r.data),

  approveRecommendation: (id: string) =>
    client.patch<RedistributionRecommendation>(`/recommendations/${id}/approve`).then((r) => r.data),

  rejectRecommendation: (id: string) =>
    client.patch<RedistributionRecommendation>(`/recommendations/${id}/reject`).then((r) => r.data),

  runOrchestration: (language: string) =>
    client.post<DistrictPayload>("/orchestration/run", null, { params: { language } }).then((r) => r.data),
}
