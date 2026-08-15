"""Reusable FastAPI dependency providers."""

from __future__ import annotations

from typing import Any, Annotated

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.security import TokenValidationError, decode_access_token
from app.models.user import USERS_COLLECTION


bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> AsyncIOMotorDatabase:
    """Provide the initialized MongoDB database to route dependencies."""
    return get_database()


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> dict[str, Any]:
    """Require a valid access token and return its active MongoDB user."""

    print("=" * 50)

    if credentials is None:
        print("No Authorization header received.")
        raise _credentials_exception()

    print("Received token:", credentials.credentials)

    try:
        payload = decode_access_token(credentials.credentials)
        print("Decoded payload:", payload)

        user_id = ObjectId(payload["sub"])
        print("ObjectId:", user_id)

    except Exception as e:
        print("Token decode failed:", repr(e))
        raise _credentials_exception()

    user = await database[USERS_COLLECTION].find_one({"_id": user_id})

    print("Mongo user:", user)

    if user is None:
        print("User not found.")
        raise _credentials_exception()

    if not user.get("is_active", False):
        print("User inactive.")
        raise _credentials_exception()

    print("Authentication successful.")

    return user
