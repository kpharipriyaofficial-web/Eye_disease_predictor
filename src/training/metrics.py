"""Classification metrics implemented with PyTorch tensors."""

from __future__ import annotations

from dataclasses import dataclass, field

import torch
from torch import Tensor


@dataclass
class ClassificationMetrics:
    """Accumulate predictions and compute multi-class classification metrics."""

    num_classes: int
    confusion_matrix: Tensor = field(init=False)
    _correct: int = field(default=0, init=False)
    _total: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        """Initialise an integer confusion matrix."""
        if self.num_classes <= 0:
            raise ValueError("num_classes must be greater than zero.")
        self.confusion_matrix = torch.zeros(
            (self.num_classes, self.num_classes),
            dtype=torch.long,
        )

    def update(self, logits: Tensor, targets: Tensor) -> None:
        """Add a model batch to the accumulated statistics.

        Rows of the confusion matrix denote actual classes; columns denote
        predicted classes.
        """
        predictions = logits.detach().argmax(dim=1).reshape(-1).to("cpu")
        target_values = targets.detach().reshape(-1).to("cpu", dtype=torch.long)
        if predictions.numel() != target_values.numel():
            raise ValueError("logits and targets must have matching batch sizes.")
        if target_values.numel() == 0:
            return
        if (
            target_values.min() < 0
            or target_values.max() >= self.num_classes
            or predictions.min() < 0
            or predictions.max() >= self.num_classes
        ):
            raise ValueError("predictions or targets contain an invalid class index.")

        self._correct += int((predictions == target_values).sum().item())
        self._total += target_values.numel()
        flattened_indices = target_values * self.num_classes + predictions
        batch_matrix = torch.bincount(
            flattened_indices,
            minlength=self.num_classes**2,
        ).reshape(self.num_classes, self.num_classes)
        self.confusion_matrix += batch_matrix

    def compute(self) -> dict[str, float | Tensor]:
        """Return accuracy plus macro precision, recall, F1, and confusion matrix."""
        matrix = self.confusion_matrix.to(dtype=torch.float32)
        true_positives = matrix.diag()
        false_positives = matrix.sum(dim=0) - true_positives
        false_negatives = matrix.sum(dim=1) - true_positives

        precision_per_class = true_positives / (true_positives + false_positives)
        recall_per_class = true_positives / (true_positives + false_negatives)
        precision_per_class = torch.nan_to_num(precision_per_class, nan=0.0)
        recall_per_class = torch.nan_to_num(recall_per_class, nan=0.0)
        f1_per_class = 2 * precision_per_class * recall_per_class / (
            precision_per_class + recall_per_class
        )
        f1_per_class = torch.nan_to_num(f1_per_class, nan=0.0)

        accuracy = self._correct / self._total if self._total else 0.0
        return {
            "accuracy": accuracy,
            "precision": float(precision_per_class.mean().item()),
            "recall": float(recall_per_class.mean().item()),
            "f1": float(f1_per_class.mean().item()),
            "confusion_matrix": self.confusion_matrix.clone(),
        }
