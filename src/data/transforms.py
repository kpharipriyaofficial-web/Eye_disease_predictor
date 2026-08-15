"""Torchvision augmentation pipelines for eye disease classification."""

from __future__ import annotations

from torchvision import transforms

IMAGE_SIZE: tuple[int, int] = (224, 224)
IMAGENET_MEAN: tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: tuple[float, float, float] = (0.229, 0.224, 0.225)


def get_train_transform(
    image_size: tuple[int, int] = IMAGE_SIZE,
) -> transforms.Compose:
    """Return the augmentation pipeline used for training images."""
    return transforms.Compose(
        [
            transforms.Resize(image_size),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(degrees=10),
            transforms.ColorJitter(
                brightness=0.1,
                contrast=0.1,
                saturation=0.05,
                hue=0.0,
            ),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


def get_eval_transform(
    image_size: tuple[int, int] = IMAGE_SIZE,
) -> transforms.Compose:
    """Return the deterministic validation and test preprocessing pipeline."""
    return transforms.Compose(
        [
            transforms.Resize(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


def get_transforms(
    image_size: tuple[int, int] = IMAGE_SIZE,
) -> dict[str, transforms.Compose]:
    """Return transforms for all dataset splits."""
    evaluation_transform = get_eval_transform(image_size)
    return {
        "train": get_train_transform(image_size),
        "val": evaluation_transform,
        "test": evaluation_transform,
    }
