interface Props {
  icon: string
  label: string
  value: number
  onChange: (value: number) => void
  step?: number
  min?: number
  max?: number
}

export function Stepper({ icon, label, value, onChange, step = 1, min = 0, max = Infinity }: Props) {
  return (
    <div className="rounded-xl bg-white p-4 shadow-sm">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-2xl" aria-hidden>
          {icon}
        </span>
        <span className="text-base font-medium text-slate-800">{label}</span>
      </div>
      <div className="flex items-center justify-between gap-3">
        <button
          type="button"
          onClick={() => onChange(Math.max(min, value - step))}
          className="h-12 w-12 rounded-full bg-slate-100 text-2xl font-bold text-slate-700 active:scale-95"
          aria-label="decrease"
        >
          −
        </button>
        <span className="min-w-16 text-center text-2xl font-semibold text-slate-900">{value}</span>
        <button
          type="button"
          onClick={() => onChange(Math.min(max, value + step))}
          className="h-12 w-12 rounded-full bg-slate-100 text-2xl font-bold text-slate-700 active:scale-95"
          aria-label="increase"
        >
          +
        </button>
      </div>
    </div>
  )
}
