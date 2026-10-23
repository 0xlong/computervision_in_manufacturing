"""Invented API answers only. No keys, network, images or real AI evidence."""

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError
import pytest

from pipeline.api_contracts import (
    ApiEvidence, RESPONSE_SCHEMA_SHA256, SCHEMA, check_access, fingerprint,
    main, next_action, parse_response, read_evidence, request_fingerprint,
    sanitized_result,
)


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/api-evidence.fixture.json"


@pytest.fixture
def data():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def rebind(data):
    images = {i["image_id"]: i for i in data["run"]["inputs"]}
    for p in data["predictions"]:
        p["request_sha256"] = request_fingerprint(data["run"], images[p["image_id"]])


def test_fixture_and_pydantic_share_authoritative_schema(data):
    Draft202012Validator(SCHEMA, format_checker=FormatChecker()).validate(data)
    saved = read_evidence(FIXTURE)
    assert saved.root == data
    assert json.loads(saved.model_dump_json()) == data
    assert data["evidence_status"] == "fixture"
    assert data["run"]["hashes"]["response_schema"] == RESPONSE_SCHEMA_SHA256
    # Pydantic must not retain mutable caller-owned dictionaries.
    data["predictions"].clear()
    assert len(saved.root["predictions"]) == 6


@pytest.mark.parametrize("decision,review", [
    ("looks_acceptable", False), ("needs_review", True), ("uncertain", True),
])
def test_three_valid_categorical_responses(decision, review):
    answer = parse_response(json.dumps({"decision": decision, "observation": "TEST ONLY: visible marks."}))
    assert (answer["decision"] != "looks_acceptable") is review
    result = sanitized_result(status="success", reason="none", raw_response=json.dumps(answer))
    assert result["status"] == "success"
    assert result["response"] == answer


@pytest.mark.parametrize("text", [
    '{"decision":"looks_acceptable","decision":"uncertain","observation":"x"}',
    '{"decision":"normal","observation":"x"}',
    '{"decision":"uncertain","observation":"   "}',
    '{"decision":"uncertain","observation":"x","confidence":0.8}',
    '{"decision":"uncertain","observation":"x","extra":NaN}',
    '{"decision":"uncertain","observation":1e999}',
    '{"decision":"uncertain"}', '[1,2]', 'null', '```json\n{}\n```',
    '{broken', '{"decision":"uncertain","observation":"' + 'a' * 601 + '"}',
])
def test_invalid_response_is_recorded_without_echoing_raw_text(text):
    with pytest.raises(ValueError, match="Invalid structured API response") as caught:
        parse_response(text)
    assert text not in str(caught.value)
    result = sanitized_result(status="success", reason="none", raw_response=text)
    assert result["status"] == "invalid_response"
    assert result["reason"] == "schema"
    assert result["response"] is None
    assert len(result["response_sha256"]) == 64


@pytest.mark.parametrize("path,value", [
    (("schema_version",), 2), (("schema_version",), True),
    (("evidence_status",), "release_approved"),
    (("run", "provider"), "openai"),
    (("run", "track_id"), "other"),
    (("run", "created_at"), "2026-10-24T10:00:00+02:00"),
    (("run", "created_at"), "2026-02-30T00:00:00Z"),
    (("run", "max_attempts"), 4),
    (("run", "request_timeout_seconds"), 61),
    (("run", "capabilities", "heatmap"), True),
    (("run", "inputs", 0, "sha256"), "a" * 64 + "\n"),
    (("predictions", 0, "attempts", 0, "latency_ms"), float("inf")),
    (("predictions", 0, "attempts", 0, "usage", "input_tokens"), -1),
    (("predictions", 0, "attempts", 0, "usage", "input_tokens"), True),
    (("predictions", 0, "attempts", 0, "reported_model_version"), "C:/private/model"),
    (("predictions", 0, "attempts", 0, "headers"), {"Authorization": "TEST-ONLY"}),
    (("predictions", 0, "attempts", 0, "error_message"), "C:/private/error"),
    (("predictions", 0, "attempts", 0, "response", "observation"), ""),
])
def test_schema_and_envelope_both_reject_bad_fields(data, path, value):
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    assert not Draft202012Validator(SCHEMA, format_checker=FormatChecker()).is_valid(data)
    with pytest.raises(ValidationError):
        ApiEvidence.model_validate(data)


