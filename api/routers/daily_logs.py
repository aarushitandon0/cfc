from __future__ import annotations

from fastapi import APIRouter, Query

from api.db.repository import get_repository
from api.models.schemas import DailyLog

router = APIRouter(prefix="/daily-logs", tags=["daily_logs"])


@router.get("", response_model=list[DailyLog])
def list_daily_logs(centre_id: str | None = Query(default=None)) -> list[dict]:
    return get_repository().list_daily_logs(centre_id=centre_id)


@router.post("", response_model=DailyLog)
def create_or_update_daily_log(log: DailyLog) -> dict:
    data = log.model_dump(mode="json")
    get_repository().upsert_daily_log(data)
    return data
