"""MongoDB connection management for the application."""

from __future__ import annotations

import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage the application's single asynchronous MongoDB client."""

    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None
        self._database: AsyncIOMotorDatabase | None = None

    @property
    def client(self) -> AsyncIOMotorClient:
        """Return the active Motor client."""
        if self._client is None:
            raise RuntimeError("MongoDB client has not been initialized.")
        return self._client

    @property
    def database(self) -> AsyncIOMotorDatabase:
        """Return the active application database."""
        if self._database is None:
            raise RuntimeError("MongoDB database has not been initialized.")
        return self._database

    async def connect(self) -> None:
        """Create and validate the singleton MongoDB connection."""
        if self._client is not None:
            return

        settings = get_settings()
        mongodb_uri = settings.require_mongodb_uri()

        client = AsyncIOMotorClient(
            mongodb_uri,
            serverSelectionTimeoutMS=settings.mongodb_server_selection_timeout_ms,
        )
        try:
            await client.admin.command("ping")
        except Exception:
            client.close()
            logger.exception("mongodb_connection_failed")
            raise

        self._client = client
        self._database = client[settings.mongodb_database]
        logger.info("mongodb_connected")

    async def disconnect(self) -> None:
        """Close the active MongoDB connection, if one exists."""
        if self._client is not None:
            self._client.close()

        self._client = None
        self._database = None
        logger.info("mongodb_disconnected")

    async def health_check(self) -> dict[str, Any]:
        """Verify MongoDB connectivity for health probes."""
        try:
            await self.client.admin.command("ping")
        except Exception as exc:
            return {"status": "unhealthy", "database": "mongodb", "detail": str(exc)}

        return {"status": "healthy", "database": "mongodb"}


database_manager = DatabaseManager()


async def connect_to_mongodb() -> None:
    """Application startup hook for MongoDB."""
    await database_manager.connect()


async def close_mongodb_connection() -> None:
    """Application shutdown hook for MongoDB."""
    await database_manager.disconnect()


def get_database() -> AsyncIOMotorDatabase:
    """Return the initialized MongoDB database for dependency injection."""
    return database_manager.database

