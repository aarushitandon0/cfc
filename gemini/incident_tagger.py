"""Structured tag extraction from free-text staff incident reports.

This is the one Gemini path that reads raw text (the incident note itself),
since there is no statistical model that could tag free text - but it still
never touches stock/footfall numbers or produces a forecast/score.
"""

from __future__ import annotations

from gemini.client import generate_json

INCIDENT_TAG_PROMPT = """You are extracting structured tags from a free-text incident
note written by PHC/CHC staff. Read the note and return strict JSON with these keys:
- category: one of ["stockout", "equipment", "staffing", "patient_safety", "infrastructure", "other"]
- severity: one of ["low", "medium", "high"]
- mentioned_medicine_names: array of medicine/equipment names mentioned, if any
- summary: a single sentence summary in English, regardless of the note's original language

Incident note:
\"\"\"{note}\"\"\"

Return only the JSON object, nothing else.
"""


def extract_incident_tags(raw_incident_text: str, *, client=None) -> dict:
    if not raw_incident_text.strip():
        raise ValueError("incident text is empty")
    prompt = INCIDENT_TAG_PROMPT.format(note=raw_incident_text)
    return generate_json(prompt, client=client)
