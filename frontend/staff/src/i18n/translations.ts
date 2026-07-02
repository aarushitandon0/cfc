export type LanguageCode = "en" | "hi" | "or"

export const LANGUAGE_LABELS: Record<LanguageCode, string> = {
  en: "English",
  hi: "हिन्दी",
  or: "ଓଡ଼ିଆ",
}

// Passed verbatim as the language_code field the backend forwards to
// Translation/Speech APIs (or the mock equivalents).
export const LANGUAGE_API_CODES: Record<LanguageCode, string> = {
  en: "en-IN",
  hi: "hi-IN",
  or: "or-IN",
}

type Dictionary = Record<string, Record<LanguageCode, string>>

export const translations: Dictionary = {
  appTitle: { en: "SwasthyaSetu Staff", hi: "स्वास्थ्य सेतु स्टाफ", or: "ସ୍ୱାସ୍ଥ୍ୟ ସେତୁ ଷ୍ଟାଫ" },
  selectCentre: { en: "Select your centre", hi: "अपना केंद्र चुनें", or: "ଆପଣଙ୍କ କେନ୍ଦ୍ର ବାଛନ୍ତୁ" },
  selectLanguage: { en: "Select language", hi: "भाषा चुनें", or: "ଭାଷା ବାଛନ୍ତୁ" },
  continue: { en: "Continue", hi: "जारी रखें", or: "ଆଗକୁ ବଢ଼ନ୍ତୁ" },
  dailyLog: { en: "Daily Log", hi: "दैनिक लॉग", or: "ଦୈନିକ ଲଗ୍" },
  reportProblem: { en: "Report a Problem", hi: "समस्या बताएं", or: "ସମସ୍ୟା ଜଣାନ୍ତୁ" },
  changeCentre: { en: "Change centre / language", hi: "केंद्र / भाषा बदलें", or: "କେନ୍ଦ୍ର / ଭାଷା ବଦଳାନ୍ତୁ" },
  footfall: { en: "Patients today", hi: "आज मरीज़", or: "ଆଜି ରୋଗୀ" },
  bedOccupancy: { en: "Beds occupied (%)", hi: "बेड भरे (%)", or: "ଶଯ୍ୟା ବ୍ୟବହାର (%)" },
  doctorPresent: { en: "Doctor present today?", hi: "डॉक्टर आज मौजूद हैं?", or: "ଡାକ୍ତର ଆଜି ଉପସ୍ଥିତ?" },
  yes: { en: "Yes", hi: "हाँ", or: "ହଁ" },
  no: { en: "No", hi: "नहीं", or: "ନାହିଁ" },
  testKitsAvailable: { en: "Test kits available?", hi: "टेस्ट किट उपलब्ध है?", or: "ଟେଷ୍ଟ କିଟ୍ ଉପଲବ୍ଧ?" },
  stockRemaining: { en: "Stock remaining", hi: "बचा हुआ स्टॉक", or: "ବାକି ଷ୍ଟକ୍" },
  submit: { en: "Submit", hi: "जमा करें", or: "ଦାଖଲ କରନ୍ତୁ" },
  submitted: { en: "Submitted! Thank you.", hi: "जमा हो गया! धन्यवाद।", or: "ଦାଖଲ ହେଲା! ଧନ୍ୟବାଦ।" },
  back: { en: "← Back", hi: "← वापस", or: "← ପଛକୁ" },
  recordVoice: { en: "Hold to speak", hi: "बोलने के लिए दबाएँ", or: "କହିବାକୁ ଦବାନ୍ତୁ" },
  recording: { en: "Recording… release to send", hi: "रिकॉर्डिंग… छोड़ें भेजने के लिए", or: "ରେକର୍ଡିଂ… ପଠାଇବାକୁ ଛାଡ଼ନ୍ତୁ" },
  typeInstead: { en: "Type instead", hi: "टाइप करें", or: "ଟାଇପ୍ କରନ୍ତୁ" },
  incidentPlaceholder: {
    en: "Describe the problem…",
    hi: "समस्या लिखें…",
    or: "ସମସ୍ୟା ଲେଖନ୍ତୁ…",
  },
  sending: { en: "Sending…", hi: "भेजा जा रहा है…", or: "ପଠାଯାଉଛି…" },
  incidentSubmitted: { en: "Reported. Thank you.", hi: "रिपोर्ट हो गया। धन्यवाद।", or: "ରିପୋର୍ଟ ହେଲା। ଧନ୍ୟବାଦ।" },
  micPermissionDenied: {
    en: "Microphone access denied. Try \"Type instead\".",
    hi: "माइक्रोफ़ोन की अनुमति नहीं मिली। \"टाइप करें\" आज़माएँ।",
    or: "ମାଇକ୍ରୋଫୋନ୍ ଅନୁମତି ମିଳିଲା ନାହିଁ। \"ଟାଇପ୍ କରନ୍ତୁ\" ବ୍ୟବହାର କରନ୍ତୁ।",
  },
}

export function translate(key: keyof typeof translations, language: LanguageCode): string {
  return translations[key]?.[language] ?? translations[key]?.en ?? key
}
