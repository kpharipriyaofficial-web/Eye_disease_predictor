"""Factory for constructing configured classification models."""

from __future__ import annotations

import importlib
from collections.abc import Sequence
from types import ModuleType

from torch import nn

from .baseline_cnn import BaselineCNN
from .resnet18 import ResNet18Classifier


def _load_config() -> ModuleType:
    """Import the project's ``config.py`` from supported project layouts."""
    for module_name in ("config", "src.config", "app.core.config"):
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError as error:
            if error.name != module_name:
                raise
    raise ModuleNotFoundError("Could not locate project config.py.")


def _get_setting(config: ModuleType, names: Sequence[str], default: object) -> object:
    """Return the first configured setting from a list of aliases."""
    for name in names:
        if hasattr(config, name):
            return getattr(config, name)
    return default


def build_model() -> nn.Module:
    """Build a classification model using settings defined in ``config.py``.

    Supported settings are ``MODEL_NAME``, ``NUM_CLASSES``, and ``DROPOUT``.
    ResNet-18 additionally accepts ``FREEZE_BACKBONE`` and
    ``UNFREEZE_LAYERS``. Common aliases are accepted for configuration
    compatibility.
    """
    config = _load_config()
    model_name = str(
        _get_setting(config, ("MODEL_NAME", "MODEL", "MODEL_TYPE"), "baseline_cnn")
    ).lower()
    num_classes = int(_get_setting(config, ("NUM_CLASSES", "N_CLASSES"), 4))
    dropout = float(_get_setting(config, ("DROPOUT", "DROPOUT_RATE"), 0.3))

    if model_name == "baseline_cnn":
        return BaselineCNN(num_classes=num_classes, dropout=dropout)

    if model_name == "resnet18":
        freeze_backbone = bool(
            _get_setting(config, ("FREEZE_BACKBONE", "FREEZE_FEATURES"), False)
        )
        unfreeze_layers = _get_setting(config, ("UNFREEZE_LAYERS",), ())
        if isinstance(unfreeze_layers, str):
            unfreeze_layers = (unfreeze_layers,)
        if not isinstance(unfreeze_layers, Sequence):
            raise TypeError("UNFREEZE_LAYERS must be a sequence of layer names.")
        return ResNet18Classifier(
            num_classes=num_classes,
            dropout=dropout,
            freeze_backbone=freeze_backbone,
            unfreeze_layers=unfreeze_layers,
        )

    raise ValueError(
        f"Unsupported MODEL_NAME '{model_name}'. "
        "Supported models: baseline_cnn, resnet18."
    )
