"""A compact convolutional baseline for eye disease classification."""

from __future__ import annotations

import torch
from torch import Tensor, nn


class BaselineCNN(nn.Module):
    """Lightweight CNN with adaptive pooling for image classification.

    The adaptive pooling layer allows the network to accept images larger or
    smaller than the project's standard 224 x 224 resolution.
    """

    def __init__(
        self,
        num_classes: int = 4,
        dropout: float = 0.3,
        input_channels: int = 3,
    ) -> None:
        """Initialise the model.

        Args:
            num_classes: Number of target classes.
            dropout: Dropout probability used by the classifier.
            input_channels: Number of image colour channels.
        """
        super().__init__()
        if num_classes <= 0:
            raise ValueError("num_classes must be greater than zero.")
        if input_channels <= 0:
            raise ValueError("input_channels must be greater than zero.")
        if not 0.0 <= dropout < 1.0:
            raise ValueError("dropout must be in the range [0.0, 1.0).")

        self.features = nn.Sequential(
            self._conv_block(input_channels, 32),
            self._conv_block(32, 64),
            self._conv_block(64, 128),
            self._conv_block(128, 256),
        )
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(128, num_classes),
        )

    @staticmethod
    def _conv_block(in_channels: int, out_channels: int) -> nn.Sequential:
        """Create a convolution, normalisation, activation, and pooling block."""
        return nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                stride=1,
                padding=1,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

    def forward(self, inputs: Tensor) -> Tensor:
        """Return unnormalised class logits for a batch of images."""
        features = self.features(inputs)
        return self.classifier(self.pool(features))
