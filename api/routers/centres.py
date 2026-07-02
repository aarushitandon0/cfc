from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.db.repository import get_repository
from api.models.schemas import Centre

router = APIRouter(prefix="/centres", tags=["centres"])


@router.get("", response_model=list[Centre])
def list_centres() -> list[dict]:
    return get_repository().list_centres()


@router.get("/{centre_id}", response_model=Centre)
def get_centre(centre_id: str) -> dict:
    centre = get_repository().get_centre(centre_id)
    if centre is None:
        raise HTTPException(status_code=404, detail=f"Centre {centre_id!r} not found")
    return centre


@router.post("", response_model=Centre)
def create_or_update_centre(centre: Centre) -> dict:
    data = centre.model_dump(mode="json")
    get_repository().upsert_centre(data)
    return data
