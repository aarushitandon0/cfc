import type { Alert } from "../types"
import { severityColor } from "../utils/healthColor"
import { useLanguage } from "../i18n/LanguageContext"

interface Props {
  alerts: Alert[]
  centreNames: Map<string, string>
  onResolve: (alertId: string) => void
}

export function AlertsFeed({ alerts, centreNames, onResolve }: Props) {
  const { t } = useLanguage()

  if (alerts.length === 0) {
    return <p className="text-sm text-slate-500">{t("noAlerts")}</p>
  }

  return (
    <ul className="space-y-2">
      {alerts.map((alert) => (
        <li
          key={alert.alert_id}
          className="flex items-start justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3"
        >
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span
                className="inline-block h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: severityColor(alert.severity) }}
              />
              <span className="text-xs font-medium uppercase text-slate-500">
                {alert.severity} · {alert.category}
              </span>
              <span className="text-xs text-slate-400">
                {centreNames.get(alert.centre_id) ?? alert.centre_id}
              </span>
            </div>
            <p className="mt-1 text-sm text-slate-800">{alert.message}</p>
          </div>
          <button
            onClick={() => onResolve(alert.alert_id)}
            className="shrink-0 rounded-md border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100"
          >
            {t("resolve")}
          </button>
        </li>
      ))}
    </ul>
  )
}
