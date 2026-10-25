"""Prepare/resume a bounded Gemini trial. Preparation is offline by default.

Reads only the package summary and checked normal fitting inputs. Evaluation
labels, masks and test indexes are never opened. Live execution additionally
requires current access/use evidence and an explicit --execute flag.
"""

import argparse
import base64
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from jsonschema import Draft202012Validator

from pipeline.api_contracts import (
    ApiEvidence, RESPONSE_SCHEMA_SHA256, SCHEMA, check_access, fingerprint,
    next_action, request_fingerprint, strict_json,
)
from pipeline.gemini_transport import outcome, stamp, utc_now
from pipeline.model_inputs import read_inputs


ROOT = Path(__file__).resolve().parents[1]
TRIAL_SCHEMA = json.loads((ROOT / "schemas/gemini-trial.v1.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(TRIAL_SCHEMA)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def implementation_hashes():
    # Bind request construction/transport code too, independent of Git CRLF rules.
    return {name: sha256(Path(__file__).with_name(name).read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            for name in ("run_gemini_trial.py", "gemini_transport.py")}


def read_json(path):
    return strict_json(path.read_text(encoding="utf-8"))


def atomic_json(path, data):
    """Flush a full snapshot before replacing the previous one."""
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


@contextmanager
def run_lock(directory):
    """OS lock is released on process death; stale lock files are harmless."""
    with (directory / "runner.lock").open("a+b") as stream:
        stream.seek(0)
        if stream.read(1) == b"":
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def prepare(package: Path, configuration: dict, model: str, *, now=None, schema=TRIAL_SCHEMA):
    if not Draft202012Validator(schema).is_valid(configuration):
        raise ValueError("Invalid bounded trial configuration")
    if model not in configuration["model_ids"]:
        raise ValueError("Unsupported trial model")
    summary_path = package / "preparation.json"
    inputs_path = package / "model-inputs/fitting.json"
    for path in (summary_path, inputs_path):
        if path.is_symlink() or path.is_junction() or not path.resolve(strict=True).is_relative_to(package.resolve(strict=True)):
            raise ValueError("Package file escapes its root")
    summary = read_json(summary_path)
    inputs = read_inputs(inputs_path)
    if summary["evidence_status"] != "development_only" or summary["indexes"]["fitting"]["sha256"] != digest(inputs_path):
        raise ValueError("Preparation summary and fitting index disagree")
    ordered = sorted(inputs["images"], key=lambda i: i["image_id"])
    if len(ordered) < 3:
        raise ValueError("Trial needs one reference and two distinct normal probes")
    selected = ordered[:3]
    for item in selected:
        if max(item["dimensions"].values()) > 700 or (inputs_path.parent / item["path"]).stat().st_size > 1024 * 1024:
            raise ValueError("Trial image exceeds the fixed input budget")
    plan = {"configuration": deepcopy(configuration), "model_id": model,
            "reference": selected[0], "probes": selected[1:],
            "fitting_index_sha256": digest(inputs_path), "preparation_sha256": digest(summary_path),
            "implementation_sha256": implementation_hashes()}
    identity = fingerprint(plan)
    run = {"run_id": "trial-" + model + "-" + identity[:12], "track_id": "fasteners",
           "provider": "gemini", "model_id": model, "created_at": stamp(now or utc_now()),
           "state": "in_progress", "hashes": {
               "manifest": summary["manifest_sha256"], "split": fingerprint(summary["indexes"]),
               "inputs": plan["fitting_index_sha256"], "configuration": identity,
               "preparation": plan["preparation_sha256"], "references": fingerprint(selected[:1]),
               "prompt": fingerprint(configuration["prompt"]), "response_schema": RESPONSE_SCHEMA_SHA256},
           "inputs": [{"image_id": i["image_id"], "sha256": i["sha256"]} for i in selected[1:]],
           "capabilities": {"categorical_decision": True, "heatmap": False,
                            "adjustable_sensitivity": False, "calibrated_probability": False},
           "policy": "fixed_categorical_review_uncertain_and_failures",
           "request_timeout_seconds": 60, "max_attempts": 3}
    predictions = [{"run_id": run["run_id"], "image_id": i["image_id"],
                    "request_sha256": request_fingerprint(run, i), "execution_state": "pending",
                    "status": None, "attempts": []} for i in run["inputs"]]
    evidence = {"schema_version": 1, "evidence_status": "development_only", "run": run, "predictions": predictions}
    ApiEvidence.model_validate(evidence)
    return plan, evidence


def image_part(root, item):
    content = (root / item["path"]).read_bytes()
    if sha256(content).hexdigest() != item["sha256"]:
        raise ValueError("Image changed after trial preparation")
    return {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(content).decode("ascii")}}


def build_payload(plan, probe, root):
    configuration = plan["configuration"]
    return {"contents": [{"role": "user", "parts": [
        {"text": configuration["prompt"]}, {"text": "Acceptable reference:"},
        image_part(root, plan["reference"]), {"text": "Candidate " + probe["image_id"] + ":"},
        image_part(root, probe)]}], "generationConfig": {
            "candidateCount": 1, "maxOutputTokens": configuration["max_output_tokens"],
            "thinkingConfig": (configuration["thinking_configs"][plan["model_id"]] if configuration["schema_version"] == 2
                               else {"thinkingLevel": configuration["thinking_level"]}),
            "responseMimeType": "application/json", "responseJsonSchema": SCHEMA["$defs"]["response"]}}


def supervised_request(model, payload, timeout=60):
    """Kill the single request child at the hard overall deadline, including reads."""
    try:
        process = subprocess.run([sys.executable, "-m", "pipeline.gemini_transport"],
                                 input=json.dumps({"model_id": model, "payload": payload}, allow_nan=False).encode("utf-8"),
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=timeout,
                                 cwd=ROOT, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        if process.returncode or len(process.stdout) > 8192:
            return outcome("unknown_outcome", "interrupted")
        return strict_json(process.stdout.decode("utf-8"))
    except subprocess.TimeoutExpired:
        return outcome("timeout", "timeout")
    except (ValueError, OSError, UnicodeError):
        return outcome("unknown_outcome", "interrupted")


def _time(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def save(directory, evidence):
    ApiEvidence.model_validate(evidence)
    atomic_json(directory / "evidence.json", evidence)


def execute(plan, evidence, root, directory, access, *, send=supervised_request,
            now=utc_now, monotonic=time.monotonic, sleep=time.sleep):
    """Serial state machine. All attempts, including unknown ones, consume budget."""
    configuration, run = plan["configuration"], evidence["run"]
    request_budget = configuration["max_requests_per_model"]
    limits = check_access(access, model_id=run["model_id"], now=now(), request_budget=request_budget,
                          input_token_budget=request_budget * configuration["reserved_input_tokens_per_request"])
    ApiEvidence.model_validate(evidence)
    if run["state"] in {"complete", "stopped"}:
        return evidence
    # A crash after the pre-submission snapshot requires explicit reconciliation.
    if any(a["status"] == "unknown_outcome" for p in evidence["predictions"] for a in p["attempts"]):
        run["state"] = "stopped"
        save(directory, evidence)
        return evidence
    started = monotonic()
    interval = max(configuration["minimum_interval_seconds"], limits["minimum_interval_seconds"])
    for prediction, probe in zip(evidence["predictions"], plan["probes"], strict=True):
        while True:
            attempts = prediction["attempts"]
            if attempts and next_action(attempts[-1]) in {"terminal", "stop_provider", "reconcile_unknown"}:
                break
            all_attempts = [a for p in evidence["predictions"] for a in p["attempts"]]
            if len(all_attempts) >= request_budget or len(attempts) >= 3:
                run["state"] = "paused"
                save(directory, evidence)
                return evidence
            earliest = now()
            if all_attempts:
                last = max(all_attempts, key=lambda a: a["started_at"])
                earliest = max(earliest, _time(last["started_at"]) + timedelta(seconds=interval))
                if last["retry_not_before"]:
                    earliest = max(earliest, _time(last["retry_not_before"]))
            if attempts:
                earliest = max(earliest, _time(attempts[-1]["finished_at"]) + timedelta(seconds=2 ** (len(attempts) - 1)))
            delay = max(0, (earliest - now()).total_seconds())
            if monotonic() - started + delay + 60 > configuration["max_runtime_seconds"]:
                run["state"] = "paused"
                save(directory, evidence)
                return evidence
            # Small waits permit interruption; the CLI's request child has its own deadline.
            while delay > 0:
                sleep(min(1, delay))
                delay = max(0, (earliest - now()).total_seconds())
            check_access(access, model_id=run["model_id"], now=now(), request_budget=request_budget,
                         input_token_budget=request_budget * configuration["reserved_input_tokens_per_request"])
            payload = build_payload(plan, probe, root)
            attempt = {"number": len(attempts) + 1, "started_at": stamp(now()),
                       "finished_at": None, "latency_ms": None,
                       **outcome("unknown_outcome", "interrupted")}
            attempts.append(attempt)
            prediction.update(execution_state="terminal", status="unknown_outcome")
            run["state"] = "in_progress"
            save(directory, evidence)  # Must succeed before submission.
            tick = monotonic()
            result = send(run["model_id"], payload, 60)
            if result["status"] == "unknown_outcome":
                run["state"] = "stopped"
                save(directory, evidence)
                return evidence
            attempt.update(result, finished_at=stamp(now()), latency_ms=min(60000, max(0, (monotonic() - tick) * 1000)))
            action = next_action(attempt)
            prediction.update(execution_state="quota_paused" if action == "pause_for_quota" else "terminal",
                              status=None if action == "pause_for_quota" else attempt["status"])
            run["state"] = "paused" if action == "pause_for_quota" else "stopped" if action == "stop_provider" else "in_progress"
            save(directory, evidence)
            # Missing/over-budget input usage stops this trial from advancing.
            usage = attempt["usage"]
            if action in {"pause_for_quota", "stop_provider"}:
                return evidence
            if attempt["status"] == "success" and (usage is None or usage["input_tokens"] is None or
                    usage["input_tokens"] > configuration["reserved_input_tokens_per_request"]):
                run["state"] = "stopped"
                save(directory, evidence)
                return evidence
    run["state"] = "complete"
    save(directory, evidence)
    return evidence


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/gemini-trial.v1.json")
    parser.add_argument("--model", choices=("gemini-3.8-flash", "gemini-3.5-flash-lite"), required=True)
    parser.add_argument("--execute", action="store_true", help="Send images only with current access/use evidence")
    parser.add_argument("--access", type=Path)
    args = parser.parse_args(argv)
    try:
        plan, fresh = prepare(args.package, read_json(args.config), args.model)
        output = ROOT / "artifacts/gemini-trials" / fresh["run"]["run_id"]
        if not output.resolve().is_relative_to((ROOT / "artifacts").resolve()):
            raise ValueError("Run output escapes ignored artifacts")
        # Preflight before any output/key access when execution is requested.
        access = read_json(args.access) if args.execute and args.access else None
        if args.execute:
            check_access(access, model_id=args.model, now=utc_now(),
                         request_budget=plan["configuration"]["max_requests_per_model"],
                         input_token_budget=96000)
        output.mkdir(parents=True, exist_ok=True)
        with run_lock(output):
            if (output / "plan.json").exists():
                if read_json(output / "plan.json") != plan:
                    raise ValueError("Changed request configuration requires a new run folder")
                evidence = ApiEvidence.model_validate(read_json(output / "evidence.json")).root
                if ({k: v for k, v in evidence["run"].items() if k not in {"created_at", "state"}} !=
                        {k: v for k, v in fresh["run"].items() if k not in {"created_at", "state"}}):
                    raise ValueError("Saved evidence does not match the prepared run")
            else:
                if (output / "evidence.json").exists():
                    raise ValueError("Incomplete run folder; use a new output folder")
                atomic_json(output / "plan.json", plan)
                save(output, fresh)
                evidence = fresh
            if args.execute:
                atomic_json(output / "access.json", access)
                # Other trial models/runs also use this provider-wide OS lock.
                with run_lock(output.parent):
                    evidence = execute(plan, evidence, args.package / "model-inputs", output, access)
        successes = sum(p["status"] == "success" for p in evidence["predictions"])
        print(f"PASS trial {'execution' if args.execute else 'offline preparation'}: {len(plan['probes'])} probes; {successes} saved successes; state={evidence['run']['state']}")
        print("Development only. Normal-preparation trial does not measure defect accuracy; website unchanged.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        print("FAIL trial: check configuration, package hashes, access/use evidence and run folder. No raw errors displayed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
