"""Generated inputs and real Windows child processes test resource safeguards."""

from hashlib import sha256
import json
from pathlib import Path
import sys
import subprocess

from PIL import Image
import pytest

from pipeline import profile_specialist as probe


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    monkeypatch.setattr(probe, "ROOT", tmp_path)
    monkeypatch.setattr(probe, "available_physical_bytes", lambda: 8 * probe.GIB)
    root = tmp_path / "inputs"
    (root / "images").mkdir(parents=True)
    items = []
    for n in (3, 1, 2):
        name = f"img-{n:06d}"
        path = root / f"images/{name}.png"
        Image.new("RGB", (4, 4), (n, 10, 20)).save(path)
        items.append({"image_id": name, "path": f"images/{name}.png",
                      "sha256": sha256(path.read_bytes()).hexdigest(),
                      "dimensions": {"width_px": 4, "height_px": 4}})
    base = json.loads(Path("configs/specialist-smoke.v1.json").read_text())
    for split, images in (("fitting", items[:2]), ("calibration", items[2:])):
        path = root / f"{split}.json"
        path.write_text(json.dumps({"schema_version": 1, "evidence_status": "development_only", "images": images}))
        base["input_index_sha256"][split] = sha256(path.read_bytes()).hexdigest()
    checkpoint = tmp_path / "checkpoint.pth"
    checkpoint.write_bytes(b"TEST ONLY: never loaded by a model")
    base["checkpoint_sha256"] = sha256(checkpoint.read_bytes()).hexdigest()
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(base))
    return root, checkpoint, config_path, tmp_path / "artifacts/probe"


def test_full_configuration_uses_all_sorted_fitting_without_reading_evaluation(prepared):
    inputs, _, path, _ = prepared
    original = json.loads(path.read_text())
    # No evaluation index or evaluator data even exists in this generated fixture.
    config, ids = probe.full_fitting_config(original, inputs)
    assert ids == ["img-000001", "img-000003"]
    assert config["fitting_sample_count"] == 2
    assert config["calibration_sample_count"] == 1
    assert original["fitting_sample_count"] == 8
    assert {k: v for k, v in config.items() if k not in ("purpose", "fitting_sample_count")} == {
        k: v for k, v in original.items() if k not in ("purpose", "fitting_sample_count")}


@pytest.mark.parametrize("changed", ["fitting.json", "calibration.json", "images/img-000003.png"])
def test_changed_inputs_are_rejected_before_worker(prepared, changed):
    inputs, checkpoint, config, out = prepared
    (inputs / changed).write_bytes(b"TEST modified input")
    with pytest.raises(ValueError):
        probe.profile("padim", inputs, checkpoint, config, out)
    assert not out.exists()


@pytest.mark.parametrize("case", ["existing", "outside", "input_overlap", "low_ram", "checkpoint", "too_much_memory", "too_long"])
def test_bad_outputs_or_resources_never_launch(prepared, monkeypatch, case):
    inputs, checkpoint, config, out = prepared
    memory, timeout = 3 * probe.GIB, 600
    if case == "existing":
        out.mkdir(parents=True)
        (out / "keep.txt").write_text("TEST previous evidence")
    elif case == "outside":
        out = out.parents[1] / "outside"
    elif case == "input_overlap":
        monkeypatch.setattr(probe, "ROOT", inputs.parent)
        out = inputs
    elif case == "low_ram":
        monkeypatch.setattr(probe, "available_physical_bytes", lambda: 4 * probe.GIB - 1)
    elif case == "checkpoint":
        checkpoint.write_bytes(b"TEST changed checkpoint")
    elif case == "too_much_memory":
        memory += 1
    else:
        timeout = 601
    def forbidden(*args):
        pytest.fail("Invalid probe must not launch a process")
    monkeypatch.setattr(probe, "bounded_process", forbidden)
    with pytest.raises(ValueError):
        probe.profile("padim", inputs, checkpoint, config, out, memory, timeout)
    if case == "existing":
        assert (out / "keep.txt").read_text() == "TEST previous evidence"


