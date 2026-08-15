"""Optimizer and learning-rate scheduler construction."""

from __future__ import annotations

from typing import Any

from torch import nn, optim
from torch.optim.lr_scheduler import CosineAnnealingLR

from src.models.factory import _get_setting, _load_config


def _config_value(names: tuple[str, ...], default: Any) -> Any:
    """Read a training setting from ``config.py`` with compatible aliases."""
    return _get_setting(_load_config(), names, default)


def create_optimizer(model: nn.Module) -> optim.AdamW:
    """Create the configured AdamW optimiser for trainable parameters."""
    learning_rate = float(_config_value(("LEARNING_RATE", "LR"), 1e-3))
    weight_decay = float(_config_value(("WEIGHT_DECAY",), 1e-4))
    if learning_rate <= 0:
        raise ValueError("LEARNING_RATE must be greater than zero.")
    if weight_decay < 0:
        raise ValueError("WEIGHT_DECAY cannot be negative.")

    parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
    if not parameters:
        raise ValueError("Model has no trainable parameters.")
    return optim.AdamW(parameters, lr=learning_rate, weight_decay=weight_decay)


def create_scheduler(optimizer: optim.Optimizer) -> CosineAnnealingLR:
    """Create the configured cosine-annealing learning-rate scheduler."""
    t_max = int(_config_value(("COSINE_T_MAX", "T_MAX", "EPOCHS", "NUM_EPOCHS"), 10))
    eta_min = float(_config_value(("MIN_LEARNING_RATE", "ETA_MIN"), 0.0))
    if t_max <= 0:
        raise ValueError("COSINE_T_MAX must be greater than zero.")
    if eta_min < 0:
        raise ValueError("MIN_LEARNING_RATE cannot be negative.")
    return CosineAnnealingLR(optimizer, T_max=t_max, eta_min=eta_min)
