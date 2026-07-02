"""Speech-to-Text + Translation abstraction for the staff app voice path.

Two implementations: MockSpeechService (deterministic, no GCP credentials
needed - used for local dev/demo) and RealSpeechService (Cloud Speech-to-Text
+ Translation API). Selected via USE_REAL_SPEECH_APIS so the incidents router
never imports a GCP speech client directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

from api.config import settings


class SpeechService(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, language_code: str) -> str:
        """Converts spoken audio in `language_code` to text in that same language."""
        ...

    @abstractmethod
    def translate_to_english(self, text: str, source_language_code: str) -> str:
        """Translates `text` from `source_language_code` to English for processing."""
        ...


@lru_cache
def get_speech_service() -> SpeechService:
    if settings.use_real_speech_apis:
        from api.services.real_speech_service import RealSpeechService

        return RealSpeechService()
    from api.services.mock_speech_service import MockSpeechService

    return MockSpeechService()
