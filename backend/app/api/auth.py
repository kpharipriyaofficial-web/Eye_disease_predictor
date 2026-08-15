"""Authentication API routes."""

from typing import Any

from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    SignupRequest,
    UserResponse,
)
from app.services.auth_service import auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(payload: SignupRequest) -> AuthResponse:
    """Create an account and return an access token."""

    user = await auth_service.create_user(
        email=payload.email,
        password=payload.password,
    )

    return AuthResponse(
        access_token=auth_service.create_access_token(user),
        user=auth_service.to_user_response(user),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
async def login(payload: LoginRequest) -> AuthResponse:
    """Authenticate a user and return an access token."""

    user = await auth_service.authenticate(
        email=payload.email,
        password=payload.password,
    )

    return AuthResponse(
        access_token=auth_service.create_access_token(user),
        user=auth_service.to_user_response(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
async def read_current_user(
    user: dict[str, Any] = Depends(get_current_user),
) -> UserResponse:
    """Return the current authenticated user."""

    return auth_service.to_user_response(user)
