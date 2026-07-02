import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react"
import { api } from "../api/client"
import type { Centre, StockItem } from "../types"

interface AppSettingsValue {
  centres: Centre[]
  stockItems: StockItem[]
  centreId: string | null
  setCentreId: (id: string) => void
  loading: boolean
}

const AppSettingsContext = createContext<AppSettingsValue | null>(null)

const STORAGE_KEY = "swasthyasetu_staff_centre_id"

export function AppSettingsProvider({ children }: { children: ReactNode }) {
  const [centres, setCentres] = useState<Centre[]>([])
  const [stockItems, setStockItems] = useState<StockItem[]>([])
  const [centreId, setCentreIdState] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.listCentres(), api.listStockItems()])
      .then(([centresData, stockItemsData]) => {
        setCentres(centresData)
        setStockItems(stockItemsData)
      })
      .finally(() => setLoading(false))
  }, [])

  const setCentreId = (id: string) => {
    localStorage.setItem(STORAGE_KEY, id)
    setCentreIdState(id)
  }

  const value = useMemo<AppSettingsValue>(
    () => ({ centres, stockItems, centreId, setCentreId, loading }),
    [centres, stockItems, centreId, loading],
  )

  return <AppSettingsContext.Provider value={value}>{children}</AppSettingsContext.Provider>
}

export function useAppSettings(): AppSettingsValue {
  const ctx = useContext(AppSettingsContext)
  if (!ctx) throw new Error("useAppSettings must be used within an AppSettingsProvider")
  return ctx
}
