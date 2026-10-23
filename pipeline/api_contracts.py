"""Saved API evidence and pure preflight checks. No provider/network execution.

JSON Schema owns field definitions; Python checks cross-record relationships.
Hashes identify bytes/configuration, not authenticity or permission to upload.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timedelta
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import JsonValue, RootModel, model_validator

from pipeline.contracts import _reject_constant, _unique_keys


SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "schemas/api-evidence.v1.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)


def _validator(definition: str | None = None) -> Draft202012Validator:
    schema = SCHEMA if definition is None else {
        "$ref": f"#/$defs/{definition}", "$defs": SCHEMA["$defs"]
    }
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _check(data: Any, definition: str | None = None) -> None:
    try:
        json.dumps(data, allow_nan=False)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("API contract requires finite JSON values") from None
    if next(_validator(definition).iter_errors(data), None) is not None:
        # No untrusted keys, provider text, paths, or input values in errors.
        raise ValueError("API contract violation; check the supported schema and fields")


def strict_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=_unique_keys, parse_constant=_reject_constant)


def fingerprint(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                             allow_nan=False).encode("utf-8")).hexdigest()


RESPONSE_SCHEMA_SHA256 = fingerprint(SCHEMA["$defs"]["response"])


def request_fingerprint(run: dict, image: dict) -> str:
    """Bind an image to the complete immutable request configuration, not run state."""
    return fingerprint({key: run[key] for key in (
        "run_id", "track_id", "provider", "model_id", "hashes",
        "request_timeout_seconds", "max_attempts", "policy", "capabilities"
    )} | {"image": image})


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


_STATUS_REASONS = {
    "success": {"none"}, "refusal": {"refusal"}, "invalid_response": {"schema"},
    "timeout": {"timeout"}, "unknown_outcome": {"interrupted"},
    "provider_error": {"transport", "server_5xx", "quota", "authentication", "entitlement", "other_provider"},
}
_TRANSIENT = {"timeout", "transport", "server_5xx"}


def _relationships(data: dict) -> None:
    run = data["run"]
    images = {item["image_id"]: item for item in run["inputs"]}
    predictions = data["predictions"]
    if len(images) != len(run["inputs"]):
        raise ValueError("Duplicate run image identity")
    if len({p["image_id"] for p in predictions}) != len(predictions):
        raise ValueError("Duplicate prediction identity")
    if set(images) != {p["image_id"] for p in predictions}:
        raise ValueError("Every declared image needs exactly one execution record")
    if run["hashes"]["response_schema"] != RESPONSE_SCHEMA_SHA256:
        raise ValueError("Response schema fingerprint mismatch")
    for p in predictions:
        if p["run_id"] != run["run_id"] or p["request_sha256"] != request_fingerprint(run, images[p["image_id"]]):
            raise ValueError("Prediction run/request fingerprint mismatch")
        attempts = p["attempts"]
        for number, a in enumerate(attempts, 1):
            if a["number"] != number or a["reason"] not in _STATUS_REASONS[a["status"]]:
                raise ValueError("Attempt numbering or status/reason mismatch")
            start = _time(a["started_at"])
            if start < _time(run["created_at"]):
                raise ValueError("Attempt precedes run creation")
            if a["status"] == "unknown_outcome":
                if any(a[k] is not None for k in ("finished_at", "latency_ms", "response", "usage")):
                    raise ValueError("Interrupted submission cannot claim a finished response")
            elif a["finished_at"] is None or a["latency_ms"] is None or _time(a["finished_at"]) < start:
                raise ValueError("Finished attempt needs ordered timestamps and latency")
            if (a["response"] is not None) != (a["status"] == "success"):
                raise ValueError("Only successful attempts carry a validated response")
            if a["response"] is not None and _sanitize_observation(a["response"]["observation"]) != a["response"]["observation"]:
                raise ValueError("Response observation contains unsanitized credential/path markers")
            if a["status"] in {"success", "invalid_response", "refusal"} and a["response_sha256"] is None:
                raise ValueError("Received response needs a raw-byte fingerprint")
            if a["retry_not_before"] is not None:
                if a["reason"] not in _TRANSIENT | {"quota"} or a["finished_at"] is None or _time(a["retry_not_before"]) < _time(a["finished_at"]):
                    raise ValueError("Invalid retry guidance")
            if a["reason"] == "quota" and a["retry_not_before"] is None:
                raise ValueError("Quota outcomes require a permitted retry window")
            if number > 1:
                prev = attempts[number - 2]
                if prev["reason"] not in _TRANSIENT | {"quota"}:
                    raise ValueError("Terminal or unknown outcomes cannot be automatically retried")
                minimum = _time(prev["finished_at"]) + timedelta(seconds=2 ** (number - 2))
                if prev["retry_not_before"]:
                    minimum = max(minimum, _time(prev["retry_not_before"]))
                if start < minimum:
                    raise ValueError("Retry violates backoff/provider retry guidance")
        state = p["execution_state"]
        if state == "pending":
            if attempts or p["status"] is not None:
                raise ValueError("Pending image cannot claim an attempt/result")
        elif state == "quota_paused":
            if not attempts or attempts[-1]["reason"] != "quota" or p["status"] is not None or attempts[-1]["retry_not_before"] is None:
                raise ValueError("Quota pause needs retry guidance and no terminal prediction")
        elif not attempts or p["status"] != attempts[-1]["status"] or attempts[-1]["reason"] == "quota":
            raise ValueError("Terminal prediction must match its final nonquota attempt")
    if run["state"] == "complete" and any(p["execution_state"] != "terminal" for p in predictions):
        raise ValueError("Pending/quota-paused images prevent a complete run")
    reasons = {a["reason"] for p in predictions for a in p["attempts"]}
    if reasons & {"authentication", "entitlement"} and run["state"] != "stopped":
        raise ValueError("Authentication/entitlement errors require a stopped run")
    if any(p["execution_state"] == "quota_paused" for p in predictions) and run["state"] not in {"paused", "stopped"}:
        raise ValueError("Quota exhaustion requires a paused run")
    # A saved serial run must not claim concurrent calls or continue after an
    # access error/interrupted submission. This checks records, not execution.
    ordered = sorted((a for p in predictions for a in p["attempts"]), key=lambda a: _time(a["started_at"]))
    for previous, current in zip(ordered, ordered[1:]):
        if previous["reason"] in {"authentication", "entitlement", "interrupted"}:
            raise ValueError("Run continued after a stop/reconciliation condition")
        earliest = _time(previous["finished_at"])
        if previous["reason"] == "quota":
            earliest = max(earliest, _time(previous["retry_not_before"]))
        if _time(current["started_at"]) < earliest:
            raise ValueError("Run overlaps requests or advances before quota recovery")


class ApiEvidence(RootModel[dict[str, JsonValue]]):
    @model_validator(mode="before")
    @classmethod
    def validate_evidence(cls, data: Any) -> Any:
        _check(data)
        _relationships(data)
        return deepcopy(data)


def read_evidence(path: Path) -> ApiEvidence:
    return ApiEvidence.model_validate(strict_json(path.read_text(encoding="utf-8")))


def parse_response(text: str) -> dict:
    """Parse only the declared response object; refuse fences, prose and extra keys."""
    try:
        data = strict_json(text)
        _check(data, "response")
    except (ValueError, TypeError, RecursionError):
        raise ValueError("Invalid structured API response") from None
    return data


def _sanitize_observation(text: str, sensitive_values: tuple[str, ...] = ()) -> str:
    for value in sorted((v for v in sensitive_values if v), key=len, reverse=True):
        text = text.replace(value, "[redacted]")
    text = re.sub(r"(?i)(?:authorization\s*[:=]\s*[^\r\n]+|bearer\s+\S+|(?:api[_ -]?key|token|password)\s*[:=]\s*\S+)", "[redacted]", text)
    text = re.sub(r"(?:[A-Za-z]:[/\\]|\\\\|/(?:home|Users|tmp|var)/)[^\s]+", "[redacted-path]", text)
    return text[:600]


def sanitized_result(*, status: str, reason: str, raw_response: str | None = None,
                     sensitive_values: tuple[str, ...] = ()) -> dict:
    """Allowlisted result fields only; never accept headers or exception messages.

    Raw text is hashed, not retained. Known secret values, common credential
    markers and local paths in the observation are redacted. This is not a
    general-purpose secret detector or public-release approval.
    """
    if status not in _STATUS_REASONS or reason not in _STATUS_REASONS[status]:
        raise ValueError("Unsupported API outcome")
    response = None
    if status == "success":
        try:
            response = parse_response(raw_response)
        except (ValueError, TypeError):
            status, reason = "invalid_response", "schema"
        if response is not None:
            response["observation"] = _sanitize_observation(response["observation"], sensitive_values)
    return {"status": status, "reason": reason, "response": response,
            "response_sha256": sha256(raw_response.encode("utf-8")).hexdigest() if raw_response is not None else None}


def check_access(access: dict | None, *, model_id: str, now: datetime,
                 request_budget: int, input_token_budget: int) -> dict:
    """Pure eligibility/budget preflight; does not reserve quota or send requests.

    Evidence must be obtained from the approved interface, never inferred from
    this function accepting a dictionary. A later serial runner must enforce
    these limits, concurrency, elapsed time, usage and durable persistence.
    """
    _check(access, "access")
    if now.tzinfo is None or now.utcoffset() != timedelta(0):
        raise ValueError("Preflight requires current UTC time")
    if access["model_id"] != model_id or not (_time(access["verified_at"]) <= now < _time(access["valid_until"])):
        raise ValueError("Access evidence is stale or for another model")
    if any(type(n) is not int or n <= 0 for n in (request_budget, input_token_budget)):
        raise ValueError("Positive bounded request/token budgets required")
    if access["remaining_requests_today"] > access["requests_per_day"]:
        raise ValueError("Remaining allowance exceeds verified daily quota")
    # Leave headroom rather than using the published/project limit itself.
    request_cap = min(access["remaining_requests_today"], access["requests_per_day"])
    if request_budget >= request_cap or input_token_budget >= access["input_tokens_per_minute"]:
        raise ValueError("Trial budget must remain below verified available quotas")
    return {"concurrency": 1, "minimum_interval_seconds": 120 / access["requests_per_minute"],
            "request_timeout_seconds": 60, "max_attempts_per_image": 3}


def next_action(attempt: dict) -> str:
    """Offline policy decision, not execution or sleep. Retry still needs preflight."""
    _check(attempt, "attempt")
    if attempt["reason"] not in _STATUS_REASONS[attempt["status"]]:
        raise ValueError("Attempt status/reason mismatch")
    if attempt["reason"] in {"authentication", "entitlement"}:
        return "stop_provider"
    if attempt["reason"] == "quota":
        return "pause_for_quota"
    if attempt["status"] == "unknown_outcome":
        return "reconcile_unknown"
    if attempt["reason"] in _TRANSIENT and attempt["number"] < 3:
        return "retry_with_backoff"
    return "terminal"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check saved API evidence offline; no provider calls.")
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args(argv)
    try:
        evidence = read_evidence(args.evidence).root
    except (OSError, ValueError, RecursionError):
        print("FAIL API evidence: check UTF-8 JSON, schema version, identities and attempt consistency.")
        return 1
    print(f"PASS API evidence contract ({evidence['evidence_status']}): {len(evidence['predictions'])} image records")
    print("Offline structure only: authenticity, access, input bytes, frontend agreement and AI quality NOT verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
