"""JSON-file-backed Repository implementation.

Used for hackathon local development and the test suite so the full stack
(generator -> seed -> API -> ML -> Gemini) can run end-to-end without GCP
credentials. Swap to FirestoreRepository in deployment via DB_BACKEND=firestore.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from api.db.repository import Repository

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "local_data" / "db.json"

_EMPTY_DB: dict = {
    "centres": {},
    "stock_items": {},
    "daily_logs": {},
    "alerts": {},
    "redistribution_recommendations": {},
}


class LocalJsonRepository(Repository):
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or Path(os.getenv("LOCAL_DB_PATH", str(DEFAULT_DB_PATH)))
        self._lock = threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write(_EMPTY_DB)

    def _read(self) -> dict:
        with self._lock:
            return json.loads(self._path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        with self._lock:
            self._path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    # centres -----------------------------------------------------------

    def list_centres(self) -> list[dict]:
        return list(self._read()["centres"].values())

    def get_centre(self, centre_id: str) -> dict | None:
        return self._read()["centres"].get(centre_id)

    def upsert_centre(self, centre: dict) -> None:
        data = self._read()
        data["centres"][centre["centre_id"]] = centre
        self._write(data)

    # stock_items ---------------------------------------------------------

    def list_stock_items(self) -> list[dict]:
        return list(self._read()["stock_items"].values())

    def upsert_stock_item(self, item: dict) -> None:
        data = self._read()
        data["stock_items"][item["medicine_id"]] = item
        self._write(data)

    # daily_logs -----------------------------------------------------------

    def list_daily_logs(self, centre_id: str | None = None) -> list[dict]:
        logs = list(self._read()["daily_logs"].values())
        if centre_id:
            logs = [log for log in logs if log["centre_id"] == centre_id]
        return logs

    def upsert_daily_log(self, log: dict) -> None:
        data = self._read()
        data["daily_logs"][log["log_id"]] = log
        self._write(data)

    # alerts -----------------------------------------------------------

    def list_alerts(self, status: str | None = None) -> list[dict]:
        alerts = list(self._read()["alerts"].values())
        if status:
            alerts = [a for a in alerts if a["status"] == status]
        return alerts

    def upsert_alert(self, alert: dict) -> None:
        data = self._read()
        data["alerts"][alert["alert_id"]] = alert
        self._write(data)

    # redistribution_recommendations ---------------------------------------

    def list_recommendations(self, status: str | None = None) -> list[dict]:
        recs = list(self._read()["redistribution_recommendations"].values())
        if status:
            recs = [r for r in recs if r["status"] == status]
        return recs

    def upsert_recommendation(self, rec: dict) -> None:
        data = self._read()
        data["redistribution_recommendations"][rec["recommendation_id"]] = rec
        self._write(data)

    def clear_all(self) -> None:
        self._write(json.loads(json.dumps(_EMPTY_DB)))
