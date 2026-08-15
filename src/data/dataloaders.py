"""DataLoader construction for eye disease classification datasets."""

from __future__ import annotations

from typing import Any

from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

from .datasets import (
    _load_config,
    get_datasets,
    get_test_dataset,
    get_train_dataset,
    get_validation_dataset,
)


def _get_config_value(name: str) -> Any:
    """Read a required loader setting from ``config.py``."""
    config = _load_config()
    if not hasattr(config, name):
        raise AttributeError(f"config.py must define {name}.")
    return getattr(config, name)


def _build_loader(dataset: ImageFolder, *, shuffle: bool) -> DataLoader:
    """Create one DataLoader using project-level loader settings."""
    batch_size = int(_get_config_value("BATCH_SIZE"))
    num_workers = int(_get_config_value("NUM_WORKERS"))
    pin_memory = bool(_get_config_value("PIN_MEMORY"))

    if batch_size <= 0:
        raise ValueError("BATCH_SIZE must be greater than zero.")
    if num_workers < 0:
        raise ValueError("NUM_WORKERS cannot be negative.")

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=num_workers > 0,
    )


def get_dataloaders() -> dict[str, DataLoader]:
    """Build train, validation, and test DataLoaders from configured datasets."""
    datasets = get_datasets()
    return {
        "train": _build_loader(datasets["train"], shuffle=True),
        "val": _build_loader(datasets["val"], shuffle=False),
        "test": _build_loader(datasets["test"], shuffle=False),
    }


def get_train_loader() -> DataLoader:
    """Build the training DataLoader."""
    return _build_loader(get_train_dataset(), shuffle=True)


def get_validation_loader() -> DataLoader:
    """Build the validation DataLoader."""
    return _build_loader(get_validation_dataset(), shuffle=False)


def get_test_loader() -> DataLoader:
    """Build the test DataLoader."""
    return _build_loader(get_test_dataset(), shuffle=False)
