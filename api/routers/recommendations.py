from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.db.repository import get_repository
from api.models.schemas import RecommendationStatus, RedistributionRecommendation

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RedistributionRecommendation])
def list_recommendations(
    status: RecommendationStatus | None = Query(default=None),
) -> list[dict]:
    return get_repository().list_recommendations(status=status.value if status else None)


@router.patch("/{recommendation_id}/approve", response_model=RedistributionRecommendation)
def approve_recommendation(recommendation_id: str) -> dict:
    return _set_status(recommendation_id, RecommendationStatus.approved)


@router.patch("/{recommendation_id}/reject", response_model=RedistributionRecommendation)
def reject_recommendation(recommendation_id: str) -> dict:
    return _set_status(recommendation_id, RecommendationStatus.rejected)


def _set_status(recommendation_id: str, status: RecommendationStatus) -> dict:
    repo = get_repository()
    recs = {r["recommendation_id"]: r for r in repo.list_recommendations()}
    rec = recs.get(recommendation_id)
    if rec is None:
        raise HTTPException(
            status_code=404, detail=f"Recommendation {recommendation_id!r} not found"
        )
    rec["status"] = status.value
    repo.upsert_recommendation(rec)
    return rec
