"""Frozen complete fastener evaluation in small, serial Free-tier batches."""

from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import argparse
import time

from pipeline.api_contracts import ApiEvidence, check_access, fingerprint, next_action, read_evidence, request_fingerprint
from pipeline.model_inputs import read_inputs
from pipeline.run_gemini_trial import (ROOT, atomic_json, build_payload, digest, implementation_hashes,
    read_json, run_lock, save, stamp, supervised_request, utc_now)
from pipeline.gemini_transport import outcome


CONFIG = {"max_requests_per_model": 345, "reserved_input_tokens_per_request": 16000,
          "max_output_tokens": 2048, "minimum_interval_seconds": 10, "thinking_level": "low"}


def prepare(package: Path, trial: dict, trial_plan: dict, *, now=utc_now):
    """Qualification reads successful normal-fitting probes, never test labels."""
    trial = ApiEvidence.model_validate(trial).root
    tr = trial["run"]
    if tr["model_id"] != "gemini-3.5-flash-lite" or tr["state"] != "complete" or len(trial["predictions"]) != 2:
        raise ValueError("Requires the qualifying Flash-Lite normal-only trial")
    if any(p["status"] != "success" or p["attempts"][-1]["reported_model_version"] is None
           for p in trial["predictions"]):
        raise ValueError("Qualification requires structured sample responses and versions")
    summary = read_json(package / "preparation.json")
    fitting_path = package / "model-inputs/fitting.json"
    fitting = read_inputs(fitting_path)
    evaluation_path = package / "model-inputs/evaluation.json"
    evaluation = read_inputs(evaluation_path)
    if any(summary["indexes"][s]["sha256"] != digest(package / f"model-inputs/{s}.json") for s in ("fitting", "evaluation")):
        raise ValueError("Prepared input indexes changed")
    fitting_ids = {i["image_id"]: i["sha256"] for i in fitting["images"]}
    if any(fitting_ids.get(i["image_id"]) != i["sha256"] for i in tr["inputs"]):
        raise ValueError("Qualification probes must be unchanged fitting images")
    if tr["hashes"]["inputs"] != digest(fitting_path) or tr["hashes"]["manifest"] != summary["manifest_sha256"]:
        raise ValueError("Trial/preparation identity mismatch")
    if len(evaluation["images"]) != 115 or set(fitting_ids) & {i["image_id"] for i in evaluation["images"]}:
        raise ValueError("Expected unchanged complete 115-image fastener test set")
    if any(max(i["dimensions"].values()) > 700 or (evaluation_path.parent / i["path"]).stat().st_size > 1024 * 1024 for i in evaluation["images"]):
        raise ValueError("Evaluation image exceeds frozen request bounds")
    if fingerprint(trial_plan) != tr["hashes"]["configuration"] or trial_plan["model_id"] != tr["model_id"] or trial_plan["reference"]["image_id"] in {i["image_id"] for i in tr["inputs"]}:
        raise ValueError("Trial plan identity mismatch")
    config = {**trial_plan["configuration"], **CONFIG}
    reference = trial_plan["reference"]
    if fitting_ids.get(reference["image_id"]) != reference["sha256"]:
        raise ValueError("Reference must remain in normal fitting inputs")
    implementation = {**implementation_hashes(), "evaluation_supervisor": sha256(Path(__file__).read_text(encoding="utf-8").encode()).hexdigest()}
    identity = {"purpose": "complete_fastener_evaluation", "configuration": config,
                "model_id": tr["model_id"], "reference": reference,
                "probes": evaluation["images"], "qualification_sha256": fingerprint(trial),
                "preparation_sha256": digest(package / "preparation.json"),
                "inputs_sha256": digest(evaluation_path), "implementation": implementation}
    identity_hash = fingerprint(identity)
    plan = {**identity, "frozen_at": stamp(now()), "run_id": f"eval-flash-lite-{identity_hash[:16]}"}
    run = {**deepcopy(tr), "run_id": plan["run_id"], "created_at": plan["frozen_at"], "state": "in_progress",
           "hashes": {**tr["hashes"], "inputs": digest(evaluation_path), "configuration": identity_hash,
                      "references": fingerprint([reference]), "preparation": identity["preparation_sha256"]},
           "inputs": [{"image_id": i["image_id"], "sha256": i["sha256"]} for i in evaluation["images"]]}
    evidence = {"schema_version": 1, "evidence_status": trial["evidence_status"], "run": run,
                "predictions": [{"run_id": run["run_id"], "image_id": i["image_id"],
                    "request_sha256": request_fingerprint(run, i), "execution_state": "pending", "status": None,
                    "attempts": []} for i in run["inputs"]]}
    ApiEvidence.model_validate(evidence)
    return plan, evidence


