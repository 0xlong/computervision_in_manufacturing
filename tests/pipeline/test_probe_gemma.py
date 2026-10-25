"""Generated normal pictures and fake responses only; no key or network access."""

from io import BytesIO
from datetime import timedelta
import json
from types import SimpleNamespace
from urllib.error import HTTPError

import pytest

from pipeline import probe_gemma as runner
from pipeline import run_gemini_trial as common
from pipeline.api_contracts import check_access, request_fingerprint
from pipeline.gemini_transport import outcome, parse_envelope
from test_gemini_trial import prepared as prepared, envelope, FAKE_KEY, Reply


def trial(prepared, model=runner.MODELS[0]):
    package, _, _, output, access, clock = prepared
    plan, evidence = runner.prepare(package, model, now=clock.now())
    access.update(model_id=model, requests_per_minute=30, input_tokens_per_minute=16000,
                  requests_per_day=14400, remaining_requests_today=14400)
    return package, plan, evidence, output, access, clock


@pytest.mark.parametrize("model", runner.MODELS)
def test_normal_only_payload_and_identity(prepared, model):
    package, plan, evidence, _, _, clock = trial(prepared, model)
    assert plan["reference"] == prepared[1]["reference"]
    assert plan["configuration"]["prompt"] == prepared[1]["configuration"]["prompt"]
    assert runner.prepare(package, model, now=clock.now())[0] == plan
    assert evidence["predictions"][0]["request_sha256"] == request_fingerprint(evidence["run"], evidence["run"]["inputs"][0])
    payload = common.build_payload(plan, plan["probes"][0], package / "model-inputs")
    assert payload["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "minimal"}
    assert len([p for p in payload["contents"][0]["parts"] if "inlineData" in p]) == 2
    assert all(s not in json.dumps(payload) for s in (str(package), "ground_truth", "source_member", '"label"'))


def test_smaller_token_budget_is_checked_not_bypassed(prepared):
    *_, access, clock = trial(prepared)
    assert check_access(access, model_id=access["model_id"], now=clock.now(),
                        request_budget=3, input_token_budget=12288)
    with pytest.raises(ValueError):
        check_access(access, model_id=access["model_id"], now=clock.now(), request_budget=3, input_token_budget=16000)


@pytest.mark.parametrize("kind", ["success", "oversize", "unknown", "timeout", "quota"])
def test_journal_pacing_usage_and_bounded_stops(prepared, kind):
    package, plan, evidence, output, access, clock = trial(prepared)
    starts = []
    def send(model, payload, timeout):
        assert timeout == 60 and model == access["model_id"]
        saved = common.read_json(output / "evidence.json")
        assert any(p["attempts"] and p["attempts"][-1]["status"] == "unknown_outcome" for p in saved["predictions"])
        starts.append(clock.now())
        clock.sleep(1)
        if kind == "unknown": return outcome("unknown_outcome", "interrupted")
        if kind == "timeout": return outcome("timeout", "timeout")
        if kind == "quota":
            result = outcome("provider_error", "quota")
            result["retry_not_before"] = common.stamp(clock.now() + timedelta(days=1))
            return result
        raw = envelope(usageMetadata={"promptTokenCount": 4097 if kind == "oversize" else 1234, "candidatesTokenCount": 25})
        return parse_envelope(raw, FAKE_KEY)
    def execute():
        return common.execute(plan, evidence, package / "model-inputs", output, access,
            send=send, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep)
    execute()
    assert all((b-a).total_seconds() >= 60 for a,b in zip(starts, starts[1:]))
    assert len(starts) == (2 if kind == "success" else 3 if kind == "timeout" else 1)
    assert evidence["run"]["state"] == ("complete" if kind == "success" else "paused" if kind in {"timeout", "quota"} else "stopped")
    if kind not in {"timeout", "quota"}:
        execute()
        assert len(starts) == (2 if kind == "success" else 1)


@pytest.mark.parametrize("model", runner.MODELS)
def test_fixed_host_allowlist_and_header(prepared, model):
    def open_request(request, timeout):
        assert request.full_url == runner.HOST + model + ":generateContent"
        assert request.get_header("X-goog-api-key") == FAKE_KEY
        assert FAKE_KEY not in request.full_url
        assert timeout == 55 and request.method == "POST"
        return Reply(envelope())
    assert runner.send_once(model, b"{}", FAKE_KEY, SimpleNamespace(open=open_request))["status"] == "success"
    with pytest.raises(ValueError): runner.send_once("another-model", b"{}", FAKE_KEY)


def test_raw_error_and_credentials_do_not_escape():
    def fail(*args, **kwargs):
        raise HTTPError("https://example.invalid/", 400, "private", {}, BytesIO(FAKE_KEY.encode()))
    result = runner.send_once(runner.MODELS[0], b"{}", FAKE_KEY, SimpleNamespace(open=fail))
    assert result["reason"] == "other_provider" and FAKE_KEY not in json.dumps(result)
    assert result["response"] is None and result["response_sha256"]


def test_execute_requires_access_before_creating_output(prepared, tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path / "isolated")
    assert runner.main(["--package", str(prepared[0]), "--model", runner.MODELS[0], "--execute"]) == 1
    assert not (runner.ROOT / "artifacts").exists()
