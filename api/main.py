"""FastAPI application entrypoint. All business logic lives in api/ and ml/;
Gemini calls are isolated in gemini/ and only ever invoked from the
orchestration router, never from CRUD routers."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import settings
from api.db.repository import get_repository
from api.routers import (
    alerts,
    centres,
    daily_logs,
    incidents,
    orchestration,
    recommendations,
    stock_items,
)

app = FastAPI(
    title="SwasthyaSetu API",
    description="AI-driven health centre management platform for district PHCs/CHCs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(centres.router)
app.include_router(stock_items.router)
app.include_router(daily_logs.router)
app.include_router(alerts.router)
app.include_router(recommendations.router)
app.include_router(incidents.router)
app.include_router(orchestration.router)


@app.get("/health", response_model=None)
def health_check() -> dict | JSONResponse:
    """Confirms the active DB backend is reachable and returns per-collection
    document counts (works for both local and firestore, since both implement
    the same Repository list methods)."""
    try:
        repo = get_repository()
        counts = {
            "centres": len(repo.list_centres()),
            "stock_items": len(repo.list_stock_items()),
            "daily_logs": len(repo.list_daily_logs()),
            "alerts": len(repo.list_alerts()),
            "redistribution_recommendations": len(repo.list_recommendations()),
        }
        return {"status": "ok", "db_backend": settings.db_backend, "document_counts": counts}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "db_backend": settings.db_backend, "error": str(exc)},
        )
