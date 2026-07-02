import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"
import { api } from "../api/client"
import { useLanguage } from "../i18n/LanguageContext"
import type { Alert, Centre, CentrePayload, DailyLog, RedistributionRecommendation, StockItem } from "../types"

interface DistrictDataValue {
  centres: Centre[]
  stockItems: StockItem[]
  alerts: Alert[]
  recommendations: RedistributionRecommendation[]
  centrePayloads: Map<string, CentrePayload>
  loading: boolean
  error: string | null
  refreshAnalysis: () => Promise<void>
  resolveAlert: (alertId: string) => Promise<void>
  approveRecommendation: (id: string) => Promise<void>
  rejectRecommendation: (id: string) => Promise<void>
  loadDailyLogs: (centreId: string) => Promise<DailyLog[]>
}

const DistrictDataContext = createContext<DistrictDataValue | null>(null)

export function DistrictDataProvider({ children }: { children: ReactNode }) {
  const { languageName } = useLanguage()

  const [centres, setCentres] = useState<Centre[]>([])
  const [stockItems, setStockItems] = useState<StockItem[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [recommendations, setRecommendations] = useState<RedistributionRecommendation[]>([])
  const [centrePayloads, setCentrePayloads] = useState<Map<string, CentrePayload>>(new Map())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadAlertsAndRecommendations = useCallback(async () => {
    const [alertsData, recsData] = await Promise.all([
      api.listAlerts("open"),
      api.listRecommendations("pending"),
    ])
    setAlerts(alertsData)
    setRecommendations(recsData)
  }, [])

  const refreshAnalysis = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const payload = await api.runOrchestration(languageName)
      setCentrePayloads(new Map(payload.centres.map((c) => [c.centre_id, c])))
      await loadAlertsAndRecommendations()
    } catch {
      setError("Could not reach the analysis backend. Is the API running?")
    } finally {
      setLoading(false)
    }
  }, [languageName, loadAlertsAndRecommendations])

  useEffect(() => {
    api
      .listCentres()
      .then(setCentres)
      .catch(() => setError("Could not load centres."))
    api.listStockItems().then(setStockItems).catch(() => undefined)
  }, [])

  useEffect(() => {
    refreshAnalysis()
  }, [refreshAnalysis])

  const resolveAlert = useCallback(async (alertId: string) => {
    await api.resolveAlert(alertId)
    setAlerts((prev) => prev.filter((a) => a.alert_id !== alertId))
  }, [])

  const approveRecommendation = useCallback(async (id: string) => {
    await api.approveRecommendation(id)
    setRecommendations((prev) => prev.filter((r) => r.recommendation_id !== id))
  }, [])

  const rejectRecommendation = useCallback(async (id: string) => {
    await api.rejectRecommendation(id)
    setRecommendations((prev) => prev.filter((r) => r.recommendation_id !== id))
  }, [])

  const loadDailyLogs = useCallback((centreId: string) => api.listDailyLogs(centreId), [])

  const value = useMemo<DistrictDataValue>(
    () => ({
      centres,
      stockItems,
      alerts,
      recommendations,
      centrePayloads,
      loading,
      error,
      refreshAnalysis,
      resolveAlert,
      approveRecommendation,
      rejectRecommendation,
      loadDailyLogs,
    }),
    [
      centres,
      stockItems,
      alerts,
      recommendations,
      centrePayloads,
      loading,
      error,
      refreshAnalysis,
      resolveAlert,
      approveRecommendation,
      rejectRecommendation,
      loadDailyLogs,
    ],
  )

  return <DistrictDataContext.Provider value={value}>{children}</DistrictDataContext.Provider>
}

export function useDistrictData(): DistrictDataValue {
  const ctx = useContext(DistrictDataContext)
  if (!ctx) throw new Error("useDistrictData must be used within a DistrictDataProvider")
  return ctx
}
