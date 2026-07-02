import { BrowserRouter, Route, Routes } from "react-router-dom"
import { DistrictDataProvider } from "./context/DistrictDataContext"
import { LanguageProvider } from "./i18n/LanguageContext"
import { CentreDetail } from "./pages/CentreDetail"
import { Dashboard } from "./pages/Dashboard"

function App() {
  return (
    <BrowserRouter>
      <LanguageProvider>
        <DistrictDataProvider>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/centres/:centreId" element={<CentreDetail />} />
          </Routes>
        </DistrictDataProvider>
      </LanguageProvider>
    </BrowserRouter>
  )
}

export default App
