import os
import shutil
import random
from pathlib import Path

# Reproducibility
random.seed(42)

# Paths
ROOT_DIR = Path(__file__).resolve().parent
SOURCE_DIR = ROOT_DIR / "Dataset_ML"
OUTPUT_DIR = ROOT_DIR / "datasets"

# Split ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}


def get_class_folders(source_dir):
    """Return a sorted list of class folder paths inside the source directory."""
    return sorted([p for p in source_dir.iterdir() if p.is_dir()])


def get_images(class_dir):
    """Return a sorted list of image files inside a class directory."""
    return sorted(
        [p for p in class_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    )


def split_indices(total, train_ratio, val_ratio):
    """Compute split sizes for train/val/test given a total count."""
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)
    test_count = total - train_count - val_count
    return train_count, val_count, test_count


def create_output_dirs(output_dir, class_names):
    """Create datasets/train, datasets/val, datasets/test with class subfolders."""
    for split in ("train", "val", "test"):
        for class_name in class_names:
            (output_dir / split / class_name).mkdir(parents=True, exist_ok=True)


def copy_images(images, destination_dir):
    """Copy a list of image files into the destination directory."""
    for image_path in images:
        shutil.copy2(image_path, destination_dir / image_path.name)


def main():
    if not SOURCE_DIR.exists():
        print(f"Source dataset folder not found: {SOURCE_DIR}")
        return

    class_folders = get_class_folders(SOURCE_DIR)
    if not class_folders:
        print(f"No class folders found inside: {SOURCE_DIR}")
        return

    class_names = [folder.name for folder in class_folders]
    create_output_dirs(OUTPUT_DIR, class_names)

    total_images_all_classes = 0

    for class_dir in class_folders:
        class_name = class_dir.name
        images = get_images(class_dir)
        random.shuffle(images)

        total_images = len(images)
        train_count, val_count, test_count = split_indices(
            total_images, TRAIN_RATIO, VAL_RATIO
        )

        train_images = images[:train_count]
        val_images = images[train_count:train_count + val_count]
        test_images = images[train_count + val_count:]

        copy_images(train_images, OUTPUT_DIR / "train" / class_name)
        copy_images(val_images, OUTPUT_DIR / "val" / class_name)
        copy_images(test_images, OUTPUT_DIR / "test" / class_name)

        total_images_all_classes += total_images

        print(class_name)
        print(f"Train: {len(train_images)}")
        print(f"Validation: {len(val_images)}")
        print(f"Test: {len(test_images)}")
        print()

    print(f"Total images processed: {total_images_all_classes}")


if __name__ == "__main__":
    main()
