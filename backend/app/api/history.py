"""Authenticated prediction-history API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.core.database import get_database
from app.dependencies import get_current_user
from app.models.prediction import PREDICTIONS_COLLECTION
from app.schemas.prediction import PredictionHistoryItem, PredictionHistoryResponse


router = APIRouter(prefix="/history", tags=["Prediction History"])


@router.get("", response_model=PredictionHistoryResponse)
async def get_prediction_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: dict[str, Any] = Depends(get_current_user),
) -> PredictionHistoryResponse:
    """Return the authenticated user's predictions, newest first."""
    user_id = str(user["_id"])
    filters = {"user_id": user_id}
    collection = get_database()[PREDICTIONS_COLLECTION]
    skip = (page - 1) * page_size

    documents = await (
        collection.find(filters)
        .sort("timestamp", -1)
        .skip(skip)
        .limit(page_size)
        .to_list(length=page_size)
    )
    total = await collection.count_documents(filters)

    return PredictionHistoryResponse(
        items=[
            PredictionHistoryItem(
                id=str(document["_id"]),
                prediction=document["prediction"],
                confidence=document["confidence"],
                timestamp=document["timestamp"],
                image_name=document["image_name"],
            )
            for document in documents
        ],
        page=page,
        page_size=page_size,
        total=total,
    )

