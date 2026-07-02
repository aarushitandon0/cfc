import type { RedistributionRecommendation } from "../types"
import { useLanguage } from "../i18n/LanguageContext"

interface Props {
  recommendations: RedistributionRecommendation[]
  centreNames: Map<string, string>
  medicineNames: Map<string, string>
  onApprove: (id: string) => void
  onReject: (id: string) => void
}

export function RedistributionPanel({
  recommendations,
  centreNames,
  medicineNames,
  onApprove,
  onReject,
}: Props) {
  const { t } = useLanguage()

  if (recommendations.length === 0) {
    return <p className="text-sm text-slate-500">{t("noRecommendations")}</p>
  }

  return (
    <ul className="space-y-2">
      {recommendations.map((rec) => (
        <li
          key={rec.recommendation_id}
          className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3"
        >
          <div className="flex-1 text-sm text-slate-800">
            <span className="font-medium">{medicineNames.get(rec.medicine_id) ?? rec.medicine_id}</span>
            {": "}
            {centreNames.get(rec.from_centre_id) ?? rec.from_centre_id}
            {" → "}
            {centreNames.get(rec.to_centre_id) ?? rec.to_centre_id}
            <div className="text-xs text-slate-500">
              {rec.suggested_units} units · urgency {rec.urgency_score} · {rec.distance_km} km
            </div>
          </div>
          <div className="flex shrink-0 gap-2">
            <button
              onClick={() => onApprove(rec.recommendation_id)}
              className="rounded-md bg-green-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-green-700"
            >
              {t("approve")}
            </button>
            <button
              onClick={() => onReject(rec.recommendation_id)}
              className="rounded-md border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100"
            >
              {t("reject")}
            </button>
          </div>
        </li>
      ))}
    </ul>
  )
}
