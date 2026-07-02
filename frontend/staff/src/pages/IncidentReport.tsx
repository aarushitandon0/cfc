import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { api } from "../api/client"
import { VoiceButton } from "../components/VoiceButton"
import { useAppSettings } from "../context/AppSettingsContext"
import { useLanguage } from "../i18n/LanguageContext"

export function IncidentReport() {
  const navigate = useNavigate()
  const { centreId } = useAppSettings()
  const { t, apiLanguageCode } = useLanguage()

  const [typing, setTyping] = useState(false)
  const [text, setText] = useState("")
  const [sending, setSending] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState(false)

  const handleVoiceRecording = async (blob: Blob) => {
    if (!centreId) return
    setSending(true)
    setError(false)
    try {
      await api.submitVoiceIncident(centreId, apiLanguageCode, blob)
      setSubmitted(true)
      setTimeout(() => navigate("/"), 1200)
    } catch {
      setError(true)
    } finally {
      setSending(false)
    }
  }

  const handleTextSubmit = async () => {
    if (!centreId || !text.trim()) return
    setSending(true)
    setError(false)
    try {
      await api.submitTextIncident(centreId, apiLanguageCode, text.trim())
      setSubmitted(true)
      setTimeout(() => navigate("/"), 1200)
    } catch {
      setError(true)
    } finally {
      setSending(false)
    }
  }

  if (submitted) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-slate-50 p-6 text-center">
        <span className="text-6xl">✅</span>
        <p className="text-xl font-semibold text-slate-800">{t("incidentSubmitted")}</p>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 p-5">
      <button onClick={() => navigate("/")} className="mb-4 self-start text-base font-medium text-blue-600">
        {t("back")}
      </button>
      <h1 className="mb-6 text-xl font-bold text-slate-900">{t("reportProblem")}</h1>

      {sending ? (
        <div className="flex flex-1 items-center justify-center text-lg text-slate-600">{t("sending")}</div>
      ) : typing ? (
        <div className="flex flex-1 flex-col gap-4">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={t("incidentPlaceholder")}
            rows={6}
            autoFocus
            className="w-full rounded-xl border border-slate-300 bg-white p-4 text-lg"
          />
          <button
            onClick={handleTextSubmit}
            disabled={!text.trim()}
            className="rounded-xl bg-blue-600 py-4 text-xl font-bold text-white disabled:opacity-40"
          >
            {t("submit")}
          </button>
        </div>
      ) : (
        <div className="flex flex-1 flex-col items-center justify-center gap-6">
          <VoiceButton onRecordingComplete={handleVoiceRecording} />
          <button onClick={() => setTyping(true)} className="text-base font-medium text-blue-600 underline">
            {t("typeInstead")}
          </button>
        </div>
      )}

      {error && <p className="mt-3 text-center text-sm text-red-600">⚠️ Could not send. Try again.</p>}
    </div>
  )
}
