"""Train an eye disease classification model from the project root.

Run with::

    python scripts/train.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType

import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.dataloaders import get_dataloaders
from src.models.factory import _load_config, build_model
from src.training.trainer import Trainer


def _set_default(config: ModuleType, name: str, value: object) -> None:
    """Set a configuration default without overriding a user setting."""
    if not hasattr(config, name):
        setattr(config, name, value)


def configure_defaults(config: ModuleType) -> None:
    """Populate safe defaults so the training entry point is immediately runnable.

    Values already declared in ``config.py`` always take precedence. The dataset
    defaults match the repository's ``datasets/train``, ``datasets/val``, and
    ``datasets/test`` layout.
    """
    dataset_root = PROJECT_ROOT / "datasets"
    defaults: dict[str, object] = {
        "TRAIN_DATA_DIR": dataset_root / "train",
        "VAL_DATA_DIR": dataset_root / "val",
        "TEST_DATA_DIR": dataset_root / "test",
        "BATCH_SIZE": 32,
        "NUM_WORKERS": 0,
        "PIN_MEMORY": torch.cuda.is_available(),
        "MODEL_NAME": "baseline_cnn",
        "DROPOUT": 0.3,
        "EPOCHS": 10,
        "LEARNING_RATE": 1e-3,
        "WEIGHT_DECAY": 1e-4,
        "COSINE_T_MAX": 10,
        "MIN_LEARNING_RATE": 0.0,
        "AMP": torch.cuda.is_available(),
        "GRADIENT_CLIP_NORM": 1.0,
        "EARLY_STOPPING_PATIENCE": 5,
        "EARLY_STOPPING_MIN_DELTA": 0.0,
        "BEST_MODEL_PATH": PROJECT_ROOT / "saved_models" / "best_model.pt",
        "RESUME_TRAINING": False,
    }
    for name, value in defaults.items():
        _set_default(config, name, value)


def _validate_datasets(loaders: dict[str, DataLoader]) -> int:
    """Validate split class mappings and return the configured class count."""
    train_dataset = loaders["train"].dataset
    validation_dataset = loaders["val"].dataset
    test_dataset = loaders["test"].dataset
    if (
        train_dataset.class_to_idx != validation_dataset.class_to_idx
        or train_dataset.class_to_idx != test_dataset.class_to_idx
    ):
        raise ValueError("Train, validation, and test splits must share class names.")
    return len(train_dataset.classes)


def main() -> None:
    """Create data, model, and trainer before running the complete workflow."""
    config = _load_config()
    configure_defaults(config)

    dataloaders = get_dataloaders()
    detected_num_classes = _validate_datasets(dataloaders)
    _set_default(config, "NUM_CLASSES", detected_num_classes)
    if int(config.NUM_CLASSES) != detected_num_classes:
        raise ValueError(
            f"NUM_CLASSES ({config.NUM_CLASSES}) does not match the "
            f"{detected_num_classes} dataset classes."
        )

    model = build_model()
    trainer = Trainer(
        model=model,
        train_loader=dataloaders["train"],
        validation_loader=dataloaders["val"],
    )
    trainer.train()
    print(f"Best model saved to: {trainer.checkpoint.path}")


if __name__ == "__main__":
    main()
