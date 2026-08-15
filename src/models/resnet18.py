"""ResNet-18 transfer-learning model for eye disease classification."""

from __future__ import annotations

from collections.abc import Sequence

from torch import Tensor, nn
from torchvision.models import ResNet18_Weights, resnet18


class ResNet18Classifier(nn.Module):
    """ImageNet-initialised ResNet-18 with a configurable classification head."""

    _FINE_TUNABLE_LAYERS = frozenset(
        {"conv1", "bn1", "layer1", "layer2", "layer3", "layer4"}
    )

    def __init__(
        self,
        num_classes: int = 4,
        dropout: float = 0.3,
        freeze_backbone: bool = False,
        unfreeze_layers: Sequence[str] | None = None,
    ) -> None:
        """Initialise ImageNet-pretrained ResNet-18.

        Args:
            num_classes: Number of target classes.
            dropout: Dropout probability before the final linear layer.
            freeze_backbone: Freeze all feature-extractor parameters initially.
            unfreeze_layers: Named ResNet stages to train after freezing. Valid
                values are ``conv1``, ``bn1``, and ``layer1`` through ``layer4``.
        """
        super().__init__()
        if num_classes <= 0:
            raise ValueError("num_classes must be greater than zero.")
        if not 0.0 <= dropout < 1.0:
            raise ValueError("dropout must be in the range [0.0, 1.0).")

        self.backbone = resnet18(weights=ResNet18_Weights.DEFAULT)
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, num_classes),
        )

        if freeze_backbone:
            self.freeze_backbone()
        if unfreeze_layers:
            self.unfreeze_layers(unfreeze_layers)

    def freeze_backbone(self) -> None:
        """Freeze all pretrained feature-extractor parameters.

        The replacement classifier remains trainable.
        """
        for name, parameter in self.backbone.named_parameters():
            parameter.requires_grad = name.startswith("fc.")

    def unfreeze_layers(self, layer_names: Sequence[str]) -> None:
        """Enable gradients for selected ResNet feature-extractor stages.

        Args:
            layer_names: One or more supported ResNet stage names.

        Raises:
            ValueError: If a requested layer is not a supported stage.
        """
        unknown_layers = set(layer_names) - self._FINE_TUNABLE_LAYERS
        if unknown_layers:
            supported = ", ".join(sorted(self._FINE_TUNABLE_LAYERS))
            requested = ", ".join(sorted(unknown_layers))
            raise ValueError(
                f"Unsupported fine-tuning layers: {requested}. "
                f"Supported layers: {supported}."
            )

        for layer_name in layer_names:
            for parameter in getattr(self.backbone, layer_name).parameters():
                parameter.requires_grad = True

    def forward(self, inputs: Tensor) -> Tensor:
        """Return unnormalised class logits for a batch of images."""
        return self.backbone(inputs)
