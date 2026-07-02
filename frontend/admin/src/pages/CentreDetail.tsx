import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { useDistrictData } from "../context/DistrictDataContext"
import { useLanguage } from "../i18n/LanguageContext"
import type { DailyLog } from "../types"
import { healthScoreColor, healthScoreLabel } from "../utils/healthColor"

const TREND_WINDOW_DAYS = 30

export function CentreDetail() {
  const { centreId } = useParams<{ centreId: string }>()
  const { t } = useLanguage()
  const { centres, stockItems, centrePayloads, loadDailyLogs } = useDistrictData()

  const [logs, setLogs] = useState<DailyLog[]>([])

  useEffect(() => {
    if (!centreId) return
    loadDailyLogs(centreId).then((data) => {
      const sorted = [...data].sort((a, b) => a.log_date.localeCompare(b.log_date))
      setLogs(sorted.slice(-TREND_WINDOW_DAYS))
    })
  }, [centreId, loadDailyLogs])

  const centre = centres.find((c) => c.centre_id === centreId)
  const payload = centreId ? centrePayloads.get(centreId) : undefined
  const thresholds = new Map(stockItems.map((s) => [s.medicine_id, s.reorder_threshold_days]))
  const medicineNames = new Map(stockItems.map((s) => [s.medicine_id, s.name]))

  const chartData = logs.map((log) => ({
    date: log.log_date.slice(5), // MM-DD
    footfall: log.footfall_count,
    bedOccupancy: log.bed_occupancy_pct,
  }))

  return (
    <div className="mx-auto max-w-4xl p-4 sm:p-6">
      <Link to="/" className="text-sm font-medium text-blue-600 hover:underline">
        {t("back")}
      </Link>

      {!centre ? (
        <p className="mt-4 text-sm text-slate-500">{t("loading")}</p>
      ) : (
        <>
          <header className="mt-3 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-xl font-semibold text-slate-900">{centre.name}</h1>
              <p className="text-sm text-slate-500">
                {centre.type} · {t("zone")}: {centre.district_zone} · bed capacity {centre.bed_capacity}
              </p>
            </div>
            {payload && (
              <span
                className="rounded-full px-3 py-1 text-sm font-semibold text-white"
                style={{ backgroundColor: healthScoreColor(payload.health_score) }}
              >
                {t("healthScore")}: {payload.health_score} ({healthScoreLabel(payload.health_score)})
              </span>
            )}
          </header>

          {payload && (
            <div className="mt-4 rounded-lg border border-slate-200 bg-white p-4">
              <h2 className="mb-1 text-sm font-semibold uppercase text-slate-500">{t("summary")}</h2>
              <p className="text-sm text-slate-800">{payload.summary}</p>
            </div>
          )}

          <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">{t("footfallTrend")}</h2>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" fontSize={10} />
                  <YAxis fontSize={10} />
                  <Tooltip />
                  <Line type="monotone" dataKey="footfall" stroke="#2563eb" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">
                {t("bedOccupancyTrend")}
              </h2>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" fontSize={10} />
                  <YAxis fontSize={10} domain={[0, 100]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="bedOccupancy" stroke="#d97706" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {payload && (
            <div className="mt-6 rounded-lg border border-slate-200 bg-white p-4">
              <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">{t("stockForecast")}</h2>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase text-slate-500">
                    <th className="py-1">Medicine</th>
                    <th className="py-1">Current stock</th>
                    <th className="py-1">{t("daysToStockout")}</th>
                  </tr>
                </thead>
                <tbody>
                  {payload.stock_forecasts.map((f) => {
                    const threshold = thresholds.get(f.medicine_id) ?? Infinity
                    const atRisk = f.days_to_stockout !== null && f.days_to_stockout < threshold
                    return (
                      <tr key={f.medicine_id} className="border-t border-slate-100">
                        <td className="py-1.5">{medicineNames.get(f.medicine_id) ?? f.medicine_id}</td>
                        <td className="py-1.5">{f.current_stock}</td>
                        <td className={`py-1.5 font-medium ${atRisk ? "text-red-600" : "text-slate-700"}`}>
                          {f.days_to_stockout ?? "—"}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
