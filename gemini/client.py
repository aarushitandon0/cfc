"""Thin wrapper around the Gemini API via the google-genai SDK (Google AI
Studio key, see api/config.py). This module and its siblings (summarizer,
alert_drafter, incident_tagger) only ever receive already-computed numbers
from ml/ - never raw daily_logs, and never asked to produce a forecast or
score themselves. The one exception is incident_tagger, which reads raw
free-text incident notes since no statistical model exists for that input.
"""

from __future__ import annotations

import json
from functools import lru_cache

from google import genai

from api.config import settings


@lru_cache
def get_client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Get a free key from https://aistudio.google.com/apikey "
            "and add it to your .env before calling the Gemini layer."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def generate_text(prompt: str, *, client: genai.Client | None = None) -> str:
    """Single text-generation call against the configured Gemini model."""
    active_client = client or get_client()
    response = active_client.models.generate_content(model=settings.gemini_model, contents=prompt)
    return (response.text or "").strip()


def generate_json(prompt: str, *, client: genai.Client | None = None) -> dict:
    """Text-generation call constrained to JSON output, parsed into a dict."""
    active_client = client or get_client()
    response = active_client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    return json.loads(response.text)
