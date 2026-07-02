import { useRef, useState } from "react"
import { useLanguage } from "../i18n/LanguageContext"

interface Props {
  onRecordingComplete: (blob: Blob) => void
  disabled?: boolean
}

export function VoiceButton({ onRecordingComplete, disabled }: Props) {
  const { t } = useLanguage()
  const [recording, setRecording] = useState(false)
  const [permissionError, setPermissionError] = useState(false)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    if (disabled) return
    setPermissionError(false)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []
      recorder.ondataavailable = (e) => chunksRef.current.push(e.data)
      recorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop())
        const blob = new Blob(chunksRef.current, { type: "audio/webm" })
        onRecordingComplete(blob)
      }
      recorder.start()
      recorderRef.current = recorder
      setRecording(true)
    } catch {
      setPermissionError(true)
    }
  }

  const stopRecording = () => {
    recorderRef.current?.stop()
    recorderRef.current = null
    setRecording(false)
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        type="button"
        disabled={disabled}
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        onTouchStart={startRecording}
        onTouchEnd={stopRecording}
        className={`flex h-40 w-40 flex-col items-center justify-center gap-2 rounded-full text-white shadow-lg active:scale-95 disabled:opacity-40 ${
          recording ? "bg-red-700 animate-pulse" : "bg-red-600"
        }`}
      >
        <span className="text-5xl" aria-hidden>
          🎤
        </span>
      </button>
      <p className="text-center text-sm font-medium text-slate-600">
        {recording ? t("recording") : t("recordVoice")}
      </p>
      {permissionError && <p className="text-center text-sm text-red-600">{t("micPermissionDenied")}</p>}
    </div>
  )
}
