"""Real GCP Firestore implementation of Repository.

Authenticates via Application Default Credentials (run
`gcloud auth application-default login` locally, or rely on the Cloud Run
service identity in deployment). Project comes from GOOGLE_CLOUD_PROJECT.
Honors FIRESTORE_EMULATOR_HOST automatically if set (google-cloud-firestore
built-in behavior), so the same code path works against the emulator too.
"""

from __future__ import annotations

import os

from google.cloud import firestore

from api.db.repository import Repository

COLLECTIONS = (
    "centres",
    "stock_items",
    "daily_logs",
    "alerts",
    "redistribution_recommendations",
)


class FirestoreRepository(Repository):
    def __init__(self) -> None:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self._client = firestore.Client(project=project)

    # centres -----------------------------------------------------------

    def list_centres(self) -> list[dict]:
        return [doc.to_dict() for doc in self._client.collection("centres").stream()]

    def get_centre(self, centre_id: str) -> dict | None:
        doc = self._client.collection("centres").document(centre_id).get()
        return doc.to_dict() if doc.exists else None

    def upsert_centre(self, centre: dict) -> None:
        self._client.collection("centres").document(centre["centre_id"]).set(centre)

    # stock_items ---------------------------------------------------------

    def list_stock_items(self) -> list[dict]:
        return [doc.to_dict() for doc in self._client.collection("stock_items").stream()]

    def upsert_stock_item(self, item: dict) -> None:
        self._client.collection("stock_items").document(item["medicine_id"]).set(item)

    # daily_logs -----------------------------------------------------------

    def list_daily_logs(self, centre_id: str | None = None) -> list[dict]:
        col = self._client.collection("daily_logs")
        query = col.where("centre_id", "==", centre_id) if centre_id else col
        return [doc.to_dict() for doc in query.stream()]

    def upsert_daily_log(self, log: dict) -> None:
        self._client.collection("daily_logs").document(log["log_id"]).set(log)

    # alerts -----------------------------------------------------------

    def list_alerts(self, status: str | None = None) -> list[dict]:
        col = self._client.collection("alerts")
        query = col.where("status", "==", status) if status else col
        return [doc.to_dict() for doc in query.stream()]

    def upsert_alert(self, alert: dict) -> None:
        self._client.collection("alerts").document(alert["alert_id"]).set(alert)

    # redistribution_recommendations ---------------------------------------

    def list_recommendations(self, status: str | None = None) -> list[dict]:
        col = self._client.collection("redistribution_recommendations")
        query = col.where("status", "==", status) if status else col
        return [doc.to_dict() for doc in query.stream()]

    def upsert_recommendation(self, rec: dict) -> None:
        self._client.collection("redistribution_recommendations").document(
            rec["recommendation_id"]
        ).set(rec)

    def clear_all(self) -> None:
        for name in COLLECTIONS:
            for doc in self._client.collection(name).stream():
                doc.reference.delete()
