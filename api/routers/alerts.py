from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.db.repository import get_repository
from api.models.schemas import Alert, AlertStatus

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[Alert])
def list_alerts(status: AlertStatus | None = Query(default=None)) -> list[dict]:
    return get_repository().list_alerts(status=status.value if status else None)


@router.post("", response_model=Alert)
def create_alert(alert: Alert) -> dict:
    data = alert.model_dump(mode="json")
    get_repository().upsert_alert(data)
    return data


@router.patch("/{alert_id}/resolve", response_model=Alert)
def resolve_alert(alert_id: str) -> dict:
    repo = get_repository()
    alerts = {a["alert_id"]: a for a in repo.list_alerts()}
    alert = alerts.get(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id!r} not found")
    alert["status"] = AlertStatus.resolved.value
    repo.upsert_alert(alert)
    return alert
