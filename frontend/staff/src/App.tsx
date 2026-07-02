import type { ReactNode } from "react"
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import { AppSettingsProvider, useAppSettings } from "./context/AppSettingsContext"
import { LanguageProvider } from "./i18n/LanguageContext"
import { DailyLogForm } from "./pages/DailyLogForm"
import { Home } from "./pages/Home"
import { IncidentReport } from "./pages/IncidentReport"
import { Onboarding } from "./pages/Onboarding"

function RequireCentre({ children }: { children: ReactNode }) {
  const { centreId, loading } = useAppSettings()
  if (loading) return null
  if (!centreId) return <Navigate to="/onboarding" replace />
  return <>{children}</>
}

function App() {
  return (
    <BrowserRouter>
      <LanguageProvider>
        <AppSettingsProvider>
          <Routes>
            <Route path="/onboarding" element={<Onboarding />} />
            <Route
              path="/"
              element={
                <RequireCentre>
                  <Home />
                </RequireCentre>
              }
            />
            <Route
              path="/daily-log"
              element={
                <RequireCentre>
                  <DailyLogForm />
                </RequireCentre>
              }
            />
            <Route
              path="/report"
              element={
                <RequireCentre>
                  <IncidentReport />
                </RequireCentre>
              }
            />
          </Routes>
        </AppSettingsProvider>
      </LanguageProvider>
    </BrowserRouter>
  )
}

export default App
