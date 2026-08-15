"""Export trained eye disease classifiers to PyTorch, TorchScript, and ONNX."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from torch import Tensor, nn

from src.models.factory import _get_setting, _load_config, build_model


def _resolve_device(device: str | torch.device | None) -> torch.device:
    """Resolve a requested device, preferring CUDA when available."""
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    resolved = torch.device(device)
    if resolved.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available.")
    return resolved


def load_training_checkpoint(
    checkpoint_path: str | Path | None = None,
    *,
    device: str | torch.device | None = None,
) -> nn.Module:
    """Build the configured model and load a training or state-dict checkpoint."""
    config = _load_config()
    path = Path(
        checkpoint_path
        or _get_setting(
            config,
            ("BEST_MODEL_PATH", "CHECKPOINT_PATH", "MODEL_SAVE_PATH"),
            "saved_models/best_model.pt",
        )
    )
    if not path.is_file():
        raise FileNotFoundError(f"Model checkpoint does not exist: {path}")

    resolved_device = _resolve_device(device)
    try:
        checkpoint: Any = torch.load(
            path,
            map_location=resolved_device,
            weights_only=False,
        )
    except TypeError:
        checkpoint = torch.load(path, map_location=resolved_device)

    model = build_model().to(resolved_device)
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def export_pytorch(
    model: nn.Module,
    output_path: str | Path,
) -> Path:
    """Export a model's state dictionary as a PyTorch ``.pt`` file."""
    output = Path(output_path)
    if output.suffix != ".pt":
        raise ValueError("PyTorch export paths must end in .pt.")
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state_dict": model.state_dict()}, output)
    return output


def load_pytorch(
    model_path: str | Path,
    *,
    model: nn.Module | None = None,
    device: str | torch.device | None = None,
) -> nn.Module:
    """Load a PyTorch state-dictionary export into a configured or supplied model."""
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(f"PyTorch model does not exist: {path}")
    resolved_device = _resolve_device(device)
    try:
        payload: Any = torch.load(path, map_location=resolved_device, weights_only=False)
    except TypeError:
        payload = torch.load(path, map_location=resolved_device)
    loaded_model = model if model is not None else build_model()
    state_dict = payload.get("model_state_dict", payload)
    loaded_model.load_state_dict(state_dict)
    return loaded_model.to(resolved_device).eval()


def export_torchscript(
    model: nn.Module,
    output_path: str | Path,
    *,
    example_input: Tensor | None = None,
) -> Path:
    """Trace and save a self-contained TorchScript ``.pt`` deployment artifact."""
    output = Path(output_path)
    if output.suffix != ".pt":
        raise ValueError("TorchScript export paths must end in .pt.")
    output.parent.mkdir(parents=True, exist_ok=True)
    model.eval()
    model_device = next(model.parameters()).device
    input_tensor = (
        example_input
        if example_input is not None
        else torch.randn(1, 3, 224, 224, device=model_device)
    )
    traced_model = torch.jit.trace(model, input_tensor)
    traced_model.save(str(output))
    return output


def load_torchscript(
    model_path: str | Path,
    *,
    device: str | torch.device | None = None,
) -> torch.jit.ScriptModule:
    """Load a TorchScript artifact for inference on CPU or CUDA."""
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(f"TorchScript model does not exist: {path}")
    return torch.jit.load(str(path), map_location=_resolve_device(device)).eval()


def export_onnx(
    model: nn.Module,
    output_path: str | Path,
    *,
    example_input: Tensor | None = None,
    opset_version: int = 17,
) -> Path:
    """Export a model to ONNX with dynamic batch-size support."""
    output = Path(output_path)
    if output.suffix != ".onnx":
        raise ValueError("ONNX export paths must end in .onnx.")
    if opset_version < 11:
        raise ValueError("opset_version must be at least 11.")
    output.parent.mkdir(parents=True, exist_ok=True)
    model.eval()
    model_device = next(model.parameters()).device
    input_tensor = (
        example_input
        if example_input is not None
        else torch.randn(1, 3, 224, 224, device=model_device)
    )
    torch.onnx.export(
        model,
        input_tensor,
        str(output),
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=["images"],
        output_names=["logits"],
        dynamic_axes={"images": {0: "batch_size"}, "logits": {0: "batch_size"}},
    )
    return output


def load_onnx(
    model_path: str | Path,
    *,
    use_cuda: bool = False,
) -> Any:
    """Load an ONNX model as an ONNX Runtime inference session.

    Install ``onnxruntime`` (or ``onnxruntime-gpu`` for CUDA) to use this
    runtime-specific loader.
    """
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(f"ONNX model does not exist: {path}")
    try:
        import onnxruntime as ort
    except ImportError as error:
        raise ImportError(
            "load_onnx requires onnxruntime. Install onnxruntime or "
            "onnxruntime-gpu."
        ) from error

    providers = ["CPUExecutionProvider"]
    if use_cuda:
        if "CUDAExecutionProvider" not in ort.get_available_providers():
            raise RuntimeError("ONNX Runtime CUDAExecutionProvider is unavailable.")
        providers.insert(0, "CUDAExecutionProvider")
    return ort.InferenceSession(str(path), providers=providers)


def recommend_deployment_format() -> str:
    """Return the recommended format for this project's FastAPI deployment."""
    return (
        "TorchScript (.pt) is recommended for FastAPI because it keeps PyTorch "
        "preprocessing and inference in one dependency stack while avoiding the "
        "need to reconstruct the Python model class at deployment time."
    )
