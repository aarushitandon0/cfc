import { createContext, useContext, useMemo, useState, type ReactNode } from "react"
import { LANGUAGE_NAMES, translate, type LanguageCode } from "./translations"

interface LanguageContextValue {
  language: LanguageCode
  languageName: string
  setLanguage: (lang: LanguageCode) => void
  t: (key: Parameters<typeof translate>[0]) => string
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<LanguageCode>("en")

  const value = useMemo<LanguageContextValue>(
    () => ({
      language,
      languageName: LANGUAGE_NAMES[language],
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
