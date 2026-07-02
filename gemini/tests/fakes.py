"""Fake genai.Client stand-in so gemini/ tests run without a real API key or
network call. Captures the prompt sent so tests can assert on it."""

from __future__ import annotations


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeModels:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.last_call: dict | None = None

    def generate_content(self, *, model: str, contents: str, config: dict | None = None) -> FakeResponse:
        self.last_call = {"model": model, "contents": contents, "config": config}
        return FakeResponse(self.response_text)


class FakeGenaiClient:
    def __init__(self, response_text: str = "ok") -> None:
        self.models = FakeModels(response_text)
