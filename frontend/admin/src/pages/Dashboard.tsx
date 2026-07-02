import { Link } from "react-router-dom"
import { AlertsFeed } from "../components/AlertsFeed"
import { CentreMap } from "../components/CentreMap"
import { LanguageToggle } from "../components/LanguageToggle"
import { RedistributionPanel } from "../components/RedistributionPanel"
import { useDistrictData } from "../context/DistrictDataContext"
import { useLanguage } from "../i18n/LanguageContext"
import { healthScoreColor, healthScoreLabel } from "../utils/healthColor"

export function Dashboard() {
  const { t } = useLanguage()
  const {
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
  } = useDistrictData()

  const centreNames = new Map(centres.map((c) => [c.centre_id, c.name]))
  const medicineNames = new Map(stockItems.map((s) => [s.medicine_id, s.name]))

  const sortedCentres = [...centres].sort((a, b) => {
    const scoreA = centrePayloads.get(a.centre_id)?.health_score ?? 100
    const scoreB = centrePayloads.get(b.centre_id)?.health_score ?? 100
    return scoreA - scoreB
  })

  return (
    <div className="mx-auto max-w-6xl p-4 sm:p-6">
      <header className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold text-slate-900">{t("appTitle")}</h1>
        <div className="flex items-center gap-3">
          <LanguageToggle />
          <button
            onClick={refreshAnalysis}
            disabled={loading}
            className="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
          >
            {loading ? t("loading") : t("runOrchestration")}
          </button>
        </div>
      </header>

      {error && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section>
          <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">{t("centres")}</h2>
          <CentreMap centres={centres} centrePayloads={centrePayloads} />
          <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
            {sortedCentres.map((centre) => {
              const payload = centrePayloads.get(centre.centre_id)
              const score = payload?.health_score ?? null
              return (
                <li key={centre.centre_id} className="flex items-center justify-between gap-3 p-3">
                  <div>
                    <p className="text-sm font-medium text-slate-900">{centre.name}</p>
                    <p className="text-xs text-slate-500">
                      {centre.type} · {t("zone")}: {centre.district_zone}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className="rounded-full px-2 py-0.5 text-xs font-semibold text-white"
                      style={{ backgroundColor: healthScoreColor(score) }}
                      title={healthScoreLabel(score)}
                    >
                      {score ?? "—"}
                    </span>
                    <Link
                      to={`/centres/${centre.centre_id}`}
                      className="text-xs font-medium text-blue-600 hover:underline"
                    >
                      {t("viewDetails")}
                    </Link>
                  </div>
                </li>
              )
            })}
          </ul>
        </section>

        <section className="space-y-6">
          <div>
            <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">{t("alertsFeed")}</h2>
            <AlertsFeed alerts={alerts} centreNames={centreNames} onResolve={resolveAlert} />
          </div>
          <div>
            <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">{t("redistribution")}</h2>
            <RedistributionPanel
              recommendations={recommendations}
              centreNames={centreNames}
              medicineNames={medicineNames}
              onApprove={approveRecommendation}
              onReject={rejectRecommendation}
            />
          </div>
        </section>
      </div>
    </div>
  )
}
