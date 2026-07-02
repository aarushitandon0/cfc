"""Storage-backend-agnostic repository interface over the 5 Firestore collections.

Two implementations exist: LocalJsonRepository (file-backed, used for hackathon
local dev/testing without GCP credentials) and FirestoreRepository (real GCP
Firestore, used in deployment). Both are selected here via DB_BACKEND so that
api/ and ml/ never import a Firestore client directly.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from functools import lru_cache


class Repository(ABC):
    """CRUD surface needed by the API layer, implemented per backend."""

    # centres
    @abstractmethod
    def list_centres(self) -> list[dict]: ...

    @abstractmethod
    def get_centre(self, centre_id: str) -> dict | None: ...

    @abstractmethod
    def upsert_centre(self, centre: dict) -> None: ...

    # stock_items
    @abstractmethod
    def list_stock_items(self) -> list[dict]: ...

    @abstractmethod
    def upsert_stock_item(self, item: dict) -> None: ...

    # daily_logs
    @abstractmethod
    def list_daily_logs(self, centre_id: str | None = None) -> list[dict]: ...

    @abstractmethod
    def upsert_daily_log(self, log: dict) -> None: ...

    # alerts
    @abstractmethod
    def list_alerts(self, status: str | None = None) -> list[dict]: ...

    @abstractmethod
    def upsert_alert(self, alert: dict) -> None: ...

    # redistribution_recommendations
    @abstractmethod
    def list_recommendations(self, status: str | None = None) -> list[dict]: ...

    @abstractmethod
    def upsert_recommendation(self, rec: dict) -> None: ...

    @abstractmethod
    def clear_all(self) -> None:
        """Used only by the seed script to reset a backend before reseeding."""
        ...


@lru_cache
def get_repository() -> Repository:
    backend = os.getenv("DB_BACKEND", "local").lower()
    if backend == "firestore":
        from api.db.firestore_repository import FirestoreRepository

        return FirestoreRepository()
    if backend == "local":
        from api.db.local_repository import LocalJsonRepository

        return LocalJsonRepository()
    raise ValueError(f"Unknown DB_BACKEND: {backend!r} (expected 'local' or 'firestore')")
