"""MongoDB document helpers for persisted model predictions."""

from __future__ import annotations

from datetime import datetime
from typing import Any


PREDICTIONS_COLLECTION = "predictions"


def build_prediction_document(
    *,
    user_id: str,
    prediction: str,
    confidence: float,
    timestamp: datetime,
    image_name: str,
) -> dict[str, Any]:
    """Build the MongoDB document stored for a completed prediction."""
    return {
        "user_id": user_id,
        "prediction": prediction,
        "confidence": confidence,
        "timestamp": timestamp,
        "image_name": image_name,
    }

