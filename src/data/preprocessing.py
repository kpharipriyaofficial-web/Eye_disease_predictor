"""OpenCV-based image loading and enhancement utilities."""

from __future__ import annotations

from pathlib import Path
from typing import TypeAlias

import cv2
import numpy as np
from PIL import Image

ImageArray: TypeAlias = np.ndarray


def apply_clahe(
    image_bgr: ImageArray,
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
) -> ImageArray:
    """Enhance luminance contrast with CLAHE while preserving colour channels.

    Args:
        image_bgr: An OpenCV BGR image with three colour channels.
        clip_limit: Threshold used to limit local histogram amplification.
        tile_grid_size: Size of the contextual regions used by CLAHE.

    Returns:
        The contrast-enhanced BGR image.

    Raises:
        ValueError: If ``image_bgr`` is not a three-channel image.
    """
    if image_bgr is None or image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError("CLAHE expects a three-channel BGR image.")

    lab_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    lightness, a_channel, b_channel = cv2.split(lab_image)
    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=tile_grid_size,
    )
    enhanced_lightness = clahe.apply(lightness)
    enhanced_lab = cv2.merge((enhanced_lightness, a_channel, b_channel))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)


def bgr_to_rgb(image_bgr: ImageArray) -> ImageArray:
    """Convert a three-channel BGR image to RGB."""
    if image_bgr is None or image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError("BGR-to-RGB conversion expects a three-channel image.")
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)


def load_image_cv2(
    image_path: str | Path,
    *,
    apply_contrast_enhancement: bool = True,
) -> ImageArray:
    """Load an image with OpenCV, optionally apply CLAHE, and return RGB data.

    The returned NumPy array is compatible with PIL and torchvision transforms.
    """
    path = Path(image_path)
    image_bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise FileNotFoundError(f"Unable to read image: {path}")

    if apply_contrast_enhancement:
        image_bgr = apply_clahe(image_bgr)
    return bgr_to_rgb(image_bgr)


def opencv_loader(image_path: str | Path) -> Image.Image:
    """ImageFolder-compatible loader returning a CLAHE-enhanced RGB PIL image."""
    return Image.fromarray(load_image_cv2(image_path))
