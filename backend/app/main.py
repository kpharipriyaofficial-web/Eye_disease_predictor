"""Deployment-ready FastAPI application entry point."""

from __future__ import annotations


from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.history import router as history_router
from app.api.prediction import router as prediction_router
from app.core.config import get_settings
from app.core.database import (
    close_mongodb_connection,
    connect_to_mongodb,
    database_manager,
)
from app.core.logging import configure_logging



def _cors_origins() -> list[str]:
    """Read permitted frontend origins from the environment."""
    return get_settings().cors_origins


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize shared database connection for this process."""

    await connect_to_mongodb()

    try:
        yield
    finally:
        await close_mongodb_connection()


# Configure application logging.
configure_logging()

# Load application settings.
settings = get_settings()


# Create FastAPI application.
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)


# Configure CORS for the frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers.
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
        status_code=(
            status.HTTP_200_OK
            if is_healthy
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        content=payload,
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_env.lower() == "development",
    )
