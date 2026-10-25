"""Generated images and simulated requests only; no real credentials/network."""

from copy import deepcopy
from datetime import timedelta
import json

import pytest

from pipeline import run_gemini_comparison as runner
from pipeline import run_gemini_trial as legacy
from pipeline import run_gemini_evaluation as evaluation
from pipeline import check_gemini_metadata as metadata
from pipeline.api_contracts import ApiEvidence, request_fingerprint
from pipeline.gemini_transport import outcome, send_once
from test_gemini_evaluation import prepared as prepared, success
from test_gemini_trial import Reply, envelope, FAKE_KEY


def access_for(model, clock, remaining=20):
    return {"provider": "gemini", "model_id": model, "evidence_sha256": "c" * 64,
        "verified_at": legacy.stamp(clock.now()), "valid_until": legacy.stamp(clock.now() + timedelta(hours=4)),
        "free_execution_verified": True, "paid_execution_disabled": True, "terms_and_data_use_verified": True,
        "requests_per_minute": 5, "input_tokens_per_minute": 250000,
        "requests_per_day": 20, "remaining_requests_today": remaining}


@pytest.mark.parametrize("model", metadata.COMPARISON_MODELS)
def test_model_specific_payloads_preserve_prompt_reference_and_label_free_inputs(prepared, model):
    package, _, old_plan, *_ = prepared
    plan, fresh = runner.prepare_trial(package, model)
    assert plan["reference"] == old_plan["reference"]
    assert plan["configuration"]["prompt"] == old_plan["configuration"]["prompt"]
    payload = legacy.build_payload(plan, plan["probes"][0], package / "model-inputs")
    expected = {"thinkingBudget": 0} if model.startswith('gemini-2.5-') else {"thinkingLevel": "low"}
    assert payload["generationConfig"]["thinkingConfig"] == expected
    assert all(text not in json.dumps(payload) for text in ('source_member', 'ground_truth', '"label"', str(package)))
    assert fresh["predictions"][0]["request_sha256"] == request_fingerprint(fresh["run"], fresh["run"]["inputs"][0])
    assert runner.prepare_trial(package, model)[0] == plan
    with pytest.raises(ValueError): legacy.prepare(package, plan["configuration"], model)


def test_snapshot_ledger_counts_trial_evaluation_failures_unknowns_and_preserves_headroom(prepared, tmp_path):
    package, *_, clock = prepared
    model = metadata.COMPARISON_MODELS[0]
    plan, evidence = runner.prepare_trial(package, model, now=clock.now())
    root = tmp_path / "ledger"; output = root / "trial"; output.mkdir(parents=True)
    access = access_for(model, clock, remaining=4)
    legacy.save(output, evidence)
    current = lambda: runner.current_allowance(access, root, model, now=clock.now)
    calls = []
    def send(*_): calls.append(1); return outcome("timeout", "timeout")
    with pytest.raises(runner.AllowancePause):
        evaluation.execute_batch(plan, evidence, package / "model-inputs", output, access,
            budget=6, send=send, current_access=current, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep)
    assert len(calls) == 3  # Snapshot says four left: preserve one, including retries.
    assert len(evidence["predictions"][0]["attempts"]) == 3
    assert not evidence["predictions"][1]["attempts"]
    # A new run/configuration does not reset the same model's daily allowance.
    other = root / "evaluation"; other.mkdir()
    copy = deepcopy(evidence)
    copy["run"]["run_id"] = "fixture-other-run"
    for p, item in zip(copy["predictions"], copy["run"]["inputs"], strict=True):
        p["run_id"] = "fixture-other-run"
        p["request_sha256"] = request_fingerprint(copy["run"], item)
    legacy.save(other, copy)
    with pytest.raises(runner.AllowancePause): current()
    assert access["remaining_requests_today"] == 4


def test_new_snapshot_does_not_invent_a_daily_reset_and_stale_access_fails(prepared, tmp_path):
    package, *_, clock = prepared
    model = metadata.COMPARISON_MODELS[1]
    _, evidence = runner.prepare_trial(package, model, now=clock.now())
    root = tmp_path / "ledger"; output = root / "trial"; output.mkdir(parents=True)
    access = access_for(model, clock)
    attempt = {"number": 1, "started_at": legacy.stamp(clock.now()), "finished_at": None, "latency_ms": None,
               **outcome("unknown_outcome", "interrupted")}
    evidence["predictions"][0].update(execution_state="terminal", status="unknown_outcome", attempts=[attempt])
    legacy.save(output, evidence)
    assert runner.current_allowance(access, root, model, now=clock.now)["remaining_requests_today"] == 19
    clock.sleep(86400)
    with pytest.raises(ValueError): runner.current_allowance(access, root, model, now=clock.now)
    renewed = access_for(model, clock, remaining=7)
    assert runner.current_allowance(renewed, root, model, now=clock.now)["remaining_requests_today"] == 7


