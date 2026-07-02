import { useNavigate } from "react-router-dom"
import { useAppSettings } from "../context/AppSettingsContext"
import { useLanguage } from "../i18n/LanguageContext"
import { LANGUAGE_LABELS, type LanguageCode } from "../i18n/translations"

export function Onboarding() {
  const { centres, centreId, setCentreId, loading } = useAppSettings()
  const { language, setLanguage, t } = useLanguage()
  const navigate = useNavigate()

  const handleContinue = () => {
    if (centreId) navigate("/")
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-slate-50 p-6">
      <h1 className="text-2xl font-bold text-slate-900">{t("appTitle")}</h1>

      <div className="w-full max-w-sm space-y-4 rounded-xl bg-white p-5 shadow-sm">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">{t("selectLanguage")}</label>
          <div className="flex gap-2">
            {(Object.keys(LANGUAGE_LABELS) as LanguageCode[]).map((code) => (
              <button
                key={code}
                onClick={() => setLanguage(code)}
                className={`flex-1 rounded-lg border px-3 py-3 text-lg font-medium ${
                  language === code
                    ? "border-blue-600 bg-blue-50 text-blue-700"
                    : "border-slate-300 text-slate-700"
                }`}
              >
                {LANGUAGE_LABELS[code]}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">{t("selectCentre")}</label>
          {loading ? (
            <p className="text-sm text-slate-500">…</p>
          ) : (
            <select
              value={centreId ?? ""}
              onChange={(e) => setCentreId(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-3 text-lg"
            >
              <option value="" disabled>
                —
              </option>
              {centres.map((c) => (
                <option key={c.centre_id} value={c.centre_id}>
                  {c.name}
                </option>
              ))}
            </select>
          )}
        </div>

        <button
          onClick={handleContinue}
          disabled={!centreId}
          className="w-full rounded-lg bg-blue-600 py-3 text-lg font-semibold text-white disabled:opacity-40"
        >
          {t("continue")}
        </button>
      </div>
    </div>
  )
}
