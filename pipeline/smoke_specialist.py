"""Measure one real CPU specialist on answer-free preparation pixels, never test data.

Run separately per model to measure independent process peak memory. The checkpoint
is a required local, hash-pinned input; this runner never downloads weights.
"""

from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import importlib.metadata
import json
from pathlib import Path
import platform
import random
import sys
from time import perf_counter

from PIL import Image

from pipeline.model_inputs import read_inputs


def pretrained_feature_state(expected_keys: set[str], weights: dict) -> tuple[dict, list[str]]:
    """Keep all feature tensors; permit only PyTorch's legacy BN counter migration.

    Old official checkpoints omit num_batches_tracked. PyTorch's strict loader
    initializes these bookkeeping counters to zero; they are not learned weights.
    """
    missing = expected_keys - set(weights)
    if not expected_keys or any(not key.endswith(".num_batches_tracked") for key in missing):
        raise ValueError("Pretrained backbone feature weights are missing")
    return {key: weights[key] for key in expected_keys if key in weights}, sorted(missing)


def peak_memory_bytes() -> int:
    """Windows process peak working set, not Python-only allocation estimates."""
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize",
                "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise OSError("Cannot measure peak process working set")
    return counters.PeakWorkingSetSize


def run(model_name: str, inputs: Path, checkpoint: Path, config: dict, out: Path) -> dict:
    if sys.platform != "win32":
        raise ValueError("This measured feasibility runner targets Windows")
    if out.exists() or out.resolve().is_relative_to(inputs.resolve()):
        raise ValueError("Choose a new output outside the model input directory")
    input_hashes = {s: sha256((inputs/f"{s}.json").read_bytes()).hexdigest() for s in ("fitting","calibration")}
    if input_hashes != config["input_index_sha256"]:
        raise ValueError("Input indexes do not match approved preparation fingerprints")
    # Fixed filenames and membership checks; no evaluator metadata/test index is read.
    fitting = read_inputs(inputs / "fitting.json")
    calibration = read_inputs(inputs / "calibration.json")
    fit_ids = {i["image_id"] for i in fitting["images"]}
    cal_ids = {i["image_id"] for i in calibration["images"]}
    fit_hashes = {i["sha256"] for i in fitting["images"]}
    if fit_ids & cal_ids or fit_hashes & {i["sha256"] for i in calibration["images"]}:
        raise ValueError("Fitting/calibration inputs overlap")
    if len(fitting["images"]) < config["fitting_sample_count"]:
        raise ValueError("Insufficient normal fitting images for smoke configuration")
    checkpoint_hash = sha256(checkpoint.read_bytes()).hexdigest()
    if checkpoint_hash != config["checkpoint_sha256"]:
        raise ValueError("Checkpoint does not match pinned official candidate bytes")
    out.mkdir(parents=True, exist_ok=False)
    report = {"schema_version": 1, "evidence_status": "authentic_development_sample",
        "status": "started", "stage": "imports", "model": model_name, "config": config, "checkpoint_sha256": checkpoint_hash,
        "started_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "platform": platform.platform(), "python": platform.python_version(),
        "input_index_sha256": input_hashes,
        "limitations": ["Only a small normal-preparation sample; not a benchmark, calibrated policy or model-quality result.",
            "Provisional preparation membership and object/session identity remain unresolved.",
            "256px defect visibility, full-fitting memory/runtime and final evaluation remain unverified.",
            "Maps are raw model outputs at resized input coordinates, not reference masks or probabilities."]}
    def save():
        (out/"result.json").write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    save()
    start = perf_counter()
    try:
        import numpy as np
        import torch
        from anomalib.models.image.padim.torch_model import PadimModel
        from anomalib.models.image.patchcore.torch_model import PatchcoreModel

        report["packages"] = {p: importlib.metadata.version(p) for p in ("anomalib","torch","torchvision","timm","numpy","pillow")}
        torch.set_num_threads(config["threads"])
        torch.manual_seed(config["seed"])
        np.random.seed(config["seed"])
        random.seed(config["seed"])
        torch.use_deterministic_algorithms(True)
        report["stage"] = "backbone"
        parameters = config[model_name]
        if model_name == "padim":
            model = PadimModel(backbone=config["backbone"], layers=parameters["layers"],
                               pre_trained=False, n_features=parameters["n_features"])
        else:
            model = PatchcoreModel(backbone=config["backbone"], layers=parameters["layers"],
                                   pre_trained=False, num_neighbors=parameters["num_neighbors"])
        # Load official ResNet-18 features locally. No timm/Hugging Face auto-download,
        # credential discovery or random-weight substitution is permitted.
        weights = torch.load(checkpoint, map_location="cpu", weights_only=True)
        extractor = model.feature_extractor.feature_extractor
        expected_keys = set(extractor.state_dict())
        state, counters = pretrained_feature_state(expected_keys, weights)
        # Feature-only timm models omit the classifier and unused deeper layers.
        # Every remaining tensor must come from the pinned pretrained checkpoint.
        extractor.load_state_dict(state, strict=True)
        report["pretrained_features_loaded"] = True
        report["pretrained_feature_tensor_count"] = len(state)
        report["legacy_batch_counter_count"] = len(counters)
        report["device"] = "cpu"
        report["setup_seconds"] = perf_counter()-start

        def tensor(item):
            content = (inputs/item["path"]).read_bytes()
            if sha256(content).hexdigest() != item["sha256"]:
                raise ValueError("Model input changed after validation")
            with Image.open(BytesIO(content), formats=["PNG"]) as image:
                image.load()
                resized = image.resize((config["input_size_px"],)*2, Image.Resampling.BILINEAR)
                arr = np.asarray(resized, dtype=np.float32).copy()/255
            batch = torch.from_numpy(arr).permute(2,0,1).unsqueeze(0)
            mean = torch.tensor(config["normalization_mean"]).reshape(1,3,1,1)
            std = torch.tensor(config["normalization_std"]).reshape(1,3,1,1)
            return (batch-mean)/std

        fit = sorted(fitting["images"], key=lambda i:i["image_id"])[:config["fitting_sample_count"]]
        sample = sorted(calibration["images"], key=lambda i:i["image_id"])[:config["calibration_sample_count"]]
        report["fitting_ids"] = [i["image_id"] for i in fit]
        report["stage"] = "fitting"
        fit_start = perf_counter()
        model.train()
        with torch.no_grad():
            for item in fit:
                model(tensor(item))
            if model_name == "padim":
                model.fit()
            else:
                model.subsample_embedding(parameters["coreset_sampling_ratio"])
        report["fit_seconds"] = perf_counter()-fit_start
        if model_name == "patchcore":
            report["memory_bank_shape"] = list(model.memory_bank.shape)
        model.eval()
        report["stage"] = "inference"
        outputs = []
        with torch.no_grad():
            for item in sample:
                infer_start = perf_counter()
                prediction = model(tensor(item))
                seconds = perf_counter()-infer_start
                score = float(prediction.pred_score.reshape(-1)[0])
                anomaly_map = prediction.anomaly_map.detach().cpu().numpy()
                if not np.isfinite(score) or not np.isfinite(anomaly_map).all():
                    raise ValueError("Model produced nonfinite output")
                if anomaly_map.shape[-2:] != (config["input_size_px"],)*2:
                    raise ValueError("Unexpected model map dimensions")
                name = f"{item['image_id']}.map.npy"
                np.save(out/name, anomaly_map, allow_pickle=False)
                outputs.append({"image_id": item["image_id"], "score": score,
                    "score_meaning": "anomalib raw image anomaly score; no threshold or probability calibration",
                    "map": name, "map_sha256": sha256((out/name).read_bytes()).hexdigest(),
                    "map_shape": list(anomaly_map.shape), "input_dimensions": item["dimensions"],
                    "map_to_input": {"x_scale": item["dimensions"]["width_px"]/config["input_size_px"],
                        "y_scale": item["dimensions"]["height_px"]/config["input_size_px"], "offset_px": [0,0]},
                    "inference_seconds_including_preprocessing": seconds})
        report.update(status="success", stage="complete", outputs=outputs)
    except Exception as error:
        # Persist bounded failure type, never an exception containing local paths/inputs.
        report.update(status="failed", error_type=type(error).__name__)
    report["elapsed_seconds"] = perf_counter()-start
    report["peak_process_working_set_bytes"] = peak_memory_bytes()
    report["completed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    save()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("padim", "patchcore"), required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/specialist-smoke.v1.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = run(args.model, args.inputs, args.checkpoint,
                     json.loads(args.config.read_text(encoding="utf-8")), args.output_dir)
    except (OSError, ValueError, KeyError):
        print("FAIL specialist smoke: check preparation inputs, checkpoint, configuration and new output location")
        return 1
    print(f"{report['status'].upper()} {args.model}: CPU development sample; not final evaluation")
    return 0 if report["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