def test_qualified_model_freezes_all_115_members_and_resumes_without_repeating_success(prepared, tmp_path):
    package, *_, clock = prepared
    model = metadata.COMPARISON_MODELS[0]
    plan, evidence = runner.prepare_trial(package, model, now=clock.now())
    root = tmp_path / "runs"; output = root / evidence["run"]["run_id"]; output.mkdir(parents=True)
    access = access_for(model, clock)
    current = lambda: runner.current_allowance(access, root, model, now=clock.now)
    evidence = evaluation.execute_batch(plan, evidence, package / "model-inputs", output, access,
        send=success, budget=6, current_access=current, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep)
    assert evidence["run"]["state"] == "complete"
    frozen, fresh = runner.prepare_evaluation(package, model, evidence, plan, now=clock.now)
    assert len(frozen["probes"]) == 115
    assert frozen["configuration"]["thinking_configs"] == plan["configuration"]["thinking_configs"]
    assert "thinking_level" not in frozen["configuration"]
    destination = root / fresh["run"]["run_id"]; destination.mkdir()
    legacy.save(destination, fresh)
    calls = []
    def send(model, payload, timeout): calls.append(payload); return success()
    for _ in range(2):
        evaluation.execute_batch(frozen, fresh, package / "model-inputs", destination, access,
            send=send, budget=4, current_access=current, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep,
            earliest_start=lambda: runner.next_model_start(root, model, 24))
    assert len(calls) == 8 and sum(p["status"] == "success" for p in fresh["predictions"]) == 8
    assert runner.current_allowance(access, root, model, now=clock.now)["remaining_requests_today"] == 10
    starts = sorted(a["started_at"] for a in runner.model_attempts(root, model))
    from datetime import datetime
    stamps = [datetime.fromisoformat(s.replace("Z", "+00:00")) for s in starts]
    assert all((b - a).total_seconds() >= 24 for a, b in zip(stamps, stamps[1:]))
    failed = deepcopy(evidence); failed["predictions"][0]["status"] = "timeout"
    with pytest.raises(ValueError): runner.prepare_evaluation(package, model, failed, plan)
    changed = deepcopy(plan); changed["configuration"]["prompt"] += " changed"
    with pytest.raises(ValueError): runner.prepare_evaluation(package, model, evidence, changed)


def test_cli_offline_never_sends_and_reuses_saved_bytes(prepared, tmp_path, monkeypatch, capsys):
    package = prepared[0]
    monkeypatch.setattr(runner, "ROOT", tmp_path / "workspace")
    monkeypatch.setattr(evaluation, "execute_batch", lambda *_a, **_k: pytest.fail("offline sent a request"))
    args = ["--package", str(package), "--model", metadata.COMPARISON_MODELS[0]]
    assert runner.main(args) == 0
    path = next((runner.ROOT / "artifacts/gemini-comparisons").glob("*/evidence.json"))
    before = path.read_bytes()
    assert runner.main(args) == 0 and path.read_bytes() == before
    assert "0 submissions" in capsys.readouterr().out


def test_live_without_access_refuses_before_output_and_transport_rejects_other_models(prepared, tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path / "workspace")
    assert runner.main(["--package", str(prepared[0]), "--model", metadata.COMPARISON_MODELS[0], "--execute"]) == 1
    assert not runner.ROOT.exists()
    with pytest.raises(ValueError): send_once("other-provider-model", b"TEST", FAKE_KEY)


@pytest.mark.parametrize("model", metadata.COMPARISON_MODELS)
def test_new_model_transport_only_uses_fixed_google_endpoint(model):
    def open_request(request, timeout):
        assert request.full_url == metadata.HOST + model + ":generateContent"
        assert request.get_header("X-goog-api-key") == FAKE_KEY
        assert request.data == b"TEST PAYLOAD" and timeout == 55
        return Reply(envelope())
    opener = type("Opener", (), {"open": staticmethod(open_request)})()
    assert send_once(model, b"TEST PAYLOAD", FAKE_KEY, opener)["status"] == "success"
