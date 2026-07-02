"""Deterministic stand-in for Cloud Speech-to-Text + Translation API, used
until real GCP credentials are wired in (USE_REAL_SPEECH_APIS=true).

transcribe() decodes the uploaded bytes as UTF-8 text rather than running real
speech recognition - in mock mode the staff PWA sends the already-recognized
browser speech-input text as the "audio" payload, so this still exercises the
full request/response shape the real implementation will use.
"""

from __future__ import annotations

from api.services.speech_service import SpeechService

# A handful of canned PHC-incident phrases (Hindi/Odia) so demos translate to
# something realistic without calling the real Translation API.
_DEMO_TRANSLATIONS = {
    "दवाई कम है": "Medicine stock is low",
    "डॉक्टर साहब आज नहीं आये": "The doctor did not come in today",
    "बहुत मरीज आये हैं आज": "Many patients came in today",
    "टेस्ट किट खत्म हो गयी है": "Test kits have run out",
    "ବେଡ଼ ଖାଲି ନାହିଁ": "No beds are available",
}


class MockSpeechService(SpeechService):
    def transcribe(self, audio_bytes: bytes, language_code: str) -> str:
        try:
            return audio_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            return "[mock transcript - non-text audio payload received in mock mode]"

    def translate_to_english(self, text: str, source_language_code: str) -> str:
        if source_language_code.lower().startswith("en"):
            return text
        if text in _DEMO_TRANSLATIONS:
            return _DEMO_TRANSLATIONS[text]
        return f"[mock translation from {source_language_code}] {text}"
