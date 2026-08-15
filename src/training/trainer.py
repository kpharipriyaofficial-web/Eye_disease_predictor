"""Mixed-precision, resumable training loop for image classification."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import torch
from torch import Tensor, nn
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler
from tqdm.auto import tqdm

from src.models.factory import _get_setting, _load_config

from .callbacks import EarlyStopping, ModelCheckpoint
from .metrics import ClassificationMetrics
from .optimizer import create_optimizer, create_scheduler


class Trainer:
    """Train a classification model with validation-driven checkpointing."""

    def __init__(
        self,
        model: nn.Module,
        train_loader: Iterable[tuple[Tensor, Tensor]],
        validation_loader: Iterable[tuple[Tensor, Tensor]],
    ) -> None:
        """Initialise training state using hyperparameters from ``config.py``."""
        self.config = _load_config()
        self.model = model
        self.train_loader = train_loader
        self.validation_loader = validation_loader
        self.num_classes = int(
            _get_setting(self.config, ("NUM_CLASSES", "N_CLASSES"), 4)
        )
        self.num_epochs = int(
            _get_setting(self.config, ("EPOCHS", "NUM_EPOCHS"), 10)
        )
        if self.num_epochs <= 0:
            raise ValueError("EPOCHS must be greater than zero.")

        configured_device = _get_setting(self.config, ("DEVICE",), None)
        default_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(configured_device or default_device)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("DEVICE is CUDA, but CUDA is not available.")
        self.model.to(self.device)

        label_smoothing = float(
            _get_setting(self.config, ("LABEL_SMOOTHING",), 0.0)
        )
        if not 0.0 <= label_smoothing < 1.0:
            raise ValueError("LABEL_SMOOTHING must be in the range [0.0, 1.0).")
        class_weights = self._get_class_weights()
        self.criterion = nn.CrossEntropyLoss(
            weight=class_weights,
            label_smoothing=label_smoothing,
        )
        self.optimizer: Optimizer = create_optimizer(self.model)
        self.scheduler: LRScheduler = create_scheduler(self.optimizer)

        self.amp_enabled = bool(_get_setting(self.config, ("AMP", "USE_AMP"), True))
        self.amp_enabled = self.amp_enabled and self.device.type == "cuda"
        self.scaler = torch.cuda.amp.GradScaler(enabled=self.amp_enabled)
        self.gradient_clip_norm = float(
            _get_setting(self.config, ("GRADIENT_CLIP_NORM", "MAX_GRAD_NORM"), 1.0)
        )
        if self.gradient_clip_norm < 0:
            raise ValueError("GRADIENT_CLIP_NORM cannot be negative.")

        patience = int(
            _get_setting(self.config, ("EARLY_STOPPING_PATIENCE", "PATIENCE"), 5)
        )
        min_delta = float(
            _get_setting(self.config, ("EARLY_STOPPING_MIN_DELTA",), 0.0)
        )
        checkpoint_path = Path(
            _get_setting(
                self.config,
                ("BEST_MODEL_PATH", "CHECKPOINT_PATH", "MODEL_SAVE_PATH"),
                "saved_models/best_model.pt",
            )
        )
        self.early_stopping = EarlyStopping(patience=patience, min_delta=min_delta)
        self.checkpoint = ModelCheckpoint(checkpoint_path, min_delta=min_delta)
        self.start_epoch = 0
        self.history: dict[str, list[float]] = {
            "train_loss": [],
            "validation_loss": [],
            "train_accuracy": [],
            "validation_accuracy": [],
        }

        resume_path = _get_setting(
            self.config,
            ("RESUME_FROM", "RESUME_CHECKPOINT"),
            None,
        )
        should_resume = bool(_get_setting(self.config, ("RESUME_TRAINING",), False))
        if resume_path or should_resume:
            self.resume_from_checkpoint(resume_path or checkpoint_path)

    def _get_class_weights(self) -> Tensor | None:
        """Compute inverse-frequency training weights when configured to do so."""
        use_class_weights = bool(
            _get_setting(self.config, ("USE_CLASS_WEIGHTS",), True)
        )
        if not use_class_weights:
            return None

        dataset = getattr(self.train_loader, "dataset", None)
        targets = getattr(dataset, "targets", None)
        if targets is None:
            raise TypeError(
                "USE_CLASS_WEIGHTS requires a training dataset with a targets "
                "attribute, such as torchvision.datasets.ImageFolder."
            )
        target_tensor = torch.as_tensor(targets, dtype=torch.long)
        class_counts = torch.bincount(target_tensor, minlength=self.num_classes)
        if class_counts.numel() != self.num_classes or torch.any(class_counts == 0):
            raise ValueError(
                "Every configured class must have at least one training image."
            )
        weights = target_tensor.numel() / (self.num_classes * class_counts.float())
        return weights.to(self.device)

    def _checkpoint_state(self, epoch: int) -> dict[str, Any]:
        """Build the complete state required to resume training."""
        return {
            "epoch": epoch,
            "model_name": _get_setting(
                self.config,
                ("MODEL_NAME", "MODEL", "MODEL_TYPE"),
                "baseline_cnn",
            ),
            "num_classes": self.num_classes,
            "class_names": list(
                getattr(getattr(self.train_loader, "dataset", None), "classes", ())
            ),
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "scaler_state_dict": self.scaler.state_dict(),
            "history": self.history,
            "early_stopping": self.early_stopping.state_dict(),
            "checkpoint": self.checkpoint.state_dict(),
        }

    def resume_from_checkpoint(self, checkpoint_path: str | Path) -> None:
        """Restore model, optimiser, scheduler, AMP, and callback state."""
        path = Path(checkpoint_path)
        if not path.is_file():
            raise FileNotFoundError(f"Resume checkpoint does not exist: {path}")
        try:
            state = torch.load(path, map_location=self.device, weights_only=False)
        except TypeError:
            state = torch.load(path, map_location=self.device)
        self.model.load_state_dict(state["model_state_dict"])
        self.optimizer.load_state_dict(state["optimizer_state_dict"])
        self.scheduler.load_state_dict(state["scheduler_state_dict"])
        self.scaler.load_state_dict(state["scaler_state_dict"])
        self.history = state.get("history", self.history)
        if "early_stopping" in state:
            self.early_stopping.load_state_dict(state["early_stopping"])
        if "checkpoint" in state:
            self.checkpoint.load_state_dict(state["checkpoint"])
        self.start_epoch = int(state["epoch"]) + 1

    def _run_epoch(
        self,
        loader: Iterable[tuple[Tensor, Tensor]],
        *,
        training: bool,
        epoch: int,
    ) -> tuple[float, dict[str, float | Tensor]]:
        """Run one train or validation epoch and return aggregate metrics."""
        self.model.train(mode=training)
        metrics = ClassificationMetrics(self.num_classes)
        total_loss = 0.0
        total_examples = 0
        description = "Train" if training else "Validation"
        progress = tqdm(loader, desc=f"{description} {epoch + 1}/{self.num_epochs}")

        context = torch.enable_grad() if training else torch.no_grad()
        with context:
            for inputs, targets in progress:
                inputs = inputs.to(self.device, non_blocking=True)
                targets = targets.to(self.device, non_blocking=True)
                batch_size = targets.size(0)

                if training:
                    self.optimizer.zero_grad(set_to_none=True)

                with torch.autocast(device_type=self.device.type, enabled=self.amp_enabled):
                    logits = self.model(inputs)
                    loss = self.criterion(logits, targets)

                if training:
                    self.scaler.scale(loss).backward()
                    if self.gradient_clip_norm > 0:
                        self.scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(),
                            max_norm=self.gradient_clip_norm,
                        )
                    self.scaler.step(self.optimizer)
                    self.scaler.update()

                total_loss += float(loss.detach().item()) * batch_size
                total_examples += batch_size
                metrics.update(logits, targets)
                progress.set_postfix(loss=f"{loss.detach().item():.4f}")

        if total_examples == 0:
            raise ValueError("DataLoader produced no batches.")
        return total_loss / total_examples, metrics.compute()

    def train(self) -> dict[str, list[float]]:
        """Run training and return per-epoch loss and accuracy history."""
        for epoch in range(self.start_epoch, self.num_epochs):
            train_loss, train_metrics = self._run_epoch(
                self.train_loader,
                training=True,
                epoch=epoch,
            )
            validation_loss, validation_metrics = self._run_epoch(
                self.validation_loader,
                training=False,
                epoch=epoch,
            )
            self.scheduler.step()

            self.history["train_loss"].append(train_loss)
            self.history["validation_loss"].append(validation_loss)
            self.history["train_accuracy"].append(float(train_metrics["accuracy"]))
            self.history["validation_accuracy"].append(
                float(validation_metrics["accuracy"])
            )
            print(
                f"Epoch {epoch + 1}/{self.num_epochs} | "
                f"train_loss={train_loss:.4f} | "
                f"val_loss={validation_loss:.4f} | "
                f"train_accuracy={train_metrics['accuracy']:.4f} | "
                f"val_accuracy={validation_metrics['accuracy']:.4f}"
            )

            should_stop = self.early_stopping.step(validation_loss)
            self.checkpoint.step(validation_loss, self._checkpoint_state(epoch))
            if should_stop:
                print("Early stopping triggered.")
                break

        return self.history

    @torch.no_grad()
    def evaluate(
        self,
        loader: Iterable[tuple[Tensor, Tensor]],
    ) -> dict[str, float | Tensor]:
        """Evaluate a loader and return loss, classification metrics, and matrix."""
        loss, metrics = self._run_epoch(loader, training=False, epoch=self.num_epochs)
        return {"loss": loss, **metrics}
