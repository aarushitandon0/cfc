from __future__ import annotations

from fastapi import APIRouter

from api.db.repository import get_repository
from api.models.schemas import StockItem

router = APIRouter(prefix="/stock-items", tags=["stock_items"])


@router.get("", response_model=list[StockItem])
def list_stock_items() -> list[dict]:
    return get_repository().list_stock_items()


@router.post("", response_model=StockItem)
def create_or_update_stock_item(item: StockItem) -> dict:
    data = item.model_dump(mode="json")
    get_repository().upsert_stock_item(data)
    return data