@pytest.mark.parametrize("change", [
    "duplicate_input", "duplicate_prediction", "missing_prediction", "foreign_image",
    "foreign_run", "changed_prompt", "changed_image", "changed_schema",
    "wrong_status", "fake_success", "bad_number", "backwards_time", "before_creation",
    "missing_raw_hash", "pending_result", "incomplete_run", "retry_success",
    "retry_too_soon", "too_many_attempts", "refusal_retry", "unknown_retry",
])
def test_inconsistent_identity_attempts_and_completion_rejected(data, change):
    p = data["predictions"][0]
    a = p["attempts"][0]
    if change == "duplicate_input":
        data["run"]["inputs"].append(deepcopy(data["run"]["inputs"][0]))
    elif change == "duplicate_prediction":
        data["predictions"].append(deepcopy(p))
    elif change == "missing_prediction":
        data["predictions"].pop()
    elif change == "foreign_image":
        p["image_id"] = "img-999999"
    elif change == "foreign_run":
        p["run_id"] = "different-run"
    elif change == "changed_prompt":
        data["run"]["hashes"]["prompt"] = "f" * 64
    elif change == "changed_image":
        data["run"]["inputs"][0]["sha256"] = "f" * 64
    elif change == "changed_schema":
        data["run"]["hashes"]["response_schema"] = "f" * 64
        rebind(data)
    elif change == "wrong_status":
        a["reason"] = "quota"
    elif change == "fake_success":
        a["response"] = None
    elif change == "bad_number":
        a["number"] = 2
    elif change == "backwards_time":
        a["finished_at"] = "2026-10-24T09:59:59Z"
    elif change == "before_creation":
        a["started_at"] = "2026-10-24T09:00:00Z"
    elif change == "missing_raw_hash":
        a["response_sha256"] = None
    elif change == "pending_result":
        p["execution_state"] = "pending"
    elif change == "incomplete_run":
        data["run"]["state"] = "complete"
        p.update(execution_state="pending", status=None, attempts=[])
    elif change == "too_many_attempts":
        p["attempts"] = [deepcopy(a)] * 4
    elif change == "retry_too_soon":
        a.update(status="timeout", reason="timeout", response=None)
        retry = deepcopy(a)
        retry["number"] = 2
        p["status"] = "timeout"
        p["attempts"].append(retry)
    else:
        if change == "refusal_retry":
            a.update(status="refusal", reason="refusal", response=None)
            p["status"] = "refusal"
        elif change == "unknown_retry":
            a.update(status="unknown_outcome", reason="interrupted", response=None,
                     finished_at=None, latency_ms=None, usage=None)
            p["status"] = "unknown_outcome"
        retry = deepcopy(a)
        retry.update(number=2, started_at="2026-10-24T10:00:10Z", finished_at="2026-10-24T10:00:11Z")
        p["attempts"].append(retry)
    with pytest.raises(ValidationError):
        ApiEvidence.model_validate(data)


def test_transient_retries_preserve_all_attempts_and_provider_guidance(data):
    p = data["predictions"][0]
    success = p["attempts"][0]
    timeout = deepcopy(success)
    timeout.update(status="timeout", reason="timeout", response=None,
                   retry_not_before="2026-10-24T10:00:05Z")
    success.update(number=2, started_at="2026-10-24T10:00:05Z", finished_at="2026-10-24T10:00:06Z")
    p["attempts"] = [timeout, success]
    assert len(ApiEvidence.model_validate(data).root["predictions"][0]["attempts"]) == 2
    success["started_at"] = "2026-10-24T10:00:04Z"
    with pytest.raises(ValidationError, match="guidance"):
        ApiEvidence.model_validate(data)


