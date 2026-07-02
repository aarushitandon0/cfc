import axios from "axios"
import type { Alert, Centre, DailyLog, StockItem } from "../types"

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "/api"

const client = axios.create({ baseURL })

export const api = {
  listCentres: () => client.get<Centre[]>("/centres").then((r) => r.data),

  listStockItems: () => client.get<StockItem[]>("/stock-items").then((r) => r.data),

  // most recent daily log for a centre, used to prefill the form with
  // yesterday's stock levels so staff only report what changed
  latestDailyLog: async (centreId: string): Promise<DailyLog | null> => {
    const logs = await client
      .get<DailyLog[]>("/daily-logs", { params: { centre_id: centreId } })
      .then((r) => r.data)
    if (logs.length === 0) return null
    return logs.reduce((latest, log) => (log.log_date > latest.log_date ? log : latest))
  },

  submitDailyLog: (log: DailyLog) => client.post<DailyLog>("/daily-logs", log).then((r) => r.data),

  submitTextIncident: (centreId: string, languageCode: string, text: string) =>
    client
      .post<Alert>("/incidents/text", { centre_id: centreId, language_code: languageCode, text })
      .then((r) => r.data),

  submitVoiceIncident: (centreId: string, languageCode: string, audio: Blob) => {
    const form = new FormData()
    form.append("centre_id", centreId)
    form.append("language_code", languageCode)
    form.append("audio", audio, "incident.webm")
    return client.post<Alert>("/incidents/voice", form).then((r) => r.data)
  },
}
