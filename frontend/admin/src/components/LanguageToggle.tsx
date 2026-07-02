import { useLanguage } from "../i18n/LanguageContext"
import { LANGUAGE_LABELS, type LanguageCode } from "../i18n/translations"

export function LanguageToggle() {
  const { language, setLanguage } = useLanguage()

  return (
    <select
      value={language}
      onChange={(e) => setLanguage(e.target.value as LanguageCode)}
      className="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm"
      aria-label="Language"
    >
      {Object.entries(LANGUAGE_LABELS).map(([code, label]) => (
        <option key={code} value={code}>
          {label}
        </option>
      ))}
    </select>
  )
}