def test_quota_pause_cannot_be_completed_or_treated_as_prediction(data):
    p = data["predictions"][-1]
    a = p["attempts"][0]
    a.update(status="provider_error", reason="quota", response=None,
             retry_not_before="2026-10-25T00:00:00Z")
    p.update(execution_state="quota_paused", status=None)
    data["run"]["state"] = "paused"
    ApiEvidence.model_validate(data)
    assert next_action(a) == "pause_for_quota"
    data["run"]["state"] = "complete"
    with pytest.raises(ValidationError):
        ApiEvidence.model_validate(data)
    data["run"]["state"] = "paused"
    a["retry_not_before"] = None
    with pytest.raises(ValidationError):
        ApiEvidence.model_validate(data)


@pytest.mark.parametrize("reason", ["authentication", "entitlement"])
def test_provider_access_errors_require_stop(data, reason):
    p = data["predictions"][-1]
    a = p["attempts"][0]
    a.update(status="provider_error", reason=reason, response=None)
    p["status"] = "provider_error"
    assert next_action(a) == "stop_provider"
    with pytest.raises(ValidationError, match="stopped"):
        ApiEvidence.model_validate(data)
    data["run"]["state"] = "stopped"
    ApiEvidence.model_validate(data)


def test_serial_records_cannot_advance_after_access_failure_or_overlap(data):
    a = data["predictions"][0]["attempts"][0]
    a.update(status="provider_error", reason="authentication", response=None)
    data["predictions"][0]["status"] = "provider_error"
    data["run"]["state"] = "stopped"
    with pytest.raises(ValidationError, match="continued"):
        ApiEvidence.model_validate(data)
    a.update(status="success", reason="none", response={"decision": "uncertain", "observation": "TEST ONLY"},
             finished_at="2026-10-24T10:01:01Z")
    data["predictions"][0]["status"] = "success"
    with pytest.raises(ValidationError, match="overlaps"):
        ApiEvidence.model_validate(data)


def test_interrupted_submission_is_distinct_and_cannot_claim_a_response(data):
    p = data["predictions"][-1]
    a = p["attempts"][0]
    a.update(status="unknown_outcome", reason="interrupted", response=None,
             finished_at=None, latency_ms=None, usage=None)
    p["status"] = "unknown_outcome"
    ApiEvidence.model_validate(data)
    assert next_action(a) == "reconcile_unknown"
    a["finished_at"] = "2026-10-24T10:05:01Z"
    with pytest.raises(ValidationError, match="Interrupted"):
        ApiEvidence.model_validate(data)


def test_saved_observations_reject_obvious_private_markers(data):
    data["predictions"][0]["attempts"][0]["response"]["observation"] = "Authorization: TEST-ONLY"
    with pytest.raises(ValidationError, match="unsanitized"):
        ApiEvidence.model_validate(data)


@pytest.mark.parametrize("status,reason,number,expected", [
    ("success", "none", 1, "terminal"), ("refusal", "refusal", 1, "terminal"),
    ("invalid_response", "schema", 1, "terminal"),
    ("timeout", "timeout", 1, "retry_with_backoff"),
    ("provider_error", "transport", 2, "retry_with_backoff"),
    ("provider_error", "server_5xx", 3, "terminal"),
    ("provider_error", "other_provider", 1, "terminal"),
    ("unknown_outcome", "interrupted", 1, "reconcile_unknown"),
])
def test_offline_retry_policy(data, status, reason, number, expected):
    a = data["predictions"][0]["attempts"][0]
    a.update(status=status, reason=reason, number=number)
    assert next_action(a) == expected


