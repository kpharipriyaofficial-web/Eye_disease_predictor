"""Callbacks for early stopping and atomic model checkpointing."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import torch
from torch import nn, optim
from torch.optim.lr_scheduler import LRScheduler


class EarlyStopping:
    """Stop training after validation loss ceases to improve."""

    def __init__(self, patience: int, min_delta: float = 0.0) -> None:
        if patience < 1:
            raise ValueError("patience must be at least one.")
        if min_delta < 0:
            raise ValueError("min_delta cannot be negative.")
        self.patience = patience
        self.min_delta = min_delta
        self.best_value = float("inf")
        self.num_bad_epochs = 0
        self.should_stop = False

    def step(self, value: float) -> bool:
        """Record a validation value and return whether training should stop."""
        if value < self.best_value - self.min_delta:
            self.best_value = value
            self.num_bad_epochs = 0
        else:
            self.num_bad_epochs += 1
            self.should_stop = self.num_bad_epochs >= self.patience
        return self.should_stop

    def state_dict(self) -> dict[str, Any]:
        """Return serialisable callback state for training resumption."""
        return {
            "best_value": self.best_value,
            "num_bad_epochs": self.num_bad_epochs,
            "should_stop": self.should_stop,
        }

    def load_state_dict(self, state: dict[str, Any]) -> None:
        """Restore callback state from a checkpoint."""
        self.best_value = float(state["best_value"])
        self.num_bad_epochs = int(state["num_bad_epochs"])
        self.should_stop = bool(state["should_stop"])


class ModelCheckpoint:
    """Save the lowest-validation-loss checkpoint to disk."""

    def __init__(self, path: str | Path, min_delta: float = 0.0) -> None:
        if min_delta < 0:
            raise ValueError("min_delta cannot be negative.")
        self.path = Path(path)
        self.min_delta = min_delta
        self.best_value = float("inf")

    def step(self, value: float, state: dict[str, Any]) -> bool:
        """Save ``state`` when ``value`` improves and return whether it saved."""
        if value >= self.best_value - self.min_delta:
            return False

        self.best_value = value
        state["checkpoint"] = self.state_dict()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        torch.save(state, temporary_path)
        os.replace(temporary_path, self.path)
        return True

    def state_dict(self) -> dict[str, float]:
        """Return serialisable callback state."""
        return {"best_value": self.best_value}

    def load_state_dict(self, state: dict[str, Any]) -> None:
        """Restore callback state from a checkpoint."""
        self.best_value = float(state["best_value"])
