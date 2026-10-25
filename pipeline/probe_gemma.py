"""Small hosted Gemma feasibility trial, isolated from frozen Gemini campaigns.

Uses the same normal-fitting pixels/prompt/response schema. Never benchmarks test
images. No requests without --execute plus a current nonsecret access record.
"""

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

from pipeline import run_gemini_trial as common
from pipeline.api_contracts import ApiEvidence, check_access, fingerprint, read_evidence, request_fingerprint, strict_json
from pipeline.check_gemini_metadata import HOST, _NoRedirect, load_key
from pipeline.gemini_transport import outcome, parse_envelope, retry_time
from pipeline.run_gemini_comparison import open_run

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("gemma-4-26b-a4b-it", "gemma-4-31b-it")
CONFIG = ROOT / "configs/gemma-trial.v1.json"
SCHEMA = common.read_json(ROOT / "schemas/gemma-trial.v1.schema.json")


def prepare(package, model, *, now=None):
    plan, evidence = common.prepare(package, common.read_json(CONFIG), model, schema=SCHEMA, now=now)
    plan["gemma_probe_sha256"] = common.sha256(Path(__file__).read_text(encoding="utf-8").encode()).hexdigest()
    identity = fingerprint(plan)
    run = evidence["run"]
    run["run_id"] = f"probe-{model}-{identity[:12]}"
    run["hashes"]["configuration"] = identity
    for p, item in zip(evidence["predictions"], run["inputs"], strict=True):
        p.update(run_id=run["run_id"], request_sha256=request_fingerprint(run, item))
    ApiEvidence.model_validate(evidence)
    return plan, evidence


def send_once(model, body, key, opener=None):
    """Small isolated allowlist: do not alter the frozen Gemini transport source."""
    if model not in MODELS: raise ValueError("Unsupported hosted Gemma candidate")
    opener = opener or build_opener(ProxyHandler({}), _NoRedirect())
    request = Request(HOST + model + ":generateContent", data=body, method="POST",
                      headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    try:
        with opener.open(request, timeout=55) as response:
            raw = response.read(65537)
            if len(raw) > 65536: return outcome("provider_error", "other_provider")
            return parse_envelope(raw, key) if response.status == 200 else outcome("provider_error", "other_provider", raw)
    except HTTPError as error:
        try:
            raw = error.read(65537)
            reason = ("authentication" if error.code == 401 else "entitlement" if error.code == 403
                      else "quota" if error.code == 429 else "server_5xx" if 500 <= error.code <= 599 else "other_provider")
            result = outcome("provider_error", reason, raw if len(raw) <= 65536 else None)
            if reason in {"quota", "server_5xx"}:
                result["retry_not_before"] = retry_time(raw, error.headers.get("Retry-After"), common.utc_now(), quota=reason == "quota")
            return result
        finally: error.close()
    except (TimeoutError, socket.timeout): return outcome("timeout", "timeout")
    except URLError as error:
        return outcome("timeout", "timeout") if isinstance(error.reason, TimeoutError) else outcome("provider_error", "transport")


def send(model, payload, timeout=60):
    try:
        child = subprocess.run([sys.executable, "-m", "pipeline.probe_gemma", "--request-child"],
            input=json.dumps({"model": model, "payload": payload}, allow_nan=False).encode(),
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=timeout, cwd=ROOT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        if child.returncode or len(child.stdout) > 8192: return outcome("unknown_outcome", "interrupted")
        return strict_json(child.stdout.decode("utf-8"))
    except subprocess.TimeoutExpired: return outcome("timeout", "timeout")
    except (OSError, ValueError, UnicodeError): return outcome("unknown_outcome", "interrupted")


def request_child():
    try:
        data = strict_json(sys.stdin.buffer.read(4 * 1024 * 1024).decode("utf-8"))
        key = load_key(ROOT / ".env")  # Previously authorized single named assignment; never printed.
        result = send_once(data["model"], json.dumps(data["payload"], allow_nan=False).encode(), key)
    except Exception: result = outcome("provider_error", "other_provider")
    print(json.dumps(result, allow_nan=False))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--access", type=Path)
    args = parser.parse_args(argv)
    try:
        plan, fresh = prepare(args.package, args.model)
        access = common.read_json(args.access) if args.execute and args.access else None
        if args.execute:
            check_access(access, model_id=args.model, now=common.utc_now(), request_budget=3, input_token_budget=12288)
        directory = ROOT / "artifacts/gemma-probes"
        output = directory / fresh["run"]["run_id"]
        if directory.is_symlink() or directory.is_junction() or output.is_symlink() or output.is_junction():
            raise ValueError("Output must be local regular directories")
        output.mkdir(parents=True, exist_ok=True)
        with common.run_lock(output):
            plan, evidence = open_run(output, plan, fresh)
            if args.execute and evidence["run"]["state"] not in {"complete", "stopped"}:
                lock = ROOT / "artifacts/gemini-trials"; lock.mkdir(parents=True, exist_ok=True)
                common.atomic_json(output / "access.json", access)
                with common.run_lock(lock):
                    evidence = common.execute(plan, evidence, args.package / "model-inputs", output, access, send=send)
        successes = sum(p["status"] == "success" for p in evidence["predictions"])
        calls = sum(len(p["attempts"]) for p in evidence["predictions"])
        print(f"PASS Gemma feasibility: {successes}/2 successful structured answers; {calls} submissions; "
              f"state={evidence['run']['state']}; run={evidence['run']['run_id']}")
        print("Normal-fitting trial only; not a complete defect evaluation. Existing runs and website unchanged.")
        return 0
    except (ValueError, OSError, KeyError, TypeError, RecursionError):
        print("FAIL Gemma probe: check configuration/input integrity, current access and saved snapshot. No raw errors displayed.")
        return 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--request-child"]: request_child()
    else: raise SystemExit(main())
