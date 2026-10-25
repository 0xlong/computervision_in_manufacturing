"""Read-only model metadata check using the user-named root .env key.

Never generates content, verifies billing/quota, prints the key, or copies .env.
This narrow loader is not a shell or general dotenv interpreter.
"""

import argparse
import json
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from pipeline.api_contracts import strict_json


ROOT = Path(__file__).resolve().parents[1]
MODELS = ("gemini-3.8-flash", "gemini-3.5-flash-lite")
COMPARISON_MODELS = ("gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3-flash-preview")
HOST = "https://generativelanguage.googleapis.com/v1beta/models/"
MAX_BYTES = 64 * 1024


def load_key(path: Path) -> str:
    """Consume only gemini_api_key/GEMINI_API_KEY; never evaluate other entries."""
    if path.is_symlink() or path.is_junction():
        raise ValueError("Credential file must be a regular local file")
    found = []
    with path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            match = re.match(r"^\s*(?:export\s+)?(?:gemini_api_key|GEMINI_API_KEY)\s*=(.*)$", line)
            if not match:
                continue
            value = match[1].strip()
            if value.startswith(('"', "'")):
                quote = value[0]
                end = value.find(quote, 1)
                if end < 0 or (value[end + 1:].strip() and not value[end + 1:].lstrip().startswith("#")):
                    raise ValueError("Invalid Gemini key assignment")
                value = value[1:end]
            else:
                value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
            # Do not expand shell expressions, environment references or escapes.
            # Treat keys as opaque header values; do not assume a provider key
            # alphabet. Reject whitespace/control characters and shell syntax.
            if not re.fullmatch(r"[\x21-\x7e]{1,4096}", value) or re.search(r"\$[({]|[`\\]", value):
                raise ValueError("Gemini key must be a nonempty literal value")
            found.append(value)
    if len(found) != 1:
        raise ValueError("Configure exactly one Gemini key assignment")
    return found[0]


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Do not allow authentication headers to follow an unexpected redirect.
        return None


def inspect_model(key: str, model: str, opener=None) -> dict:
    if model not in MODELS + COMPARISON_MODELS:
        raise ValueError("Only declared inspection candidates may be inspected")
    result = {"model_id": model, "status": "unavailable", "http_status": None,
              "supports_generate_content": None}
    # Explicit TLS defaults; no inherited proxy or alternate provider endpoint.
    opener = opener or build_opener(ProxyHandler({}), _NoRedirect())
    request = Request(HOST + model, method="GET", headers={"x-goog-api-key": key})
    try:
        with opener.open(request, timeout=15) as response:
            result["http_status"] = response.status
            if response.status != 200:
                return result
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            result["status"] = "invalid_metadata"
            return result
        metadata = strict_json(raw.decode("utf-8"))
        if not isinstance(metadata, dict) or metadata.get("name") != "models/" + model:
            result["status"] = "invalid_metadata"
            return result
        methods = metadata.get("supportedGenerationMethods")
        if not isinstance(methods, list) or any(not isinstance(m, str) for m in methods):
            result["status"] = "invalid_metadata"
            return result
        result.update(status="metadata_available", supports_generate_content="generateContent" in methods)
    except HTTPError as error:
        # Do not read, print or persist the response body, URL or headers.
        result["http_status"] = error.code
        result["status"] = "authentication_or_permission_error" if error.code in (401, 403) else "http_error"
        error.close()
    except ValueError:
        result["status"] = "invalid_metadata"
    except Exception:
        # Library errors may carry request headers/private paths. Never echo them.
        result["status"] = "connection_or_metadata_error"
    return result


def probe(key: str, opener=None) -> list[dict]:
    results = []
    for model in MODELS:
        result = inspect_model(key, model, opener)
        results.append(result)
        # No retries, fallback or further requests following access/quota errors.
        if result["http_status"] in (401, 403, 429) or result["status"] == "connection_or_metadata_error":
            break
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check root Gemini key locally; optional read-only metadata GETs.")
    parser.add_argument("--metadata", action="store_true", help="Read metadata for at most two candidates; no generation or uploads")
    args = parser.parse_args(argv)
    try:
        key = load_key(ROOT / ".env")
    except ValueError:
        print("FAIL local key configuration: the named assignment is missing, repeated or not a nonempty literal value.")
        return 1
    except Exception:
        print("FAIL local key configuration: configure one nonempty gemini_api_key in the root .env.")
        return 1
    print("PASS local Gemini key configuration; value hidden.")
    if args.metadata:
        results = probe(key)
        for result in results:
            print(json.dumps(result, sort_keys=True))
        passed = len(results) == len(MODELS) and all(r["status"] == "metadata_available" and r["supports_generate_content"] for r in results)
    else:
        passed = True
    print("Free tier, remaining quota, applicable use and inference remain UNVERIFIED. No image or generation request sent.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
