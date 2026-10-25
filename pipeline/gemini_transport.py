"""Fixed-host Gemini transport. The runner supervises this child with a deadline.

Only this child consumes the configured key. Raw provider text, headers, errors,
and the key never leave the process. No SDK, redirects, proxy or fallback.
"""

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
import json
import re
import socket
import sys
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

from pipeline.api_contracts import sanitized_result, strict_json
from pipeline.check_gemini_metadata import HOST, MODELS, COMPARISON_MODELS, ROOT, _NoRedirect, load_key


MAX_RESPONSE_BYTES = 64 * 1024


def utc_now():
    return datetime.now(timezone.utc)


def stamp(value):
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def outcome(status, reason, raw=None):
    result = sanitized_result(status=status, reason=reason)
    result.update(reported_model_version=None, usage=None, retry_not_before=None)
    if raw is not None:
        result["response_sha256"] = sha256(raw).hexdigest()
    return result


def parse_envelope(raw: bytes, key: str) -> dict:
    """Classify real provider envelopes; never confuse truncation with refusal."""
    result = outcome("invalid_response", "schema", raw)
    try:
        data = strict_json(raw.decode("utf-8"))
        if not isinstance(data, dict):
            return result
        version = data.get("modelVersion")
        if isinstance(version, str) and re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,99}", version) and key not in version:
            result["reported_model_version"] = version
        usage = data.get("usageMetadata", {})
        fields = [usage.get(k) for k in ("promptTokenCount", "candidatesTokenCount", "thoughtsTokenCount")]
        if all(v is None or (type(v) is int and v >= 0) for v in fields):
            result["usage"] = {"input_tokens": fields[0], "output_tokens":
                               None if fields[1] is None else fields[1] + (fields[2] or 0)}
        blocked = data.get("promptFeedback", {}).get("blockReason")
        candidates = data.get("candidates", [])
        if blocked in {"SAFETY", "OTHER", "BLOCKLIST", "PROHIBITED_CONTENT", "IMAGE_SAFETY"}:
            result.update(status="refusal", reason="refusal")
            return result
        if blocked not in (None, "BLOCK_REASON_UNSPECIFIED"):
            return result
        if len(candidates) != 1:
            return result
        candidate = candidates[0]
        finish = candidate.get("finishReason")
        if finish in {"SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT", "SPII", "IMAGE_SAFETY"}:
            result.update(status="refusal", reason="refusal")
            return result
        if finish != "STOP":
            return result
        parts = candidate["content"]["parts"]
        text_parts = [p["text"] for p in parts if p.get("thought") is not True]
        if not text_parts or any(not isinstance(t, str) for t in text_parts):
            return result
        parsed = sanitized_result(status="success", reason="none", raw_response="".join(text_parts),
                                  sensitive_values=(key,))
        result.update(status=parsed["status"], reason=parsed["reason"], response=parsed["response"])
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError):
        pass
    return result


def retry_time(raw, header, now, *, quota):
    """Honor Retry-After and Google's RetryInfo; absent quota guidance waits a day."""
    delays = []
    if header:
        try:
            delays.append(now + timedelta(seconds=max(0, int(header))))
        except (ValueError, OverflowError):
            try:
                date = parsedate_to_datetime(header)
                if date.tzinfo:
                    delays.append(date.astimezone(timezone.utc))
            except (ValueError, TypeError, OverflowError):
                pass
    try:
        for detail in strict_json(raw.decode("utf-8"))["error"].get("details", []):
            if detail.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":
                delay = detail.get("retryDelay", "")
                if re.fullmatch(r"[0-9]{1,9}(?:\.[0-9]{1,9})?s", delay):
                    delays.append(now + timedelta(seconds=float(delay[:-1])))
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError):
        pass
    if delays:
        return stamp(max(now + timedelta(seconds=1), *delays))
    return stamp(now + timedelta(days=1)) if quota else None


def send_once(model, payload, key, opener=None):
    if model not in MODELS + COMPARISON_MODELS:
        raise ValueError("Unsupported trial model")
    opener = opener or build_opener(ProxyHandler({}), _NoRedirect())
    request = Request(HOST + model + ":generateContent", data=payload,
                      headers={"x-goog-api-key": key, "Content-Type": "application/json"}, method="POST")
    try:
        with opener.open(request, timeout=55) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                # Do not mislabel a captured prefix as a complete-response hash.
                return outcome("provider_error", "other_provider")
            if response.status != 200:
                return outcome("provider_error", "other_provider", raw)
            return parse_envelope(raw, key)
    except HTTPError as error:
        try:
            raw = error.read(MAX_RESPONSE_BYTES + 1)
            reason = ("authentication" if error.code == 401 else "entitlement" if error.code == 403
                      else "quota" if error.code == 429 else "server_5xx" if 500 <= error.code <= 599
                      else "other_provider")
            result = outcome("provider_error", reason, raw if len(raw) <= MAX_RESPONSE_BYTES else None)
            if reason in {"quota", "server_5xx"}:
                result["retry_not_before"] = retry_time(raw, error.headers.get("Retry-After"), utc_now(), quota=reason == "quota")
            return result
        finally:
            error.close()
    except (TimeoutError, socket.timeout):
        return outcome("timeout", "timeout")
    except URLError as error:
        return outcome("timeout", "timeout") if isinstance(error.reason, TimeoutError) else outcome("provider_error", "transport")


def main():
    try:
        # stdin contains image bytes/configuration, never credentials or paths.
        data = strict_json(sys.stdin.buffer.read(4 * 1024 * 1024).decode("utf-8"))
        key = load_key(ROOT / ".env")
        result = send_once(data["model_id"], json.dumps(data["payload"], allow_nan=False).encode("utf-8"), key)
    except Exception:
        # Never print provider exceptions, raw bodies, headers or tracebacks.
        result = outcome("provider_error", "other_provider")
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
