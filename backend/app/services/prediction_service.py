"""Asynchronous service for image-based model predictions."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile, status

from app.core.database import get_database
from app.ml.predictor import get_predictor
from app.models.prediction import PREDICTIONS_COLLECTION, build_prediction_document


_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class PredictionService:
    """Validate uploaded images and execute synchronous ML inference safely."""

    async def predict_upload(
        self,
        image: UploadFile,
        *,
        user_id: str,
    ) -> dict[str, str | float]:
        """Read, predict, and persist a user-uploaded image."""
        self.validate_content_type(image.content_type)
        image_bytes = await image.read()
        return await self.predict_and_store(
            image_bytes=image_bytes,
            image_name=image.filename or "image",
            user_id=user_id,
        )

    async def predict_and_store(
        self,
        *,
        image_bytes: bytes,
        image_name: str,
        user_id: str,
    ) -> dict[str, str | float]:
        """Run inference for image bytes and save the prediction in MongoDB."""
        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The uploaded image is empty.",
            )

        result = await self.predict_bytes(image_bytes)
        timestamp = datetime.now(timezone.utc)
        await get_database()[PREDICTIONS_COLLECTION].insert_one(
            build_prediction_document(
                user_id=user_id,
                prediction=str(result["prediction"]),
                confidence=float(result["confidence"]),
                timestamp=timestamp,
                image_name=image_name,
            )
        )
        return {
            "prediction": str(result["prediction"]),
            "confidence": float(result["confidence"]),
            "timestamp": timestamp.isoformat(),
            "image_name": image_name,
        }

    @staticmethod
    def validate_content_type(content_type: str | None) -> None:
        """Accept only formats supported by the prediction API."""
        if content_type not in _ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only image uploads are supported.",
            )

    async def predict_bytes(self, image_bytes: bytes) -> dict[str, str | float]:
        """Run inference for already-read image bytes without blocking the event loop."""
        try:
            return await asyncio.to_thread(self._predict_bytes, image_bytes)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The uploaded file is not a valid RGB image.",
            ) from exc

    @staticmethod
    def _predict_bytes(image_bytes: bytes) -> dict[str, str | float]:
        """Run the shared CPU predictor in a worker thread."""
        return get_predictor().predict(image_bytes)


prediction_service = PredictionService()

