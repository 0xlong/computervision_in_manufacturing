"""Bound a full-normal-fitting CPU probe; never score final-test images.

Windows Job Objects cap committed process memory (not working-set RAM). The
worker waits for a start signal until the OS limits have been installed.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from uuid import uuid4

from pipeline.model_inputs import read_inputs

GIB = 1024**3
ROOT = Path(__file__).resolve().parents[1]
# No ML import, input access or model execution before the parent sends RUN.
GATED_WORKER = (
    "import runpy,sys; "
    "gate=sys.stdin.readline(); "
    "assert gate == 'RUN\\n', 'Supervisor did not authorize execution'; "
    "from pipeline.profile_specialist import attach_current_job; "
    "attach_current_job(sys.argv.pop(1)); "
    "sys.argv=['pipeline.smoke_specialist',*sys.argv[1:]]; "
    "runpy.run_module('pipeline.smoke_specialist',run_name='__main__')"
)


class BasicLimits(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong),
               ("PerJobUserTimeLimit", ctypes.c_longlong),
               ("LimitFlags", wintypes.DWORD),
               ("MinimumWorkingSetSize", ctypes.c_size_t),
               ("MaximumWorkingSetSize", ctypes.c_size_t),
               ("ActiveProcessLimit", wintypes.DWORD),
               ("Affinity", ctypes.c_size_t),
               ("PriorityClass", wintypes.DWORD),
               ("SchedulingClass", wintypes.DWORD)]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", BasicLimits),
               ("IoInfo", ctypes.c_ulonglong * 6),
               ("ProcessMemoryLimit", ctypes.c_size_t),
               ("JobMemoryLimit", ctypes.c_size_t),
               ("PeakProcessMemoryUsed", ctypes.c_size_t),
               ("PeakJobMemoryUsed", ctypes.c_size_t)]


class MemoryStatus(ctypes.Structure):
    _fields_ = [("dwLength", wintypes.DWORD), ("dwMemoryLoad", wintypes.DWORD)] + [
        (name, ctypes.c_ulonglong) for name in (
            "ullTotalPhys", "ullAvailPhys", "ullTotalPageFile", "ullAvailPageFile",
            "ullTotalVirtual", "ullAvailVirtual", "ullAvailExtendedVirtual")]


class WindowsJob:
    """One child process, committed-memory cap, terminate on supervisor exit."""

    def __init__(self, memory_bytes: int):
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.api.CreateJobObjectW.restype = wintypes.HANDLE
        for name in ("SetInformationJobObject", "QueryInformationJobObject"):
            getattr(self.api, name).restype = wintypes.BOOL
        self.api.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.api.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]
        self.api.CloseHandle.restype = wintypes.BOOL
        self.name = "Local\\inspection-resource-" + uuid4().hex
        self.handle = self.api.CreateJobObjectW(None, self.name)
        if not self.handle:
            raise OSError("Cannot create resource-limited job")
        limits = ExtendedLimits()
        # PROCESS_MEMORY | ACTIVE_PROCESS | KILL_ON_JOB_CLOSE
        limits.BasicLimitInformation.LimitFlags = 0x100 | 0x8 | 0x2000
        limits.BasicLimitInformation.ActiveProcessLimit = 1
        limits.ProcessMemoryLimit = memory_bytes
        if not self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            self.close()
            raise OSError("Cannot install resource limits")

    def peak_committed_bytes(self) -> int:
        limits = ExtendedLimits()
        if not self.api.QueryInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits), None):
            raise OSError("Cannot measure job peak committed memory")
        return limits.PeakProcessMemoryUsed

    def close(self) -> None:
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def attach_current_job(name: str) -> None:
    """Attach the actual interpreter, including behind Windows venv launchers.

    The parent owns the only enduring job handle. If it dies before attachment,
    opening fails; if it dies after attachment, closing this handle kills us.
    No model import or input access takes place before successful attachment.
    """
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenJobObjectW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    api.OpenJobObjectW.restype = wintypes.HANDLE
    api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    api.AssignProcessToJobObject.restype = wintypes.BOOL
    api.GetCurrentProcess.restype = wintypes.HANDLE
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    # JOB_OBJECT_ASSIGN_PROCESS access only; no child-owned configuration rights.
    handle = api.OpenJobObjectW(0x1, False, name)
    if not handle:
        raise OSError("Supervisor resource job is unavailable")
    try:
        if not api.AssignProcessToJobObject(handle, api.GetCurrentProcess()):
            raise OSError("Cannot attach actual interpreter to resource job")
    finally:
        api.CloseHandle(handle)


def available_physical_bytes() -> int:
    memory = MemoryStatus()
    memory.dwLength = ctypes.sizeof(memory)
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MemoryStatus)]
    api.GlobalMemoryStatusEx.restype = wintypes.BOOL
    if not api.GlobalMemoryStatusEx(ctypes.byref(memory)):
        raise OSError("Cannot measure available physical memory")
    return memory.ullAvailPhys


def bounded_process(command: list[str], memory_bytes: int, timeout_seconds: int) -> dict:
    """Discard worker logs, which may contain private paths; persist safe status."""
    job = WindowsJob(memory_bytes)
    process = None
    started = perf_counter()
    try:
        # The bootstrap attaches the actual Python interpreter rather than a
        # possible Windows venv launcher before importing any ML package.
        process = subprocess.Popen([*command[:3], job.name, *command[3:]], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, cwd=ROOT, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            process.communicate(input=b"RUN\n", timeout=timeout_seconds)
            status = "exited"
        except subprocess.TimeoutExpired:
            # Closing the job also kills an interpreter behind a venv launcher.
            peak = job.peak_committed_bytes()
            job.close()
            process.kill()
            process.communicate()
            status = "timed_out"
        return {"worker_status": status, "worker_exit_code": process.returncode,
                "wall_seconds_including_validation": perf_counter() - started,
                "peak_process_committed_bytes": peak if status == "timed_out" else job.peak_committed_bytes()}
    finally:
        # Failure to install limits must never release the worker start gate.
        if process is not None:
            job.close()
            if process.poll() is None:
                process.kill()
            process.communicate()
        job.close()


def full_fitting_config(base: dict, inputs: Path) -> tuple[dict, list[str]]:
    fingerprints = {split: sha256((inputs / f"{split}.json").read_bytes()).hexdigest()
                    for split in ("fitting", "calibration")}
    if fingerprints != base["input_index_sha256"]:
        raise ValueError("Input indexes do not match approved preparation fingerprints")
    fitting = read_inputs(inputs / "fitting.json")
    ids = sorted(item["image_id"] for item in fitting["images"])
    config = {**base, "fitting_sample_count": len(ids), "calibration_sample_count": 1,
              "purpose": "development_only_full_normal_fitting_resource_probe"}
    return config, ids


def profile(model: str, inputs: Path, checkpoint: Path, config_path: Path, out: Path,
            memory_bytes: int = 3 * GIB, timeout_seconds: int = 600) -> dict:
    if sys.platform != "win32":
        raise ValueError("Resource profiling requires Windows Job Objects")
    if model not in ("padim", "patchcore") or not GIB <= memory_bytes <= 3 * GIB or not 1 <= timeout_seconds <= 600:
        raise ValueError("Use a supported model, 1–3 GiB memory and 1–600 seconds")
    # Confine generated evidence to the project's ignored artifacts directory.
    target = out.resolve()
    artifact_root = (ROOT / "artifacts").resolve()
    if (out.exists() or not artifact_root.is_relative_to(ROOT.resolve())
            or not target.is_relative_to(artifact_root) or target == artifact_root):
        raise ValueError("Choose a new directory below project artifacts")
    if target.is_relative_to(inputs.resolve()) or inputs.resolve().is_relative_to(target):
        raise ValueError("Output and model inputs must be separate")
    base_bytes = config_path.read_bytes()
    config, fitting_ids = full_fitting_config(json.loads(base_bytes), inputs)
    if sha256(checkpoint.read_bytes()).hexdigest() != config["checkpoint_sha256"]:
        raise ValueError("Checkpoint does not match pinned bytes")
    available = available_physical_bytes()
    if available < memory_bytes + GIB:
        raise ValueError("Insufficient free physical memory for cap plus 1 GiB headroom")
    out.mkdir(parents=True, exist_ok=False)
    derived = out / "probe-config.json"
    derived.write_text(json.dumps(config, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    report = {"schema_version": 1, "evidence_status": "development_only_resource_probe",
              "status": "started", "model": model,
              "started_at": datetime.now(timezone.utc).isoformat(),
              "base_config_sha256": sha256(base_bytes).hexdigest(),
              "probe_config_sha256": sha256(derived.read_bytes()).hexdigest(),
              "fitting_count": len(fitting_ids), "calibration_probe_count": 1,
              "input_size_px": config["input_size_px"],
              "available_physical_bytes_at_start": available,
              "limits": {"process_committed_bytes": memory_bytes, "wall_seconds": timeout_seconds,
                         "threads": config["threads"], "child_processes": 1},
              "limitations": ["Provisional preparation and resolution; no final-test inference or threshold calibration.",
                              "Single local resource sample, not defect quality, model comparison or VPS readiness.",
                              "Committed memory cap differs from physical working set; other apps may change free RAM.",
                              "A nonzero exit alone does not identify a memory-limit failure."]}

    def save():
        (out / "profile.json").write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    save()
    try:
        command = [sys.executable, "-c", GATED_WORKER, "--model", model, "--inputs", str(inputs.resolve()),
                   "--checkpoint", str(checkpoint.resolve()), "--config", str(derived.resolve()),
                   "--output-dir", str((out / "worker").resolve())]
        report.update(bounded_process(command, memory_bytes, timeout_seconds))
        worker_path = out / "worker/result.json"
        worker = json.loads(worker_path.read_text(encoding="utf-8")) if worker_path.exists() else {}
        report["worker_report_sha256"] = sha256(worker_path.read_bytes()).hexdigest() if worker else None
        report["worker_stage"] = worker.get("stage")
        success = (report["worker_status"] == "exited" and report["worker_exit_code"] == 0
                   and worker.get("status") == "success" and worker.get("config") == config
                   and worker.get("fitting_ids") == fitting_ids and worker.get("all_fitting_inputs_used") is True
                   and len(worker.get("outputs", [])) == 1 and report["peak_process_committed_bytes"] > 0)
        report["status"] = "success" if success else "incomplete"
    except (OSError, ValueError, KeyError) as error:
        report.update(status="failed", error_type=type(error).__name__)
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    save()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("padim", "patchcore"), required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/specialist-smoke.v1.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--memory-mib", type=int, default=3072)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    args = parser.parse_args(argv)
    try:
        report = profile(args.model, args.inputs, args.checkpoint, args.config, args.output_dir,
                         args.memory_mib * 1024**2, args.timeout_seconds)
    except (OSError, ValueError, KeyError):
        print("FAIL resource probe: check pinned inputs, free RAM, limits and new artifacts directory")
        return 1
    print(f"{report['status'].upper()} {args.model}: full-normal-fitting resource probe; no final evaluation")
    return 0 if report["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
