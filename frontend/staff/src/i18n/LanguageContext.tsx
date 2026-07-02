import { createContext, useContext, useMemo, useState, type ReactNode } from "react"
import { LANGUAGE_API_CODES, translate, type LanguageCode } from "./translations"

interface LanguageContextValue {
  language: LanguageCode
  apiLanguageCode: string
  setLanguage: (lang: LanguageCode) => void
  t: (key: Parameters<typeof translate>[0]) => string
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

const STORAGE_KEY = "swasthyasetu_staff_language"

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<LanguageCode>(
    () => (localStorage.getItem(STORAGE_KEY) as LanguageCode) || "en",
  )

  const setLanguage = (lang: LanguageCode) => {
    localStorage.setItem(STORAGE_KEY, lang)
    setLanguageState(lang)
  }

  const value = useMemo<LanguageContextValue>(
    () => ({
      language,
      apiLanguageCode: LANGUAGE_API_CODES[language],
      setLanguage,
      t: (key) => translate(key, language),
    }),
    [language],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error("useLanguage must be used within a LanguageProvider")
  return ctx
}
