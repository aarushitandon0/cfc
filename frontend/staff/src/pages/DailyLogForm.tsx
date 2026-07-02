import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { api } from "../api/client"
import { Stepper } from "../components/Stepper"
import { ToggleYesNo } from "../components/ToggleYesNo"
import { useAppSettings } from "../context/AppSettingsContext"
import { useLanguage } from "../i18n/LanguageContext"
import type { MedicineStockSnapshot } from "../types"

// new_avg blends yesterday's rolling average with today's implied usage,
// so the forecaster gets an evolving signal from a single "stock remaining"
// number per medicine instead of asking staff to report consumption directly.
const CONSUMPTION_SMOOTHING = 0.8

export function DailyLogForm() {
  const navigate = useNavigate()
  const { centreId, stockItems } = useAppSettings()
  const { t } = useLanguage()

  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [footfall, setFootfall] = useState(0)
  const [bedOccupancy, setBedOccupancy] = useState(0)
  const [doctorPresent, setDoctorPresent] = useState(true)
  const [testKitsAvailable, setTestKitsAvailable] = useState(true)
  const [stock, setStock] = useState<Map<string, MedicineStockSnapshot>>(new Map())
  // yesterday's values, kept immutable, so submit-time can derive today's
  // implied consumption from (previous units_in_stock - what staff entered)
  const [previousStock, setPreviousStock] = useState<Map<string, MedicineStockSnapshot>>(new Map())

  useEffect(() => {
    if (!centreId) return
    api.latestDailyLog(centreId).then((log) => {
      const prefilled = new Map<string, MedicineStockSnapshot>()
      for (const item of stockItems) {
        const previous = log?.stock_snapshot.find((s) => s.medicine_id === item.medicine_id)
        prefilled.set(item.medicine_id, {
          medicine_id: item.medicine_id,
          units_in_stock: previous?.units_in_stock ?? 0,
          avg_daily_consumption: previous?.avg_daily_consumption ?? 0,
        })
      }
      setStock(prefilled)
      setPreviousStock(new Map(prefilled))
      if (log) {
        setFootfall(log.footfall_count)
        setBedOccupancy(log.bed_occupancy_pct)
        setDoctorPresent(log.doctor_attendance)
        setTestKitsAvailable(log.test_kits_available)
      }
      setLoading(false)
    })
  }, [centreId, stockItems])

  const setStockUnits = (medicineId: string, units: number) => {
    setStock((prev) => {
      const next = new Map(prev)
      const entry = next.get(medicineId)
      if (entry) next.set(medicineId, { ...entry, units_in_stock: Math.max(0, units) })
      return next
    })
  }

  const handleSubmit = async () => {
    if (!centreId) return
    setSubmitting(true)
    const today = new Date().toISOString().slice(0, 10)

    const stockSnapshot: MedicineStockSnapshot[] = Array.from(stock.values()).map((entry) => {
      const previous = previousStock.get(entry.medicine_id)
      const impliedConsumption = Math.max(0, (previous?.units_in_stock ?? entry.units_in_stock) - entry.units_in_stock)
      const previousAvg = previous?.avg_daily_consumption ?? impliedConsumption
      const avgDailyConsumption =
        CONSUMPTION_SMOOTHING * previousAvg + (1 - CONSUMPTION_SMOOTHING) * impliedConsumption
      return { ...entry, avg_daily_consumption: Math.round(avgDailyConsumption * 100) / 100 }
    })

    try {
      await api.submitDailyLog({
        log_id: `${centreId}_${today}`,
        centre_id: centreId,
        log_date: today,
        stock_snapshot: stockSnapshot,
        footfall_count: footfall,
        bed_occupancy_pct: bedOccupancy,
        doctor_attendance: doctorPresent,
        test_kits_available: testKitsAvailable,
      })
      setSubmitted(true)
      setTimeout(() => navigate("/"), 1200)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-slate-500">…</div>
  }

  if (submitted) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-slate-50 p-6 text-center">
        <span className="text-6xl">✅</span>
        <p className="text-xl font-semibold text-slate-800">{t("submitted")}</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 p-5 pb-28">
      <button onClick={() => navigate("/")} className="mb-4 text-base font-medium text-blue-600">
        {t("back")}
      </button>
      <h1 className="mb-4 text-xl font-bold text-slate-900">{t("dailyLog")}</h1>

      <div className="space-y-3">
        <Stepper icon="🧍" label={t("footfall")} value={footfall} onChange={setFootfall} step={5} />
        <Stepper
          icon="🛏️"
          label={t("bedOccupancy")}
          value={bedOccupancy}
          onChange={setBedOccupancy}
          step={5}
          max={100}
        />
        <ToggleYesNo icon="🩺" label={t("doctorPresent")} value={doctorPresent} onChange={setDoctorPresent} />
        <ToggleYesNo
          icon="🧪"
          label={t("testKitsAvailable")}
          value={testKitsAvailable}
          onChange={setTestKitsAvailable}
        />

        <h2 className="pt-2 text-base font-semibold text-slate-700">{t("stockRemaining")}</h2>
        {stockItems.map((item) => (
          <Stepper
            key={item.medicine_id}
            icon="💊"
            label={item.name}
            value={stock.get(item.medicine_id)?.units_in_stock ?? 0}
            onChange={(v) => setStockUnits(item.medicine_id, v)}
            step={5}
          />
        ))}
      </div>

      <div className="fixed inset-x-0 bottom-0 bg-slate-50 p-4">
        <button
          onClick={handleSubmit}
          disabled={submitting}
          className="w-full rounded-xl bg-blue-600 py-4 text-xl font-bold text-white shadow-md disabled:opacity-50"
        >
          {submitting ? "…" : t("submit")}
        </button>
      </div>
    </div>
  )
}