def execute_batch(plan, evidence, root, output, access, *, budget=12, send=supervised_request,
                  now=utc_now, monotonic=time.monotonic, sleep=time.sleep):
    """At most 12 submissions per invocation; attempts persist across batches."""
    if type(budget) is not int or not 1 <= budget <= 12:
        raise ValueError("Batch budget must be 1–12 requests")
    ApiEvidence.model_validate(evidence)
    run = evidence["run"]
    if run["state"] in {"complete", "stopped"}: return evidence
    config = plan["configuration"]
    count, started = 0, monotonic()
    def preflight():
        current = deepcopy(access)
        # Count all submissions after this snapshot, without assuming a reset.
        verified = datetime.fromisoformat(access["verified_at"].replace("Z", "+00:00"))
        current["remaining_requests_today"] -= sum(datetime.fromisoformat(a["started_at"].replace("Z", "+00:00")) >= verified
            for p in evidence["predictions"] for a in p["attempts"])
        return check_access(current, model_id=run["model_id"], now=now(),
                            request_budget=budget, input_token_budget=budget * 16000)
    interval = max(10, preflight()["minimum_interval_seconds"])
    for prediction, probe in zip(evidence["predictions"], plan["probes"], strict=True):
        while True:
            attempts = prediction["attempts"]
            if any(a["status"] == "unknown_outcome" for p in evidence["predictions"] for a in p["attempts"]):
                run["state"] = "stopped"; save(output, evidence); return evidence
            if attempts and next_action(attempts[-1]) in {"terminal", "stop_provider"}: break
            all_attempts = [a for p in evidence["predictions"] for a in p["attempts"]]
            if count >= budget or len(all_attempts) >= config["max_requests_per_model"] or monotonic() - started > 900:
                run["state"] = "paused"; save(output, evidence); return evidence
            earliest = now().timestamp()
            if all_attempts:
                last = max(all_attempts, key=lambda a: a["started_at"])
                earliest = max(earliest, datetime.fromisoformat(last["started_at"].replace("Z", "+00:00")).timestamp() + interval)
                if last["retry_not_before"]:
                    earliest = max(earliest, datetime.fromisoformat(last["retry_not_before"].replace("Z", "+00:00")).timestamp())
            if attempts:
                earliest = max(earliest, datetime.fromisoformat(attempts[-1]["finished_at"].replace("Z", "+00:00")).timestamp() + 2 ** (len(attempts) - 1))
            if earliest - now().timestamp() > 60 or monotonic() - started + max(0, earliest - now().timestamp()) + 60 > 900:
                run["state"] = "paused"; save(output, evidence); return evidence
            while earliest > now().timestamp(): sleep(min(1, earliest - now().timestamp()))
            preflight()
            payload = build_payload(plan, probe, root)
            attempts.append({"number": len(attempts) + 1, "started_at": stamp(now()), "finished_at": None,
                             "latency_ms": None, **outcome("unknown_outcome", "interrupted")})
            prediction.update(execution_state="terminal", status="unknown_outcome")
            run["state"] = "in_progress"
            save(output, evidence)  # Durable unknown submission before launching a child.
            tick = monotonic()
            result = send(run["model_id"], payload, 60)
            count += 1
            if result["status"] == "unknown_outcome":
                run["state"] = "stopped"; save(output, evidence); return evidence
            attempts[-1].update(result, finished_at=stamp(now()), latency_ms=min(60000, max(0, (monotonic() - tick) * 1000)))
            action = next_action(attempts[-1])
            prediction.update(execution_state="quota_paused" if action == "pause_for_quota" else "terminal",
                              status=None if action == "pause_for_quota" else result["status"])
            run["state"] = "paused" if action == "pause_for_quota" else "stopped" if action == "stop_provider" else "in_progress"
            if result["status"] == "success" and (result["usage"] is None or result["usage"]["input_tokens"] is None or result["usage"]["input_tokens"] > 16000):
                run["state"] = "stopped"
            save(output, evidence)
            if run["state"] in {"paused", "stopped"}: return evidence
    run["state"] = "complete"; save(output, evidence); return evidence


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--trial", type=Path, required=True)
    parser.add_argument("--access", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    try:
        trial = read_evidence(args.trial).root
        trial_plan = read_json(args.trial.parent / "plan.json")
        plan, fresh = prepare(args.package, trial, trial_plan)
        output = ROOT / "artifacts/gemini-evaluations" / plan["run_id"]
        output.mkdir(parents=True, exist_ok=True)
        with run_lock(output):
            if (output / "plan.json").exists():
                old_plan = read_json(output / "plan.json")
                if {k: v for k, v in plan.items() if k != "frozen_at"} != {k: v for k, v in old_plan.items() if k != "frozen_at"}:
                    raise ValueError("Frozen plan changed")
                plan = old_plan
                evidence = read_evidence(output / "evidence.json").root
                if {k: v for k, v in evidence["run"].items() if k not in {"created_at", "state"}} != {k: v for k, v in fresh["run"].items() if k not in {"created_at", "state"}}:
                    raise ValueError("Saved run differs from frozen plan")
            else:
                if (output / "evidence.json").exists(): raise ValueError("Incomplete output folder")
                atomic_json(output / "plan.json", plan); save(output, fresh); evidence = fresh
            if args.execute:
                if trial["evidence_status"] == "fixture": raise ValueError("Cannot execute fixture qualification")
                access = read_json(args.access)
                atomic_json(output / "access.json", access)
                with run_lock(ROOT / "artifacts/gemini-trials"):
                    evidence = execute_batch(plan, evidence, args.package / "model-inputs", output, access)
        done = sum(p["execution_state"] == "terminal" for p in evidence["predictions"])
        print(f"PASS evaluation {'batch' if args.execute else 'offline plan'}: {done}/115 terminal; state={evidence['run']['state']}")
        return 0
    except (OSError, ValueError, KeyError, TypeError):
        print("FAIL evaluation runner: check frozen inputs, trial, access freshness/allowance and saved run")
        return 1


if __name__ == "__main__": raise SystemExit(main())
