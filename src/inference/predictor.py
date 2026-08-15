"""FastAPI-ready single-image inference for eye disease classification."""

from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from types import ModuleType
from typing import Any, Sequence

import cv2
import numpy as np
import torch
from PIL import Image

from src.data.preprocessing import apply_clahe, bgr_to_rgb, opencv_loader
from src.data.transforms import get_eval_transform
from src.models.factory import _get_setting, _load_config, build_model


def _set_default(config: ModuleType, name: str, value: object) -> None:
    """Set a configuration default without overwriting an explicit value."""
    if not hasattr(config, name):
        setattr(config, name, value)


def _discover_class_names(project_root: Path) -> tuple[str, ...]:
    """Read ImageFolder's sorted class order from the available dataset split."""
    for split in ("train", "val", "test"):
        split_path = project_root / "datasets" / split
        if split_path.is_dir():
            class_names = tuple(
                sorted(path.name for path in split_path.iterdir() if path.is_dir())
            )
            if class_names:
                return class_names
    raise FileNotFoundError(
        "Unable to discover classes. Define CLASS_NAMES in config.py or provide "
        "class_names when constructing Predictor."
    )


class Predictor:
    """Load a trained model once and serve predictions for individual images."""

    def __init__(
        self,
        *,
        class_names: Sequence[str] | None = None,
        device: str | torch.device | None = None,
    ) -> None:
        """Load the configured best checkpoint and prepare its eval transform."""
        self.config = _load_config()
        project_root = Path(__file__).resolve().parents[2]
        configured_names = _get_setting(self.config, ("CLASS_NAMES",), None)
        if class_names is not None:
            self.class_names = tuple(class_names)
        elif configured_names is not None:
            if isinstance(configured_names, str):
                self.class_names = tuple(
                    name.strip() for name in configured_names.split(",") if name.strip()
                )
            else:
                self.class_names = tuple(configured_names)
        else:
            self.class_names = _discover_class_names(project_root)
        if not self.class_names:
            raise ValueError("At least one class name is required for prediction.")

        _set_default(self.config, "NUM_CLASSES", len(self.class_names))
        if int(self.config.NUM_CLASSES) != len(self.class_names):
            raise ValueError("NUM_CLASSES does not match the number of class names.")
        _set_default(self.config, "MODEL_NAME", "baseline_cnn")
        _set_default(self.config, "DROPOUT", 0.3)
        _set_default(
            self.config,
            "BEST_MODEL_PATH",
            project_root / "saved_models" / "best_model.pt",
        )

        configured_device = _get_setting(self.config, ("DEVICE",), None)
        selected_device = device or configured_device
        if selected_device is None:
            selected_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(selected_device)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available.")

        self.model = build_model().to(self.device)
        self.model.eval()
        self.transform = get_eval_transform()
        self.checkpoint_path = Path(
            _get_setting(
                self.config,
                ("BEST_MODEL_PATH", "CHECKPOINT_PATH", "MODEL_SAVE_PATH"),
                "saved_models/best_model.pt",
            )
        )
        self.last_inference_time_ms = 0.0
        self._load_model_weights()

    def _load_model_weights(self) -> None:
        """Load model weights once from the best-model checkpoint."""
        if not self.checkpoint_path.is_file():
            raise FileNotFoundError(
                f"Trained model checkpoint does not exist: {self.checkpoint_path}"
            )
        try:
            checkpoint: Any = torch.load(
                self.checkpoint_path,
                map_location=self.device,
                weights_only=False,
            )
        except TypeError:
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        state_dict = checkpoint.get("model_state_dict", checkpoint)
        self.model.load_state_dict(state_dict)
        self.model.eval()

    @staticmethod
    def _decode_image(image: bytes | bytearray | np.ndarray) -> Image.Image:
        """Decode uploaded image bytes or an OpenCV BGR image into RGB PIL data."""
        if isinstance(image, (bytes, bytearray)):
            image_array = np.frombuffer(image, dtype=np.uint8)
            image_bgr = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        else:
            image_bgr = image
        if image_bgr is None:
            raise ValueError("Unable to decode the supplied image.")
        if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
            raise ValueError("The supplied image must have three colour channels.")
        return Image.fromarray(bgr_to_rgb(apply_clahe(image_bgr)))

    def _prepare_image(
        self,
        image: str | Path | bytes | bytearray | np.ndarray | Image.Image,
    ) -> torch.Tensor:
        """Load and transform one image into a batched tensor."""
        if isinstance(image, (str, Path)):
            pil_image = opencv_loader(image)
        elif isinstance(image, Image.Image):
            image_rgb = np.asarray(image.convert("RGB"))
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            pil_image = Image.fromarray(bgr_to_rgb(apply_clahe(image_bgr)))
        else:
            pil_image = self._decode_image(image)
        return self.transform(pil_image).unsqueeze(0).to(self.device)

    @torch.inference_mode()
    def predict(
        self,
        image: str | Path | bytes | bytearray | np.ndarray | Image.Image,
    ) -> dict[str, str | float]:
        """Predict one eye image and return its label, confidence, and latency.

        ``image`` accepts a filesystem path, raw bytes from a FastAPI upload,
        an OpenCV BGR array, or a PIL image.
        """
        inputs = self._prepare_image(image)
        if self.device.type == "cuda":
            torch.cuda.synchronize(self.device)
        start_time = perf_counter()
        logits = self.model(inputs)
        probabilities = torch.softmax(logits, dim=1)
        confidence, prediction_index = probabilities.max(dim=1)
        if self.device.type == "cuda":
            torch.cuda.synchronize(self.device)
        self.last_inference_time_ms = (perf_counter() - start_time) * 1_000

        class_index = int(prediction_index.item())
        return {
            "prediction": self.class_names[class_index],
            "confidence": round(float(confidence.item() * 100), 2),
            "inference_time_ms": round(self.last_inference_time_ms, 2),
        }


@lru_cache(maxsize=1)
def get_predictor() -> Predictor:
    """Return a process-wide predictor singleton for FastAPI dependencies."""
    return Predictor()


def main() -> None:
    """Run single-image inference from the command line."""
    parser = argparse.ArgumentParser(
        description="Predict an eye disease class for one image."
    )
    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Path to the eye image to classify.",
    )
    arguments = parser.parse_args()
    if not arguments.image.is_file():
        parser.error(f"Image file does not exist: {arguments.image}")

    result = get_predictor().predict(arguments.image)
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {float(result['confidence']):.2f}%")
    print(f"Inference Time: {float(result['inference_time_ms']):.2f} ms")


if __name__ == "__main__":
    main()
