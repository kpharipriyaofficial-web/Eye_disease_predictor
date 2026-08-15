"""Deployment-ready FastAPI application entry point."""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.history import router as history_router
from app.api.prediction import router as prediction_router
from app.core.database import (
    close_mongodb_connection,
    connect_to_mongodb,
    database_manager,
)
from app.ml.predictor import get_predictor


def _cors_origins() -> list[str]:
    """Read permitted frontend origins from the environment."""
    configured_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize shared database and ML dependencies for this process."""
    await connect_to_mongodb()
    try:
        # Loading PyTorch weights is synchronous; keep the event loop responsive.
        await asyncio.to_thread(get_predictor)
        yield
    finally:
        await close_mongodb_connection()


app = FastAPI(
    title=os.getenv("APP_NAME", "AI Eye Disease Detection API"),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(prediction_router)
app.include_router(history_router)


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """Report API readiness and MongoDB connectivity."""
    database_health = await database_manager.health_check()
    is_healthy = database_health["status"] == "healthy"
    payload = {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": database_health,
        "model": "loaded",
    }
    return JSONResponse(
        status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload,
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("APP_ENV", "development").lower() == "development",
    )
