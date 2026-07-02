import { useNavigate } from "react-router-dom"
import { useAppSettings } from "../context/AppSettingsContext"
import { useLanguage } from "../i18n/LanguageContext"

export function Home() {
  const navigate = useNavigate()
  const { centres, centreId } = useAppSettings()
  const { t } = useLanguage()
  const centre = centres.find((c) => c.centre_id === centreId)

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 p-5">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">{t("appTitle")}</h1>
          {centre && <p className="text-sm text-slate-500">{centre.name}</p>}
        </div>
        <button
          onClick={() => navigate("/onboarding")}
          aria-label={t("changeCentre")}
          className="rounded-full bg-white p-3 text-2xl shadow-sm"
        >
          ⚙️
        </button>
      </header>

      <div className="flex flex-1 flex-col gap-5">
        <button
          onClick={() => navigate("/daily-log")}
          className="flex flex-col items-center justify-center gap-3 rounded-2xl bg-blue-600 py-12 text-white shadow-md active:scale-95"
        >
          <span className="text-6xl" aria-hidden>
            📋
          </span>
          <span className="text-2xl font-semibold">{t("dailyLog")}</span>
        </button>

        <button
          onClick={() => navigate("/report")}
          className="flex flex-col items-center justify-center gap-3 rounded-2xl bg-red-600 py-12 text-white shadow-md active:scale-95"
        >
          <span className="text-6xl" aria-hidden>
            🎤
          </span>
          <span className="text-2xl font-semibold">{t("reportProblem")}</span>
        </button>
      </div>
    </div>
  )
}
