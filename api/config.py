"""Centralized settings, loaded from environment variables / .env."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # storage backend: "local" (JSON file, no GCP needed) or "firestore"
    db_backend: str = "local"
    google_cloud_project: str | None = None

    # Gemini (Google AI Studio key, see gemini/client.py)
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    # Speech-to-Text / Translation (Layer 1 voice path)
    use_real_speech_apis: bool = False

    cors_allow_origins: list[str] = ["http://localhost:5173", "http://localhost:5174"]


settings = Settings()
