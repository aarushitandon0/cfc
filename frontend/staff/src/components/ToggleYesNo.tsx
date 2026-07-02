import { useLanguage } from "../i18n/LanguageContext"

interface Props {
  icon: string
  label: string
  value: boolean
  onChange: (value: boolean) => void
}

export function ToggleYesNo({ icon, label, value, onChange }: Props) {
  const { t } = useLanguage()

  return (
    <div className="rounded-xl bg-white p-4 shadow-sm">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-2xl" aria-hidden>
          {icon}
        </span>
        <span className="text-base font-medium text-slate-800">{label}</span>
      </div>
      <div className="flex gap-3">
        <button
          type="button"
          onClick={() => onChange(true)}
          className={`flex-1 rounded-lg py-3 text-lg font-semibold ${
            value ? "bg-green-600 text-white" : "bg-slate-100 text-slate-600"
          }`}
        >
          ✅ {t("yes")}
        </button>
        <button
          type="button"
          onClick={() => onChange(false)}
          className={`flex-1 rounded-lg py-3 text-lg font-semibold ${
            !value ? "bg-red-600 text-white" : "bg-slate-100 text-slate-600"
          }`}
        >
          ❌ {t("no")}
        </button>
      </div>
    </div>
  )
}
