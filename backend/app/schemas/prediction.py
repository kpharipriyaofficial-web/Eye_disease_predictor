"""Response schemas for prediction records and history."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """Public representation of one prediction."""

    prediction: str
    confidence: float
    timestamp: datetime
    image_name: str


class PredictionHistoryItem(PredictionResponse):
    """A persisted prediction returned in a user's history."""

    id: str


class PredictionHistoryResponse(BaseModel):
    """Paginated result set for a user's prediction history."""

    items: list[PredictionHistoryItem]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)

