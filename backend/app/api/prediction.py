"""Image-prediction API routes."""

from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.dependencies import get_current_user
from app.services.prediction_service import prediction_service


router = APIRouter(tags=["Predictions"])

_UPLOADS_DIRECTORY = Path(__file__).resolve().parents[1] / "uploads"


def _temporary_upload_path(image_name: str) -> Path:
    """Create a safe, unique temporary location for an uploaded image."""
    suffix = Path(image_name).suffix.lower()
    return _UPLOADS_DIRECTORY / f"{uuid4().hex}{suffix}"


def _remove_file(path: Path) -> None:
    """Remove a temporary upload if it remains on disk."""
    path.unlink(missing_ok=True)


@router.post("/predict")
async def predict_image(
    image: UploadFile = File(...),
    user: dict[str, object] = Depends(get_current_user),
) -> dict[str, str | float]:
    """Predict an eye condition from an uploaded image and record the result."""
    prediction_service.validate_content_type(image.content_type)

    image_name = Path(image.filename or "image").name
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded image is empty.",
        )

    _UPLOADS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    temporary_path = _temporary_upload_path(image_name)
    try:
        await asyncio.to_thread(temporary_path.write_bytes, image_bytes)
        return await prediction_service.predict_and_store(
            image_bytes=image_bytes,
            image_name=image_name,
            user_id=str(user["_id"]),
        )
    finally:
        await asyncio.to_thread(_remove_file, temporary_path)

