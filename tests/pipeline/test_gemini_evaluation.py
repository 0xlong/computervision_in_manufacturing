"""Generated clean images and fake responses, without credentials or network."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image
import pytest

from pipeline import run_gemini_evaluation as runner
from pipeline import run_gemini_trial as trial_runner
from pipeline.api_contracts import ApiEvidence
from pipeline.gemini_transport import outcome


class Clock:
    value = datetime(2026, 10, 24, 12, tzinfo=timezone.utc)
    tick = 0
    def now(self): return self.value
    def monotonic(self): return self.tick
    def sleep(self, n): self.tick += n; self.value += timedelta(seconds=n)


def success(*_):
    return {**outcome("invalid_response", "schema"), "status": "success", "reason": "none", "response_sha256": "a" * 64,
            "response": {"decision": "looks_acceptable", "observation": "TEST ONLY: uniform generated pixels."},
            "reported_model_version": "synthetic-version", "usage": {"input_tokens": 50, "output_tokens": 10}}


@pytest.fixture
def prepared(tmp_path):
    clock = Clock()
    package = tmp_path / "package"
    model_root = package / "model-inputs"
    (model_root / "images").mkdir(parents=True)
    groups = {}
    for split, start, stop in (("fitting", 201, 205), ("evaluation", 1, 116)):
        images = []
        for n in range(start, stop):
            path = model_root / f"images/img-{n:06}.png"
            Image.new("RGB", (4, 4), (n, 20, 30)).save(path)
            images.append({"image_id": f"img-{n:06}", "path": f"images/img-{n:06}.png",
                           "sha256": sha256(path.read_bytes()).hexdigest(), "dimensions": {"width_px": 4, "height_px": 4}})
        index = {"schema_version": 1, "evidence_status": "development_only", "images": images}
        (model_root / f"{split}.json").write_text(json.dumps(index), encoding="utf-8")
        groups[split] = {"sha256": runner.digest(model_root / f"{split}.json"), "count": len(images)}
    (package / "preparation.json").write_text(json.dumps({"evidence_status": "development_only", "manifest_sha256": "b" * 64,
        "indexes": groups}), encoding="utf-8")
    trial_plan, trial = trial_runner.prepare(package, trial_runner.read_json(runner.ROOT / "configs/gemini-trial.v1.json"),
                                             "gemini-3.5-flash-lite", now=clock.now())
    access = {"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "evidence_sha256": "c" * 64,
        "verified_at": "2026-10-24T00:00:00Z", "valid_until": "2026-10-25T00:00:00Z",
        "free_execution_verified": True, "paid_execution_disabled": True, "terms_and_data_use_verified": True,
        "requests_per_minute": 15, "input_tokens_per_minute": 250000, "requests_per_day": 500, "remaining_requests_today": 498}
    trial_output = tmp_path / "trial"; trial_output.mkdir()
    trial = trial_runner.execute(trial_plan, trial, model_root, trial_output, access,
        send=success, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep)
    plan, evidence = runner.prepare(package, trial, trial_plan, now=clock.now)
    output = tmp_path / "evaluation"; output.mkdir()
    return package, trial, trial_plan, plan, evidence, output, access, clock


def batch(prepared, send=success, budget=12):
    package, _, _, plan, evidence, output, access, clock = prepared
    return runner.execute_batch(plan, evidence, package / "model-inputs", output, access, budget=budget,
        send=send, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep)


def test_frozen_plan_keeps_all_members_and_no_label_access(prepared):
    package, trial, trial_plan, plan, evidence, _, _, clock = prepared
    assert len(evidence["predictions"]) == 115
    assert plan["configuration"]["prompt"] == trial_plan["configuration"]["prompt"]
    assert plan["reference"] == trial_plan["reference"]
    assert not (package / "evaluator").exists()
    assert runner.prepare(package, trial, trial_plan, now=clock.now)[0] == plan
    assert not any(word in json.dumps(plan) for word in ('"label"', 'source_member', 'ground_truth'))
    changed = deepcopy(trial_plan); changed["configuration"]["prompt"] += " changed"
    with pytest.raises(ValueError): runner.prepare(package, trial, changed)


def test_batches_resume_without_repeating_successes_and_finish_complete_membership(prepared):
    calls = []
    def send(*args): calls.append(1); return success()
    assert batch(prepared, send)["run"]["state"] == "paused"
    assert len(calls) == 12
    for _ in range(9): batch(prepared, send)
    assert len(calls) == 115 and prepared[4]["run"]["state"] == "complete"
    assert all(p["status"] == "success" for p in prepared[4]["predictions"])
    batch(prepared, send)
    assert len(calls) == 115
    ApiEvidence.model_validate(prepared[4])


def test_unknown_is_journaled_before_send_and_stops_restart(prepared):
    def send(*_):
        saved = json.loads((prepared[5] / "evidence.json").read_text())
        assert saved["predictions"][0]["status"] == "unknown_outcome"
        return outcome("unknown_outcome", "interrupted")
    assert batch(prepared, send)["run"]["state"] == "stopped"
    assert batch(prepared, lambda *_: pytest.fail("must not repeat unknown submission"))["run"]["state"] == "stopped"


@pytest.mark.parametrize("reason,state", [("quota", "paused"), ("authentication", "stopped"), ("entitlement", "stopped")])
def test_provider_quota_access_stops(prepared, reason, state):
    result = outcome("provider_error", reason)
    if reason == "quota": result["retry_not_before"] = "2026-10-25T12:00:00Z"
    assert batch(prepared, lambda *_: result)["run"]["state"] == state
    if reason == "quota": batch(prepared, lambda *_: pytest.fail("quota not yet available"))


def test_transient_retries_are_bounded_and_other_images_continue(prepared):
    batch(prepared, lambda *_: outcome("timeout", "timeout"), budget=4)
    first, second = prepared[4]["predictions"][:2]
    assert len(first["attempts"]) == 3 and len(second["attempts"]) == 1
    assert first["status"] == "timeout"
    stamps = [datetime.fromisoformat(a["started_at"].replace("Z", "+00:00")) for p in prepared[4]["predictions"] for a in p["attempts"]]
    assert all((b - a).total_seconds() >= 10 for a, b in zip(stamps, stamps[1:]))


def test_access_freshness_budget_and_missing_usage_fail_closed(prepared):
    prepared[6]["valid_until"] = "2026-10-24T01:00:00Z"
    with pytest.raises(ValueError): batch(prepared)
    assert not any(p["attempts"] for p in prepared[4]["predictions"])
    prepared[6]["valid_until"] = "2026-10-25T00:00:00Z"
    prepared[6]["remaining_requests_today"] = 12
    with pytest.raises(ValueError): batch(prepared)
    prepared[6]["remaining_requests_today"] = 498
    result = success(); result["usage"] = None
    assert batch(prepared, lambda *_: result)["run"]["state"] == "stopped"


def test_disk_failure_before_journal_prevents_submission(prepared, monkeypatch):
    monkeypatch.setattr(runner, "save", lambda *_: (_ for _ in ()).throw(OSError("TEST disk unavailable")))
    with pytest.raises(OSError): batch(prepared, lambda *_: pytest.fail("must not send before durable journal"))
