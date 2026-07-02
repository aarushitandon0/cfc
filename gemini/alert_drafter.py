"""Drafts human-readable alert messages from precomputed alert metrics
(category, severity, source_metric) - these are decided upstream by ml/ or a
rules layer; Gemini only phrases them, it never sets severity or category.
"""

from __future__ import annotations

from gemini.client import generate_text


def draft_alert_message(
    category: str,
    severity: str,
    centre_name: str,
    source_metric: dict,
    language: str = "English",
    *,
    client=None,
) -> str:
    prompt = (
        f"Write a single short alert sentence in {language} for a district health "
        f"dashboard. The severity and category below are already decided - use them "
        f"exactly as given, do not change or reinterpret them.\n\n"
        f"Centre: {centre_name}\n"
        f"Category: {category}\n"
        f"Severity: {severity}\n"
        f"Supporting data: {source_metric}\n\n"
        f"Output only the sentence, no preamble."
    )
    return generate_text(prompt, client=client)
