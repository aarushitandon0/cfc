export type LanguageCode = "en" | "hi" | "or"

export const LANGUAGE_LABELS: Record<LanguageCode, string> = {
  en: "English",
  hi: "Hindi",
  or: "Odia",
}

// The orchestration endpoint's `language` query param is passed straight into
// the Gemini summarizer prompt, so it needs the full English name, not a code.
export const LANGUAGE_NAMES: Record<LanguageCode, string> = {
  en: "English",
  hi: "Hindi",
  or: "Odia",
}

type Dictionary = Record<string, Record<LanguageCode, string>>

export const translations: Dictionary = {
  appTitle: { en: "SwasthyaSetu District Dashboard", hi: "स्वास्थ्य सेतु जिला डैशबोर्ड", or: "ସ୍ୱାସ୍ଥ୍ୟ ସେତୁ ଜିଲ୍ଲା ଡ୍ୟାସବୋର୍ଡ" },
  centres: { en: "Centres", hi: "केंद्र", or: "କେନ୍ଦ୍ର" },
  alertsFeed: { en: "Alerts", hi: "अलर्ट", or: "ଆଲର୍ଟ" },
  redistribution: { en: "Redistribution", hi: "पुनर्वितरण", or: "ପୁନଃବଣ୍ଟନ" },
  healthScore: { en: "Health Score", hi: "स्वास्थ्य स्कोर", or: "ସ୍ୱାସ୍ଥ୍ୟ ସ୍କୋର" },
  runOrchestration: { en: "Refresh Analysis", hi: "विश्लेषण ताज़ा करें", or: "ବିଶ୍ଳେଷଣ ସତେଜ କରନ୍ତୁ" },
  loading: { en: "Loading…", hi: "लोड हो रहा है…", or: "ଲୋଡ୍ ହେଉଛି…" },
  approve: { en: "Approve", hi: "स्वीकृत करें", or: "ଅନୁମୋଦନ କରନ୍ତୁ" },
  reject: { en: "Reject", hi: "अस्वीकार करें", or: "ବାତିଲ୍ କରନ୍ତୁ" },
  resolve: { en: "Resolve", hi: "हल करें", or: "ସମାଧାନ କରନ୍ତୁ" },
  noAlerts: { en: "No open alerts.", hi: "कोई खुला अलर्ट नहीं।", or: "କୌଣସି ଖୋଲା ଆଲର୍ଟ ନାହିଁ।" },
  noRecommendations: { en: "No pending recommendations.", hi: "कोई लंबित सिफारिश नहीं।", or: "କୌଣସି ବିଚାରାଧୀନ ସୁପାରିଶ ନାହିଁ।" },
  viewDetails: { en: "View details", hi: "विवरण देखें", or: "ବିବରଣୀ ଦେଖନ୍ତୁ" },
  back: { en: "← Back to dashboard", hi: "← डैशबोर्ड पर वापस", or: "← ଡ୍ୟାସବୋର୍ଡକୁ ଫେରନ୍ତୁ" },
  footfallTrend: { en: "Footfall (last 30 days)", hi: "फुटफॉल (पिछले 30 दिन)", or: "ପଦଚାପ (ଗତ ୩୦ ଦିନ)" },
  bedOccupancyTrend: { en: "Bed Occupancy % (last 30 days)", hi: "बेड अधिभोग % (पिछले 30 दिन)", or: "ଶଯ୍ୟା ବ୍ୟବହାର % (ଗତ ୩୦ ଦିନ)" },
  stockForecast: { en: "Stock Forecast", hi: "स्टॉक पूर्वानुमान", or: "ଷ୍ଟକ୍ ପୂର୍ବାନୁମାନ" },
  daysToStockout: { en: "Days to stockout", hi: "स्टॉक खत्म होने में दिन", or: "ଷ୍ଟକ୍ ସରିବାକୁ ଦିନ" },
  summary: { en: "AI Summary", hi: "एआई सारांश", or: "AI ସାରାଂଶ" },
  zone: { en: "Zone", hi: "क्षेत्र", or: "ଜୋନ" },
}

export function translate(key: keyof typeof translations, language: LanguageCode): string {
  return translations[key]?.[language] ?? translations[key]?.en ?? key
}
