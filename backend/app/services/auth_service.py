"""Authentication services backed by MongoDB and JWT."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError

from app.core.database import get_database
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import USERS_COLLECTION, build_user_document
from app.schemas.auth import UserResponse


class AuthService:
    """Encapsulate credential, token, and user persistence operations."""

    @property
    def users(self) -> AsyncIOMotorCollection:
        """Return the users collection from the initialized database."""
        return get_database()[USERS_COLLECTION]

    async def ensure_indexes(self) -> None:
        """Create indexes needed to preserve user-account invariants."""
        await self.users.create_index("email", unique=True, name="unique_user_email")

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password with bcrypt."""
        return hash_password(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a plaintext password against its bcrypt hash."""
        return verify_password(password, password_hash)

    def create_access_token(self, user: dict[str, Any]) -> str:
        """Create a signed, time-limited token for a user."""
        return create_access_token(subject=str(user["_id"]), email=user["email"])

    async def create_user(self, *, email: str, password: str) -> dict[str, Any]:
        """Persist a new user with a bcrypt password hash."""
        await self.ensure_indexes()
        user = build_user_document(email=email, password_hash=self.hash_password(password))
        try:
            result = await self.users.insert_one(user)
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            ) from exc

        user["_id"] = result.inserted_id
        return user

    async def authenticate(self, *, email: str, password: str) -> dict[str, Any]:
        """Validate credentials and return the authenticated user."""
        user = await self.users.find_one({"email": email.lower()})
        if user is None or not self.verify_password(password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.get("is_active", False):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive.")
        return user

    @staticmethod
    def to_user_response(user: dict[str, Any]) -> UserResponse:
        """Convert a MongoDB user document to its public API schema."""
        return UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            is_active=user["is_active"],
            created_at=user["created_at"],
        )


auth_service = AuthService()

