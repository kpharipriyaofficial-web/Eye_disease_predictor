"""Model loading and test-set evaluation for eye disease classification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader

from src.data.dataloaders import get_test_loader
from src.models.factory import _get_setting, _load_config, build_model
from src.training.metrics import ClassificationMetrics

from .visualization import display_sample_predictions, plot_confusion_matrix


@dataclass(frozen=True)
class EvaluationResult:
    """Structured metrics and generated artifact location from an evaluation."""

    test_loss: float
    accuracy: float
    precision: float
    recall: float
    f1: float
    confusion_matrix: Tensor
    classification_report: dict[str, dict[str, float]]
    confusion_matrix_path: Path


def _set_default(config: ModuleType, name: str, value: object) -> None:
    """Set a configuration default only when the user has not set it."""
    if not hasattr(config, name):
        setattr(config, name, value)


def _configure_evaluation_defaults(config: ModuleType) -> None:
    """Provide project-layout defaults for standalone evaluation."""
    project_root = Path(__file__).resolve().parents[2]
    defaults: dict[str, object] = {
        "TEST_DATA_DIR": project_root / "datasets" / "test",
        "BATCH_SIZE": 32,
        "NUM_WORKERS": 0,
        "PIN_MEMORY": torch.cuda.is_available(),
        "MODEL_NAME": "baseline_cnn",
        "DROPOUT": 0.3,
        "BEST_MODEL_PATH": project_root / "saved_models" / "best_model.pt",
        "CONFUSION_MATRIX_PATH": project_root / "outputs" / "confusion_matrix.png",
        "SHOW_SAMPLE_PREDICTIONS": True,
        "NUM_SAMPLE_PREDICTIONS": 12,
    }
    for name, value in defaults.items():
        _set_default(config, name, value)


def build_classification_report(
    confusion_matrix: Tensor,
    class_names: list[str],
) -> dict[str, dict[str, float]]:
    """Build a per-class, macro, and weighted classification report."""
    matrix = confusion_matrix.to(dtype=torch.float32)
    true_positives = matrix.diag()
    support = matrix.sum(dim=1)
    predicted_count = matrix.sum(dim=0)
    precision = torch.nan_to_num(true_positives / predicted_count, nan=0.0)
    recall = torch.nan_to_num(true_positives / support, nan=0.0)
    f1 = torch.nan_to_num(
        2 * precision * recall / (precision + recall),
        nan=0.0,
    )
    total = support.sum()
    accuracy = float(true_positives.sum().item() / total.item()) if total else 0.0

    report: dict[str, dict[str, float]] = {}
    for index, class_name in enumerate(class_names):
        report[class_name] = {
            "precision": float(precision[index].item()),
            "recall": float(recall[index].item()),
            "f1-score": float(f1[index].item()),
            "support": float(support[index].item()),
        }
    report["accuracy"] = {"accuracy": accuracy, "support": float(total.item())}
    report["macro avg"] = {
        "precision": float(precision.mean().item()),
        "recall": float(recall.mean().item()),
        "f1-score": float(f1.mean().item()),
        "support": float(total.item()),
    }
    weights = support / total if total else torch.zeros_like(support)
    report["weighted avg"] = {
        "precision": float((precision * weights).sum().item()),
        "recall": float((recall * weights).sum().item()),
        "f1-score": float((f1 * weights).sum().item()),
        "support": float(total.item()),
    }
    return report


class Evaluator:
    """Load the best checkpoint and evaluate it on the configured test split."""

    def __init__(self, test_loader: DataLoader | None = None) -> None:
        self.config = _load_config()
        _configure_evaluation_defaults(self.config)
        self.device = torch.device(
            _get_setting(
                self.config,
                ("DEVICE",),
                "cuda" if torch.cuda.is_available() else "cpu",
            )
        )
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("DEVICE is CUDA, but CUDA is not available.")
        self.test_loader = test_loader if test_loader is not None else get_test_loader()
        self.class_names = list(self.test_loader.dataset.classes)
        self.num_classes = len(self.class_names)
        _set_default(self.config, "NUM_CLASSES", self.num_classes)
        if int(self.config.NUM_CLASSES) != self.num_classes:
            raise ValueError("NUM_CLASSES does not match the configured test dataset.")

        self.model = build_model().to(self.device)
        self.checkpoint_path = Path(
            _get_setting(
                self.config,
                ("BEST_MODEL_PATH", "CHECKPOINT_PATH", "MODEL_SAVE_PATH"),
                "saved_models/best_model.pt",
            )
        )

    def load_best_model(self) -> None:
        """Load ``saved_models/best_model.pt`` into the configured model."""
        if not self.checkpoint_path.is_file():
            raise FileNotFoundError(
                f"Best-model checkpoint does not exist: {self.checkpoint_path}"
            )
        try:
            checkpoint = torch.load(
                self.checkpoint_path,
                map_location=self.device,
                weights_only=False,
            )
        except TypeError:
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        state_dict = checkpoint.get("model_state_dict", checkpoint)
        self.model.load_state_dict(state_dict)
        self.model.eval()

    @torch.inference_mode()
    def evaluate(self) -> EvaluationResult:
        """Evaluate the best model, save its matrix, and display predictions."""
        self.load_best_model()
        metrics = ClassificationMetrics(self.num_classes)
        criterion = nn.CrossEntropyLoss()
        total_loss = 0.0
        total_examples = 0
        sample_images: list[Tensor] = []
        sample_targets: list[Tensor] = []
        sample_predictions: list[Tensor] = []
        maximum_samples = int(
            _get_setting(self.config, ("NUM_SAMPLE_PREDICTIONS",), 12)
        )

        for images, targets in self.test_loader:
            images = images.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)
            logits = self.model(images)
            total_loss += float(criterion(logits, targets).item()) * targets.size(0)
            total_examples += targets.size(0)
            predictions = logits.argmax(dim=1)
            metrics.update(logits, targets)

            remaining = maximum_samples - sum(batch.size(0) for batch in sample_images)
            if remaining > 0:
                sample_images.append(images[:remaining].cpu())
                sample_targets.append(targets[:remaining].cpu())
                sample_predictions.append(predictions[:remaining].cpu())

        computed = metrics.compute()
        if total_examples == 0:
            raise ValueError("Test DataLoader produced no examples.")
        matrix = computed["confusion_matrix"]
        assert isinstance(matrix, Tensor)
        output_path = Path(
            _get_setting(
                self.config,
                ("CONFUSION_MATRIX_PATH",),
                "outputs/confusion_matrix.png",
            )
        )
        saved_matrix = plot_confusion_matrix(matrix, self.class_names, output_path)

        if sample_images and bool(
            _get_setting(self.config, ("SHOW_SAMPLE_PREDICTIONS",), True)
        ):
            display_sample_predictions(
                torch.cat(sample_images),
                torch.cat(sample_targets),
                torch.cat(sample_predictions),
                self.class_names,
                max_samples=maximum_samples,
            )

        return EvaluationResult(
            test_loss=total_loss / total_examples,
            accuracy=float(computed["accuracy"]),
            precision=float(computed["precision"]),
            recall=float(computed["recall"]),
            f1=float(computed["f1"]),
            confusion_matrix=matrix,
            classification_report=build_classification_report(
                matrix,
                self.class_names,
            ),
            confusion_matrix_path=saved_matrix,
        )


def evaluate_best_model() -> EvaluationResult:
    """Convenience entry point for complete test-set evaluation."""
    return Evaluator().evaluate()


def main() -> None:
    """Run configured test-set evaluation from the command line."""
    _load_config()
    result = evaluate_best_model()
    print(f"Test Loss: {result.test_loss:.4f}")
    print(f"Accuracy: {result.accuracy:.4f}")
    print(f"Precision: {result.precision:.4f}")
    print(f"Recall: {result.recall:.4f}")
    print(f"F1 Score: {result.f1:.4f}")
    print("Classification Report:")
    print(json.dumps(result.classification_report, indent=2))
    print(f"Confusion matrix saved to: {result.confusion_matrix_path}")


if __name__ == "__main__":
    main()
