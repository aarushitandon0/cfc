"""Real Cloud Speech-to-Text + Translation API implementation. Activated by
setting USE_REAL_SPEECH_APIS=true once Speech-to-Text and Translation are
enabled on your GCP project and Application Default Credentials are set up.
"""

from __future__ import annotations

from google.cloud import speech, translate_v2

from api.services.speech_service import SpeechService


class RealSpeechService(SpeechService):
    def __init__(self) -> None:
        self._speech_client = speech.SpeechClient()
        self._translate_client = translate_v2.Client()

    def transcribe(self, audio_bytes: bytes, language_code: str) -> str:
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            language_code=language_code,
        )
        response = self._speech_client.recognize(config=config, audio=audio)
        return " ".join(result.alternatives[0].transcript for result in response.results)

    def translate_to_english(self, text: str, source_language_code: str) -> str:
        if source_language_code.lower().startswith("en"):
            return text
        result = self._translate_client.translate(
            text, source_language=source_language_code, target_language="en"
        )
        return result["translatedText"]
