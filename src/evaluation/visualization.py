"""Visual outputs for classification evaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import Tensor

IMAGENET_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
IMAGENET_STD = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)


def plot_confusion_matrix(
    confusion_matrix: Tensor | np.ndarray,
    class_names: Sequence[str],
    output_path: str | Path = "outputs/confusion_matrix.png",
) -> Path:
    """Save an annotated confusion-matrix heatmap to ``output_path``."""
    matrix = torch.as_tensor(confusion_matrix).detach().cpu().numpy()
    if matrix.shape != (len(class_names), len(class_names)):
        raise ValueError("Confusion matrix dimensions must match class_names.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(8, 6))
    image = axis.imshow(matrix, interpolation="nearest", cmap="Blues")
    figure.colorbar(image, ax=axis)
    axis.set(
        xticks=np.arange(len(class_names)),
        yticks=np.arange(len(class_names)),
        xticklabels=class_names,
        yticklabels=class_names,
        xlabel="Predicted label",
        ylabel="Actual label",
        title="Confusion Matrix",
    )
    plt.setp(axis.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    threshold = matrix.max() / 2 if matrix.size else 0
    for row, column in np.ndindex(matrix.shape):
        axis.text(
            column,
            row,
            str(int(matrix[row, column])),
            ha="center",
            va="center",
            color="white" if matrix[row, column] > threshold else "black",
        )
    figure.tight_layout()
    figure.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return output


def display_sample_predictions(
    images: Tensor,
    targets: Tensor,
    predictions: Tensor,
    class_names: Sequence[str],
    max_samples: int = 12,
    show: bool = True,
) -> plt.Figure:
    """Display normalized image samples with actual and predicted class labels."""
    sample_count = min(max_samples, images.size(0))
    if sample_count <= 0:
        raise ValueError("At least one sample is required for visualization.")

    columns = min(4, sample_count)
    rows = int(np.ceil(sample_count / columns))
    figure, axes = plt.subplots(rows, columns, figsize=(4 * columns, 4 * rows))
    axes_array = np.atleast_1d(axes).ravel()
    display_images = images[:sample_count].detach().cpu()
    display_targets = targets[:sample_count].detach().cpu()
    display_predictions = predictions[:sample_count].detach().cpu()

    for index in range(sample_count):
        image = display_images[index] * IMAGENET_STD + IMAGENET_MEAN
        image = image.clamp(0, 1).permute(1, 2, 0).numpy()
        actual_index = int(display_targets[index].item())
        predicted_index = int(display_predictions[index].item())
        is_correct = actual_index == predicted_index

        axes_array[index].imshow(image)
        axes_array[index].set_title(
            f"Actual: {class_names[actual_index]}\n"
            f"Predicted: {class_names[predicted_index]}",
            color="green" if is_correct else "red",
        )
        axes_array[index].axis("off")

    for axis in axes_array[sample_count:]:
        axis.axis("off")
    figure.tight_layout()
    if show:
        plt.show()
    return figure
