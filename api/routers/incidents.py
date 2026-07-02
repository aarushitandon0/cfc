"""Staff incident intake: voice or typed free-text notes become a tagged
Alert. Voice path: audio -> transcript (original language) -> English
translation -> Gemini tag extraction -> stored Alert. The original-language
transcript is preserved in source_metric for staff-facing display even though
tagging runs on the English translation, per the Layer 1 spec.
"""

from __future__ import annotations

import logging
import uuid
from datetime import date

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from api.db.repository import get_repository
from api.models.schemas import Alert, AlertStatus, Severity
from api.services.speech_service import get_speech_service
from gemini.incident_tagger import extract_incident_tags

router = APIRouter(prefix="/incidents", tags=["incidents"])
logger = logging.getLogger(__name__)


class TextIncidentRequest(BaseModel):
    centre_id: str
    language_code: str
    text: str


def _tag_incident(translated_text: str) -> dict:
    try:
        return extract_incident_tags(translated_text)
    except Exception:
        logger.warning("Gemini incident tagging failed; using untagged fallback", exc_info=True)
        return {
            "category": "other",
            "severity": "medium",
            "mentioned_medicine_names": [],
            "summary": translated_text[:280],
        }


def _build_alert(centre_id: str, original_text: str, translated_text: str, language_code: str) -> dict:
    tags = _tag_incident(translated_text)
    alert = Alert(
        alert_id=str(uuid.uuid4()),
        centre_id=centre_id,
        created_at=date.today(),
        category=tags["category"],
        severity=Severity(tags["severity"]),
        status=AlertStatus.open,
        message=tags["summary"],
        source_metric={
            "original_text": original_text,
            "translated_text": translated_text,
            "language_code": language_code,
            "mentioned_medicine_names": tags.get("mentioned_medicine_names", []),
        },
    )
    return alert.model_dump(mode="json")


@router.post("/voice", response_model=Alert)
async def submit_voice_incident(
    centre_id: str = Form(...),
    language_code: str = Form(...),
    audio: UploadFile = File(...),
) -> dict:
    speech_service = get_speech_service()
    audio_bytes = await audio.read()

    original_text = speech_service.transcribe(audio_bytes, language_code)
    translated_text = speech_service.translate_to_english(original_text, language_code)

    data = _build_alert(centre_id, original_text, translated_text, language_code)
    get_repository().upsert_alert(data)
    return data


@router.post("/text", response_model=Alert)
def submit_text_incident(payload: TextIncidentRequest) -> dict:
    speech_service = get_speech_service()
    translated_text = speech_service.translate_to_english(payload.text, payload.language_code)

    data = _build_alert(payload.centre_id, payload.text, translated_text, payload.language_code)
    get_repository().upsert_alert(data)
    return data
