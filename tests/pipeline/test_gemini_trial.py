"""Generated pictures and simulated provider responses only; never use .env/network."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError, URLError

from PIL import Image
import pytest

from pipeline.api_contracts import ApiEvidence
from pipeline import gemini_transport as transport
from pipeline import run_gemini_trial as runner


CONFIG = Path(__file__).resolve().parents[2] / "configs/gemini-trial.v1.json"
FAKE_KEY = "FAKE-TEST-KEY-NEVER-A-CREDENTIAL"


class Clock:
    def __init__(self):
        self.value = datetime(2026, 10, 24, 12, tzinfo=timezone.utc)
        self.ticks = 0

    def now(self):
        return self.value

    def monotonic(self):
        return self.ticks

    def sleep(self, seconds):
        self.value += timedelta(seconds=seconds)
        self.ticks += seconds


def envelope(decision="looks_acceptable", **updates):
    data = {"modelVersion": "gemini-test-version", "usageMetadata": {
        "promptTokenCount": 1234, "candidatesTokenCount": 25, "thoughtsTokenCount": 12},
        "candidates": [{"finishReason": "STOP", "content": {"parts": [
            {"text": json.dumps({"decision": decision, "observation": "TEST ONLY: generated image looks uniform."})}]}}]}
    data.update(updates)
    return json.dumps(data).encode()


@pytest.fixture
def prepared(tmp_path):
    package = tmp_path / "package"
    root = package / "model-inputs"
    (root / "images").mkdir(parents=True)
    images = []
    for n in range(1, 5):
        name = f"img-{n:06}"
        path = root / f"images/{name}.png"
        Image.new("RGB", (24, 24), (n * 40, 20, 10)).save(path)
        images.append({"image_id": name, "path": f"images/{name}.png",
                       "sha256": sha256(path.read_bytes()).hexdigest(),
                       "dimensions": {"width_px": 24, "height_px": 24}})
    (root / "fitting.json").write_text(json.dumps({"schema_version": 1, "evidence_status": "development_only", "images": images}), encoding="utf-8")
    (package / "preparation.json").write_text(json.dumps({"evidence_status": "development_only",
        "manifest_sha256": "a" * 64, "indexes": {"fitting": {"sha256": runner.digest(root / "fitting.json"), "count": 4}}}), encoding="utf-8")
    config = runner.read_json(CONFIG)
    clock = Clock()
    plan, evidence = runner.prepare(package, config, "gemini-3.8-flash", now=clock.now())
    output = tmp_path / "run"
    output.mkdir()
    access = {"provider": "gemini", "model_id": "gemini-3.8-flash", "evidence_sha256": "b" * 64,
              "verified_at": "2026-10-24T00:00:00Z", "valid_until": "2026-10-26T00:00:00Z",
              "free_execution_verified": True, "paid_execution_disabled": True, "terms_and_data_use_verified": True,
              "requests_per_minute": 5, "input_tokens_per_minute": 250000,
              "requests_per_day": 20, "remaining_requests_today": 20}
    return package, plan, evidence, output, access, clock


def run(prepared, send):
    package, plan, evidence, output, access, clock = prepared
    return runner.execute(plan, evidence, package / "model-inputs", output, access,
                          send=send, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep)


def success(*_):
    return transport.parse_envelope(envelope(), FAKE_KEY)


def test_offline_preparation_binds_hashes_and_hides_all_evaluator_data(prepared):
    package, plan, evidence, _, _, clock = prepared
    assert plan["reference"]["image_id"] == "img-000001"
    assert [i["image_id"] for i in plan["probes"]] == ["img-000002", "img-000003"]
    assert [p["execution_state"] for p in evidence["predictions"]] == ["pending", "pending"]
    assert runner.prepare(package, plan["configuration"], plan["model_id"], now=clock.now())[0] == plan
    payload = runner.build_payload(plan, plan["probes"][0], package / "model-inputs")
    assert len([p for p in payload["contents"][0]["parts"] if "inlineData" in p]) == 2
    serialized = json.dumps(payload)
    assert all(text not in serialized for text in (str(package), "sha256", "evaluation", "mask", "label"))
    assert payload["generationConfig"]["responseJsonSchema"]["required"] == ["decision", "observation"]
    assert payload["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "low"}


@pytest.mark.parametrize("change", ["hash", "schema", "model", "config", "pixels"])
def test_preparation_refuses_changed_or_unsupported_inputs(prepared, change):
    package, plan, _, _, _, _ = prepared
    config, model = deepcopy(plan["configuration"]), plan["model_id"]
    if change == "hash":
        (package / "model-inputs/fitting.json").write_text("{}", encoding="utf-8")
    elif change == "schema":
        config["schema_version"] = 2
    elif change == "model":
        model = "different-model"
    elif change == "config":
        config["max_requests_per_model"] = 100
    else:
        (package / "model-inputs/images/img-000002.png").write_bytes(b"broken")
    with pytest.raises(ValueError):
        runner.prepare(package, config, model)


def test_successes_are_saved_before_advancing_and_not_repeated(prepared):
    calls = []
    def send(model, payload, timeout):
        saved = runner.read_json(prepared[3] / "evidence.json")
        current = saved["predictions"][len(calls)]
        assert current["attempts"][-1]["status"] == "unknown_outcome"
        assert current["status"] == "unknown_outcome"
        calls.append((model, timeout, prepared[5].now()))
        prepared[5].sleep(1)
        return success()
    result = run(prepared, send)
    assert result["run"]["state"] == "complete"
    assert len(calls) == 2
    assert (calls[1][2] - calls[0][2]).total_seconds() >= 65
    assert all(p["status"] == "success" for p in result["predictions"])
    ApiEvidence.model_validate(runner.read_json(prepared[3] / "evidence.json"))
    run(prepared, lambda *_: pytest.fail("Completed work repeated"))


@pytest.mark.parametrize("reason,status", [("server_5xx", "provider_error"), ("transport", "provider_error"), ("timeout", "timeout")])
def test_transient_errors_retry_at_most_three_times_then_move_on(prepared, reason, status):
    calls = []
    def send(*_):
        calls.append(prepared[5].now())
        return transport.outcome(status, reason)
    evidence = run(prepared, send)
    assert len(calls) == 6
    assert all(len(p["attempts"]) == 3 for p in evidence["predictions"])
    assert evidence["run"]["state"] == "complete"
    assert all((b - a).total_seconds() >= 65 for a, b in zip(calls, calls[1:]))


def test_retry_honors_longer_provider_guidance_and_runtime_budget(prepared):
    def send(*_):
        result = transport.outcome("provider_error", "server_5xx")
        result["retry_not_before"] = transport.stamp(prepared[5].now() + timedelta(hours=1))
        return result
    evidence = run(prepared, send)
    assert evidence["run"]["state"] == "paused"
    assert len(evidence["predictions"][0]["attempts"]) == 1
    assert prepared[5].ticks == 0  # Pause rather than blocking for an hour.


def test_quota_pauses_and_restart_waits_before_retry(prepared):
    def quota(*_):
        result = transport.outcome("provider_error", "quota")
        result["retry_not_before"] = transport.stamp(prepared[5].now() + timedelta(seconds=120))
        return result
    evidence = run(prepared, quota)
    assert evidence["run"]["state"] == "paused"
    assert evidence["predictions"][0]["execution_state"] == "quota_paused"
    assert evidence["predictions"][1]["attempts"] == []
    evidence = run(prepared, success)
    assert evidence["run"]["state"] == "complete"
    starts = [a["started_at"] for a in evidence["predictions"][0]["attempts"]]
    assert (runner._time(starts[1]) - runner._time(starts[0])).total_seconds() >= 120


@pytest.mark.parametrize("reason", ["authentication", "entitlement"])
def test_access_errors_stop_all_further_calls(prepared, reason):
    evidence = run(prepared, lambda *_: transport.outcome("provider_error", reason))
    assert evidence["run"]["state"] == "stopped"
    assert evidence["predictions"][1]["attempts"] == []
    run(prepared, lambda *_: pytest.fail("Stopped provider resumed"))


@pytest.mark.parametrize("status,reason", [("invalid_response", "schema"), ("refusal", "refusal")])
def test_terminal_received_failures_are_not_retried(prepared, status, reason):
    evidence = run(prepared, lambda *_: transport.outcome(status, reason, b"TEST ONLY"))
    assert evidence["run"]["state"] == "complete"
    assert all(len(p["attempts"]) == 1 for p in evidence["predictions"])
    assert all(p["status"] == status for p in evidence["predictions"])


def test_crash_after_submission_is_durable_and_is_not_automatically_retried(prepared):
    def crash(*_):
        raise KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt):
        run(prepared, crash)
    saved = runner.read_json(prepared[3] / "evidence.json")
    assert saved["predictions"][0]["status"] == "unknown_outcome"
    prepared[2].clear()
    prepared[2].update(saved)
    evidence = run(prepared, lambda *_: pytest.fail("Unknown submission repeated"))
    assert evidence["run"]["state"] == "stopped"


def test_no_call_if_submission_snapshot_cannot_be_saved(prepared, monkeypatch):
    def fail(*_):
        raise OSError("TEST ONLY")
    monkeypatch.setattr(runner, "atomic_json", fail)
    with pytest.raises(OSError):
        run(prepared, lambda *_: pytest.fail("Submitted without durable record"))


@pytest.mark.parametrize("field,value", [("free_execution_verified", False), ("terms_and_data_use_verified", False),
    ("paid_execution_disabled", False), ("remaining_requests_today", 6), ("valid_until", "2026-10-23T00:00:00Z")])
def test_preflight_refuses_missing_access_use_or_budget(prepared, field, value):
    prepared[4][field] = value
    with pytest.raises(ValueError):
        run(prepared, lambda *_: pytest.fail("Unverified request sent"))
    assert not (prepared[3] / "evidence.json").exists()


@pytest.mark.parametrize("usage", [None, {"input_tokens": None, "output_tokens": 20}, {"input_tokens": 16001, "output_tokens": 20}])
def test_missing_or_excess_input_usage_stops_further_successful_calls(prepared, usage):
    def send(*_):
        result = success()
        result["usage"] = usage
        return result
    evidence = run(prepared, send)
    assert evidence["run"]["state"] == "stopped"
    assert evidence["predictions"][0]["status"] == "success"
    assert evidence["predictions"][1]["attempts"] == []


def test_changed_image_before_submission_is_refused(prepared):
    (prepared[0] / "model-inputs/images/img-000002.png").write_bytes(b"changed")
    with pytest.raises(ValueError, match="Image changed"):
        run(prepared, lambda *_: pytest.fail("Changed input submitted"))


def test_request_deadline_kills_a_real_generated_child_without_network(monkeypatch):
    actual_run = subprocess.run
    def generated_child(command, **kwargs):
        assert kwargs["timeout"] == 0.1
        return actual_run([sys.executable, "-c", "import time; time.sleep(30)"], **kwargs)
    monkeypatch.setattr(runner.subprocess, "run", generated_child)
    assert runner.supervised_request("gemini-3.8-flash", {}, timeout=0.1)["status"] == "timeout"


def test_exclusive_os_lock_blocks_a_second_owner(tmp_path):
    with runner.run_lock(tmp_path):
        with pytest.raises(OSError):
            with runner.run_lock(tmp_path):
                pytest.fail("Concurrent runner acquired lock")
    with runner.run_lock(tmp_path):
        pass  # A released lock file is reusable.


@pytest.mark.parametrize("decision", ["looks_acceptable", "needs_review", "uncertain"])
def test_parse_real_envelope_shape_and_usage(decision):
    raw = envelope(decision)
    result = transport.parse_envelope(raw, FAKE_KEY)
    assert result["status"] == "success"
    assert result["response"]["decision"] == decision
    assert result["usage"] == {"input_tokens": 1234, "output_tokens": 37}
    assert result["response_sha256"] == sha256(raw).hexdigest()


@pytest.mark.parametrize("change,expected", [
    ({"promptFeedback": {"blockReason": "SAFETY"}, "candidates": []}, "refusal"),
    ({"candidates": [{"finishReason": "SAFETY"}]}, "refusal"),
    ({"candidates": [{"finishReason": "MAX_TOKENS"}]}, "invalid_response"),
    ({"candidates": []}, "invalid_response"), ({"candidates": [None]}, "invalid_response"),
    ({"usageMetadata": None}, "invalid_response"), ({"promptFeedback": None}, "invalid_response"),
    ({"promptFeedback": {"blockReason": "UNKNOWN_VALUE"}}, "invalid_response"),
])
def test_refusal_is_distinct_from_malformed_or_truncated_output(change, expected):
    assert transport.parse_envelope(envelope(**change), FAKE_KEY)["status"] == expected


def test_provider_observation_redacts_known_key_and_local_paths():
    data = json.loads(envelope())
    data["candidates"][0]["content"]["parts"][0]["text"] = json.dumps({
        "decision": "uncertain", "observation": FAKE_KEY + " C:/private/picture.png"})
    result = transport.parse_envelope(json.dumps(data).encode(), FAKE_KEY)
    assert FAKE_KEY not in json.dumps(result)
    assert "C:/private" not in json.dumps(result)


class Reply(BytesIO):
    status = 200


def test_fixed_post_headers_and_label_free_body():
    def open_request(request, timeout):
        assert request.full_url == "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"
        assert FAKE_KEY not in request.full_url
        assert request.method == "POST" and timeout == 55
        assert request.get_header("X-goog-api-key") == FAKE_KEY
        assert request.data == b"TEST ONLY PAYLOAD"
        return Reply(envelope())
    opener = type("Opener", (), {"open": staticmethod(open_request)})()
    assert transport.send_once("gemini-3.8-flash", b"TEST ONLY PAYLOAD", FAKE_KEY, opener)["status"] == "success"


@pytest.mark.parametrize("code,reason", [(401, "authentication"), (403, "entitlement"), (429, "quota"),
    (500, "server_5xx"), (503, "server_5xx"), (400, "other_provider"), (302, "other_provider")])
def test_http_errors_are_allowlisted_and_retry_guidance_is_retained(code, reason):
    def fail(*_, **__):
        raw = json.dumps({"error": {"message": FAKE_KEY, "details": [{
            "@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "120s"}]}}).encode()
        raise HTTPError("https://example.invalid", code, FAKE_KEY, {"Retry-After": "60"}, BytesIO(raw))
    opener = type("Opener", (), {"open": staticmethod(fail)})()
    result = transport.send_once("gemini-3.8-flash", b"x", FAKE_KEY, opener)
    assert result["reason"] == reason
    assert FAKE_KEY not in json.dumps(result)
    assert (result["retry_not_before"] is not None) == (reason in {"quota", "server_5xx"})


def test_unknown_quota_reset_uses_conservative_one_day_pause():
    now = Clock().now()
    assert runner._time(transport.retry_time(b"{}", None, now, quota=True)) == now + timedelta(days=1)


@pytest.mark.parametrize("raw", [b"[]", b"null", b"broken", b'{"x":NaN}', b'{"x":1,"x":2}', b"\xff"])
def test_malformed_envelope_never_escapes_or_becomes_success(raw):
    assert transport.parse_envelope(raw, FAKE_KEY)["status"] == "invalid_response"


def test_no_sdk_redirect_proxy_or_automatic_retry(monkeypatch):
    calls = []
    def factory(*handlers):
        assert handlers[0].proxies == {}
        assert isinstance(handlers[1], transport._NoRedirect)
        def fail(*_, **__):
            calls.append(1)
            raise URLError("TEST ONLY " + FAKE_KEY)
        return type("Opener", (), {"open": staticmethod(fail)})()
    monkeypatch.setattr(transport, "build_opener", factory)
    assert transport.send_once("gemini-3.8-flash", b"x", FAKE_KEY)["reason"] == "transport"
    assert len(calls) == 1


def test_cli_prepares_and_reuses_the_same_folder_without_access_or_network(prepared, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(runner, "ROOT", tmp_path / "workspace")
    def fail(*_, **__):
        pytest.fail("Offline CLI invoked execution")
    monkeypatch.setattr(runner, "execute", fail)
    args = ["--package", str(prepared[0]), "--config", str(CONFIG), "--model", "gemini-3.8-flash"]
    assert runner.main(args) == 0
    folder = runner.ROOT / "artifacts/gemini-trials" / prepared[2]["run"]["run_id"]
    before = (folder / "evidence.json").read_bytes()
    assert runner.main(args) == 0
    assert (folder / "evidence.json").read_bytes() == before
    assert "offline preparation" in capsys.readouterr().out


def test_cli_live_flag_without_access_evidence_refuses_before_creating_output(prepared, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(runner, "ROOT", tmp_path / "workspace")
    args = ["--package", str(prepared[0]), "--config", str(CONFIG), "--model", "gemini-3.8-flash", "--execute"]
    assert runner.main(args) == 1
    assert not (runner.ROOT / "artifacts").exists()
    assert "FAIL trial" in capsys.readouterr().out


def test_unknown_worker_result_stops_and_retains_submission_record(prepared):
    evidence = run(prepared, lambda *_: transport.outcome("unknown_outcome", "interrupted"))
    assert evidence["run"]["state"] == "stopped"
    assert evidence["predictions"][0]["attempts"][0]["finished_at"] is None
    assert evidence["predictions"][1]["attempts"] == []


def test_quota_with_no_window_does_not_sleep_on_restart(prepared):
    def quota(*_):
        result = transport.outcome("provider_error", "quota")
        result["retry_not_before"] = transport.retry_time(b"{}", None, prepared[5].now(), quota=True)
        return result
    run(prepared, quota)
    run(prepared, lambda *_: pytest.fail("Quota retried before permitted window"))
    assert prepared[2]["run"]["state"] == "paused"
    assert prepared[5].ticks == 0


def test_expired_access_during_throttle_does_not_submit_next_image(prepared):
    prepared[4]["valid_until"] = "2026-10-24T12:00:30Z"
    calls = []
    def send(*_):
        calls.append(1)
        return success()
    with pytest.raises(ValueError, match="stale"):
        run(prepared, send)
    assert len(calls) == 1


def test_changed_reference_is_also_refused(prepared):
    (prepared[0] / "model-inputs/images/img-000001.png").write_bytes(b"changed")
    with pytest.raises(ValueError, match="Image changed"):
        run(prepared, lambda *_: pytest.fail("Changed reference submitted"))


def test_changed_request_code_creates_a_new_immutable_run(prepared, monkeypatch):
    monkeypatch.setattr(runner, "implementation_hashes", lambda: {"test-code": "c" * 64})
    _, fresh = runner.prepare(prepared[0], prepared[1]["configuration"], prepared[1]["model_id"])
    assert fresh["run"]["run_id"] != prepared[2]["run"]["run_id"]
    assert fresh["predictions"][0]["request_sha256"] != prepared[2]["predictions"][0]["request_sha256"]
