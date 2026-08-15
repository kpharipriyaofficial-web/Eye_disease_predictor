"""CPU-only, process-wide eye-disease model predictor."""

from __future__ import annotations

import sys
from pathlib import Path
from threading import Lock
from typing import Any


# The trained model and its preprocessing pipeline live at the repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.inference.predictor import Predictor as ProjectPredictor  # noqa: E402


class EyeDiseasePredictor:
    """Adapt the ML project's predictor for the FastAPI backend."""

    def __init__(self) -> None:
        # ProjectPredictor reuses the project's CLAHE + evaluation transform and
        # loads saved_models/best_model.pt with map_location set to this device.
        self._predictor = ProjectPredictor(device="cpu")

    def predict(self, image_bytes: bytes) -> dict[str, str | float]:
        """Predict a disease class from uploaded image bytes."""
        result: dict[str, Any] = self._predictor.predict(image_bytes)
        return {
            "prediction": str(result["prediction"]),
            "confidence": float(result["confidence"]),
        }


_predictor: EyeDiseasePredictor | None = None
_predictor_lock = Lock()


def get_predictor() -> EyeDiseasePredictor:
    """Return the process-wide predictor, loading its model exactly once."""
    global _predictor
    if _predictor is None:
        with _predictor_lock:
            if _predictor is None:
                _predictor = EyeDiseasePredictor()
    return _predictor

