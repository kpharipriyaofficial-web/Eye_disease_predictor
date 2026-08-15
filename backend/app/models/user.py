"""MongoDB document model helpers for users."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


USERS_COLLECTION = "users"


def build_user_document(*, email: str, password_hash: str) -> dict[str, Any]:
    """Build the MongoDB document stored for a newly registered user."""
    now = datetime.now(timezone.utc)
    return {
        "email": email.lower(),
        "password_hash": password_hash,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

