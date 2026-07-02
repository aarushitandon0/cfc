export function healthScoreColor(score: number | null): string {
  if (score === null) return "#9ca3af" // gray - no data
  if (score >= 70) return "#16a34a" // green
  if (score >= 40) return "#d97706" // amber
  return "#dc2626" // red
}

export function healthScoreLabel(score: number | null): string {
  if (score === null) return "No data"
  if (score >= 70) return "Healthy"
  if (score >= 40) return "Needs attention"
  return "Critical"
}

export function severityColor(severity: "low" | "medium" | "high"): string {
  if (severity === "high") return "#dc2626"
  if (severity === "medium") return "#d97706"
  return "#2563eb"
}
