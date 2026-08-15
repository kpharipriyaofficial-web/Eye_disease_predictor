"""Dataset construction for the train, validation, and test splits."""

from __future__ import annotations

import importlib
from pathlib import Path
from types import ModuleType

from torchvision.datasets import ImageFolder

from .preprocessing import opencv_loader
from .transforms import get_eval_transform, get_train_transform

_PATH_SETTING_NAMES: dict[str, tuple[str, ...]] = {
    "train": ("TRAIN_DATA_DIR", "TRAIN_DIR", "TRAIN_DATASET_DIR"),
    "val": ("VAL_DATA_DIR", "VALIDATION_DATA_DIR", "VAL_DIR", "VALIDATION_DIR"),
    "test": ("TEST_DATA_DIR", "TEST_DIR", "TEST_DATASET_DIR"),
}


def _load_config() -> ModuleType:
    """Import the project's configuration module without binding to one layout."""
    for module_name in ("config", "src.config", "app.core.config"):
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError as error:
            if error.name != module_name:
                raise
    raise ModuleNotFoundError("Could not locate project config.py.")


def get_dataset_path(split: str) -> Path:
    """Get and validate a split directory configured in ``config.py``."""
    normalized_split = split.lower()
    if normalized_split not in _PATH_SETTING_NAMES:
        raise ValueError("split must be one of: train, val, test")

    config = _load_config()
    for setting_name in _PATH_SETTING_NAMES[normalized_split]:
        configured_path = getattr(config, setting_name, None)
        if configured_path:
            dataset_path = Path(configured_path).expanduser()
            if not dataset_path.is_dir():
                raise FileNotFoundError(
                    f"Configured {setting_name} directory does not exist: "
                    f"{dataset_path}"
                )
            return dataset_path

    expected = ", ".join(_PATH_SETTING_NAMES[normalized_split])
    raise AttributeError(
        f"config.py must define one of these settings for {normalized_split}: "
        f"{expected}."
    )


def get_dataset(split: str) -> ImageFolder:
    """Create an ImageFolder dataset for a configured split."""
    normalized_split = split.lower()
    if normalized_split == "train":
        transform = get_train_transform()
    elif normalized_split in {"val", "test"}:
        transform = get_eval_transform()
    else:
        raise ValueError("split must be one of: train, val, test")

    return ImageFolder(
        root=str(get_dataset_path(normalized_split)),
        loader=opencv_loader,
        transform=transform,
    )


def get_train_dataset() -> ImageFolder:
    """Create the training dataset."""
    return get_dataset("train")


def get_validation_dataset() -> ImageFolder:
    """Create the validation dataset."""
    return get_dataset("val")


def get_test_dataset() -> ImageFolder:
    """Create the test dataset."""
    return get_dataset("test")


def get_datasets() -> dict[str, ImageFolder]:
    """Create datasets for every configured split."""
    datasets = {
        "train": get_train_dataset(),
        "val": get_validation_dataset(),
        "test": get_test_dataset(),
    }
    reference_mapping = datasets["train"].class_to_idx
    for split_name in ("val", "test"):
        if datasets[split_name].class_to_idx != reference_mapping:
            raise ValueError(
                "All dataset splits must contain identical class directories and "
                "ImageFolder mappings. "
                f"Mismatch found in the {split_name} split."
            )
    configured_classes = getattr(_load_config(), "CLASS_NAMES", None)
    if configured_classes is not None:
        if isinstance(configured_classes, str):
            configured_classes = tuple(
                name.strip() for name in configured_classes.split(",") if name.strip()
            )
        if tuple(configured_classes) != tuple(datasets["train"].classes):
            raise ValueError(
                "CLASS_NAMES must match ImageFolder's alphabetically sorted "
                "class-directory order."
            )
    return datasets