def test_sanitized_records_do_not_copy_raw_errors_or_known_secrets():
    raw = json.dumps({"decision": "uncertain", "observation":
        "TEST ONLY: fake-value C:/Users/example/private.png /home/example/file API_KEY=made-up"})
    result = sanitized_result(status="success", reason="none", raw_response=raw,
                              sensitive_values=("fake-value",))
    encoded = json.dumps(result)
    for private in ("fake-value", "Users/example", "home/example", "made-up"):
        assert private not in encoded
    assert "redacted" in encoded
    error = sanitized_result(status="provider_error", reason="authentication", raw_response="TEST-ONLY-Authorization: Bearer FAKE")
    assert error["response"] is None
    assert "FAKE" not in json.dumps(error)


@pytest.fixture
def access():
    return {"provider": "gemini", "model_id": "synthetic-model", "evidence_sha256": "e" * 64,
            "verified_at": "2026-10-24T00:00:00Z", "valid_until": "2026-10-25T00:00:00Z",
            "free_execution_verified": True, "paid_execution_disabled": True,
            "terms_and_data_use_verified": True, "requests_per_minute": 10,
            "input_tokens_per_minute": 1000, "requests_per_day": 20,
            "remaining_requests_today": 12}


def preflight(access, **changes):
    args = {"model_id": "synthetic-model", "now": datetime(2026, 10, 24, 10, tzinfo=timezone.utc),
            "request_budget": 3, "input_token_budget": 500}
    args.update(changes)
    return check_access(access, **args)


def test_preflight_requires_verified_free_access_and_leaves_quota_headroom(access):
    assert preflight(access) == {"concurrency": 1, "minimum_interval_seconds": 12,
                                 "request_timeout_seconds": 60, "max_attempts_per_image": 3}
    with pytest.raises(ValueError):
        preflight(None)


@pytest.mark.parametrize("field,value", [
    ("provider", "openai"), ("model_id", "different-model"),
    ("evidence_sha256", None), ("free_execution_verified", False),
    ("paid_execution_disabled", False), ("terms_and_data_use_verified", False),
    ("requests_per_minute", 0), ("input_tokens_per_minute", None),
    ("requests_per_day", 0), ("remaining_requests_today", 0),
    ("remaining_requests_today", 21),
    ("valid_until", "2026-10-24T09:00:00Z"),
    ("verified_at", "2026-10-24T11:00:00Z"),
])
def test_preflight_refuses_missing_stale_wrong_or_paid_evidence(access, field, value):
    access[field] = value
    with pytest.raises(ValueError):
        preflight(access)


@pytest.mark.parametrize("changes", [
    {"request_budget": 12}, {"request_budget": 0}, {"request_budget": True},
    {"input_token_budget": 1000}, {"input_token_budget": -1},
    {"now": datetime(2026, 10, 24)},
])
def test_preflight_refuses_unbounded_or_quota_consuming_trial(access, changes):
    with pytest.raises(ValueError):
        preflight(access, **changes)


def test_strict_reader_and_cli_never_echo_private_data(tmp_path, capsys):
    for text in ('{"schema_version":1,"schema_version":1}', '{"a":NaN}',
                 '{"a":1e999}', '{"private":"C:/Users/PRIVATE Authorization: FAKE"}'):
        path = tmp_path / "bad.json"
        path.write_text(text, encoding="utf-8")
        assert main([str(path)]) == 1
        output = capsys.readouterr().out
        assert "PRIVATE" not in output and "FAKE" not in output and str(tmp_path) not in output
    assert main([str(FIXTURE)]) == 0
    assert "fixture" in capsys.readouterr().out


def test_fingerprints_are_stable_and_bound_to_request_configuration(data):
    assert fingerprint({"b": 1, "a": 2}) == fingerprint({"a": 2, "b": 1})
    run = data["run"]
    image = run["inputs"][0]
    original = request_fingerprint(run, image)
    run["state"] = "stopped"
    assert request_fingerprint(run, image) == original
    run["model_id"] = "different-model"
    assert request_fingerprint(run, image) != original
