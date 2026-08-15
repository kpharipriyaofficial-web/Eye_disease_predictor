"""Central configuration for the machine-learning pipeline."""

from __future__ import annotations

from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "datasets"
TRAIN_DATA_DIR = DATASET_DIR / "train"
VAL_DATA_DIR = DATASET_DIR / "val"
TEST_DATA_DIR = DATASET_DIR / "test"

# Dataset and model
CLASS_NAMES = ("Cataracts", "Glaucoma", "Normal", "Uveitis")
NUM_CLASSES = len(CLASS_NAMES)
MODEL_NAME = "baseline_cnn"
DROPOUT = 0.3

# Data loading
BATCH_SIZE = 32
NUM_WORKERS = 0
PIN_MEMORY = torch.cuda.is_available()

# Optimisation
EPOCHS = 10
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
COSINE_T_MAX = EPOCHS
MIN_LEARNING_RATE = 0.0
LABEL_SMOOTHING = 0.0
USE_CLASS_WEIGHTS = True
GRADIENT_CLIP_NORM = 1.0
AMP = torch.cuda.is_available()

# Checkpointing and early stopping
EARLY_STOPPING_PATIENCE = 5
EARLY_STOPPING_MIN_DELTA = 0.0
BEST_MODEL_PATH = PROJECT_ROOT / "saved_models" / "best_model.pt"
RESUME_TRAINING = False
RESUME_FROM: Path | None = None

# Evaluation and inference
CONFUSION_MATRIX_PATH = PROJECT_ROOT / "outputs" / "confusion_matrix.png"
SHOW_SAMPLE_PREDICTIONS = True
NUM_SAMPLE_PREDICTIONS = 12