@pytest.mark.parametrize("case", ["success", "missing", "timeout", "wrong_ids", "partial", "guard_failed"])
def test_only_complete_full_fitting_worker_can_succeed(prepared, monkeypatch, case):
    inputs, checkpoint, config, out = prepared
    def worker(command, memory, timeout):
        assert "evaluation" not in " ".join(command)
        assert memory == 3 * probe.GIB and timeout == 600
        if case == "guard_failed":
            raise OSError("TEST path that must never appear in report: C:/private")
        if case != "missing":
            worker_out = out / "worker"
            worker_out.mkdir()
            (worker_out / "result.json").write_text(json.dumps({
                "status": "success", "stage": "complete", "config": json.loads((out / "probe-config.json").read_text()),
                "fitting_ids": ["img-000001", "img-000003"] if case != "wrong_ids" else ["img-000001"],
                "all_fitting_inputs_used": case != "partial", "outputs": [{"TEST": "not a prediction"}]}))
        return {"worker_status": "timed_out" if case == "timeout" else "exited", "worker_exit_code": 0,
                "wall_seconds_including_validation": 1.5, "peak_process_committed_bytes": 1234}
    monkeypatch.setattr(probe, "bounded_process", worker)
    report = probe.profile("padim", inputs, checkpoint, config, out)
    assert report["status"] == ("success" if case == "success" else "failed" if case == "guard_failed" else "incomplete")
    assert report["fitting_count"] == 2
    assert "C:/private" not in (out / "profile.json").read_text()
    assert report == json.loads((out / "profile.json").read_text())


BOOTSTRAP = (
    "import sys; assert sys.stdin.readline() == 'RUN\\n'; "
    "from pipeline.profile_specialist import attach_current_job; attach_current_job(sys.argv[1]); "
)


@pytest.mark.skipif(sys.platform != "win32", reason="Real Windows Job Object integration")
def test_windows_memory_cap_denies_large_allocation(tmp_path):
    marker = tmp_path / "denied.txt"
    code = BOOTSTRAP + (
        "from pathlib import Path\n"
        "try:\n    allocation=bytearray(512*1024**2)\n"
        "except MemoryError:\n    Path(sys.argv[2]).write_text('TEST allocation denied')\n"
    )
    result = probe.bounded_process([sys.executable, "-c", code, str(marker)], 128 * 1024**2, 15)
    assert result["worker_status"] == "exited" and result["worker_exit_code"] == 0
    assert marker.read_text() == "TEST allocation denied"
    assert 0 < result["peak_process_committed_bytes"] <= 128 * 1024**2


@pytest.mark.skipif(sys.platform != "win32", reason="Real Windows Job Object integration")
def test_windows_timeout_stops_actual_interpreter(tmp_path):
    pid_file = tmp_path / "pid.txt"
    code = BOOTSTRAP + "import os,time; from pathlib import Path; Path(sys.argv[2]).write_text(str(os.getpid())); time.sleep(30)"
    result = probe.bounded_process([sys.executable, "-c", code, str(pid_file)], 128 * 1024**2, 3)
    assert result["worker_status"] == "timed_out"
    assert result["wall_seconds_including_validation"] < 10
    assert_interpreter_stopped(pid_file)


def assert_interpreter_stopped(pid_file):
    # Check the actual interpreter, which may differ from Popen's venv-launcher PID.
    import ctypes
    from ctypes import wintypes
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    api.OpenProcess.restype = wintypes.HANDLE
    api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = api.OpenProcess(0x100000, False, int(pid_file.read_text()))
    if handle:
        try:
            assert api.WaitForSingleObject(handle, 1000) == 0
        finally:
            api.CloseHandle(handle)


@pytest.mark.skipif(sys.platform != "win32", reason="Real Windows Job Object integration")
def test_supervisor_exit_stops_worker_even_without_cleanup(tmp_path):
    pid_file = tmp_path / "actual-worker-pid.txt"
    child_code = BOOTSTRAP + "import os,time; from pathlib import Path; Path(sys.argv[2]).write_text(str(os.getpid())); time.sleep(30)"
    parent_code = (
        "import os,sys,time,subprocess\n"
        "from pathlib import Path\n"
        "from pipeline.profile_specialist import WindowsJob\n"
        "job=WindowsJob(128*1024**2)\n"
        "child=subprocess.Popen([sys.executable,'-c',sys.argv[1],job.name,sys.argv[2]],stdin=subprocess.PIPE,"
        "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)\n"
        "child.stdin.write(b'RUN\\n'); child.stdin.flush()\n"
        "for _ in range(500):\n"
        "    if Path(sys.argv[2]).exists(): os._exit(0)\n"
        "    time.sleep(0.01)\n"
        "os._exit(1)\n"
    )
    result = subprocess.run([sys.executable, "-c", parent_code, child_code, str(pid_file)],
                            timeout=10, cwd=probe.ROOT, creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.returncode == 0
    assert_interpreter_stopped(pid_file)


@pytest.mark.skipif(sys.platform != "win32", reason="Real Windows Job Object integration")
def test_missing_supervisor_job_cannot_release_model_execution(tmp_path):
    marker = tmp_path / "must-not-run.txt"
    code = BOOTSTRAP.replace("sys.argv[1]", "'Local\\\\inspection-job-that-does-not-exist'")
    code += "from pathlib import Path; Path(sys.argv[2]).write_text('must not run')"
    result = probe.bounded_process([sys.executable, "-c", code, str(marker)], 128 * 1024**2, 15)
    assert result["worker_exit_code"] != 0
    assert not marker.exists()
