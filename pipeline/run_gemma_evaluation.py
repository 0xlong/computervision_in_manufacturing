"""Frozen Gemma evaluation with a shared rolling input-token budget.

Isolated from the existing frozen Gemini supervisors. Offline unless --execute.
Each invocation sends at most twelve serial requests; successful pictures are reused.
"""

import argparse
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import time

from pipeline import probe_gemma as probe
from pipeline import run_gemini_trial as common
from pipeline import run_gemini_evaluation as existing
from pipeline.run_gemini_comparison import open_run, model_attempts
from pipeline.api_contracts import ApiEvidence, check_access, fingerprint, next_action, read_evidence, request_fingerprint
from pipeline.gemini_transport import outcome

ROOT = Path(__file__).resolve().parents[1]
RESERVE = 4096
TOKEN_WINDOW = 60
MIN_INTERVAL = 10


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def prepare(package, qualifying, qualifying_plan, *, now=common.utc_now):
    model = qualifying["run"]["model_id"]
    expected_plan, expected = probe.prepare(package, model)
    stable = lambda r: {k: v for k, v in r.items() if k not in {"created_at", "state"}}
    if expected_plan != qualifying_plan or stable(qualifying["run"]) != stable(expected["run"]):
        raise ValueError("Requires the unchanged qualifying Gemma trial")
    plan, fresh = existing.prepare(package, qualifying, qualifying_plan, models=probe.MODELS, now=now)
    plan["configuration"].update(reserved_input_tokens_per_request=RESERVE, thinking_level="minimal")
    plan["implementation"]["gemma_evaluation"] = sha256(Path(__file__).read_text(encoding="utf-8").encode()).hexdigest()
    plan["execution_policy"] = {"shared_gemma_allowance": True, "input_window_seconds": TOKEN_WINDOW,
        "input_reservation": RESERVE, "minimum_interval_seconds": MIN_INTERVAL,
        "daily_request_headroom": 1, "automatic_daily_reset": False,
        "submissions_per_batch": 12, "batch_request_wait_seconds": 900}
    identity = fingerprint({k: v for k, v in plan.items() if k not in {"frozen_at", "run_id"}})
    plan["run_id"] = "eval-gemma-" + identity[:16]
    run = fresh["run"]
    run.update(run_id=plan["run_id"])
    run["hashes"]["configuration"] = identity
    for p, item in zip(fresh["predictions"], run["inputs"], strict=True):
        p.update(run_id=run["run_id"], request_sha256=request_fingerprint(run, item))
    ApiEvidence.model_validate(fresh)
    return plan, fresh


def ledger_attempts(roots):
    for directory in roots:
        for model in probe.MODELS:
            yield from model_attempts(directory, model)


def allowance(access, attempts, model, now):
    current = deepcopy(access)
    verified = timestamp(current["verified_at"])
    current["remaining_requests_today"] -= sum(timestamp(a["started_at"]) >= verified for a in attempts)
    return check_access(current, model_id=model, now=now, request_budget=1, input_token_budget=RESERVE)


def earliest_start(attempts, access, now):
    """Reserve the next request before sending; failures/unknowns cost the reserve."""
    earliest = now.timestamp()
    interval = max(MIN_INTERVAL, 120 / access["requests_per_minute"])
    if attempts:
        earliest = max(earliest, max(timestamp(a["started_at"]) for a in attempts) + interval)
    earliest = max([earliest, *(timestamp(a["retry_not_before"]) for a in attempts if a["retry_not_before"])])
    while True:
        active = [a for a in attempts if timestamp(a["started_at"]) + TOKEN_WINDOW >= earliest]
        used = sum(a["usage"]["input_tokens"] if a["status"] == "success" and a["usage"] and a["usage"]["input_tokens"] is not None else RESERVE for a in active)
        if used + RESERVE < access["input_tokens_per_minute"]:
            return earliest
        if not active:
            raise ValueError("Input reservation exceeds allowance")
        earliest = min(timestamp(a["started_at"]) + TOKEN_WINDOW for a in active) + 0.001


def execute_batch(plan, evidence, root, output, access, roots, *, budget=12, send=probe.send,
                  now=common.utc_now, monotonic=time.monotonic, sleep=time.sleep):
    if type(budget) is not int or not 1 <= budget <= 12:
        raise ValueError("Use 1–12 submissions per batch")
    ApiEvidence.model_validate(evidence)
    run = evidence["run"]
    if run["state"] in {"complete", "stopped"}: return evidence
    started, count = monotonic(), 0
    # Caller holds the provider-wide lock: load once, then update this ledger with
    # every journaled attempt. No other provider worker can submit during a batch.
    ledger = list(ledger_attempts(roots))
    for prediction, item in zip(evidence["predictions"], plan["probes"], strict=True):
        while True:
            attempts = prediction["attempts"]
            if attempts and next_action(attempts[-1]) in {"terminal", "stop_provider"}: break
            if any(a["status"] == "unknown_outcome" for a in ledger):
                run["state"] = "stopped"; common.save(output, evidence); return evidence
            if count >= budget or len(attempts) >= 3 or sum(len(p["attempts"]) for p in evidence["predictions"]) >= 345:
                run["state"] = "paused"; common.save(output, evidence); return evidence
            try:
                allowance(access, ledger, run["model_id"], now())
            except ValueError:
                run["state"] = "paused"; common.save(output, evidence); return evidence
            earliest = earliest_start(ledger, access, now())
            if attempts:
                earliest = max(earliest, timestamp(attempts[-1]["finished_at"]) + 2 ** (len(attempts) - 1))
            delay = max(0, earliest - now().timestamp())
            if delay > 60 or monotonic() - started + delay + 60 > 900:
                run["state"] = "paused"; common.save(output, evidence); return evidence
            while earliest > now().timestamp(): sleep(min(1, max(0.001, earliest - now().timestamp())))
            allowance(access, ledger, run["model_id"], now())
            payload = common.build_payload(plan, item, root)
            attempts.append({"number": len(attempts) + 1, "started_at": common.stamp(now()),
                "finished_at": None, "latency_ms": None, **outcome("unknown_outcome", "interrupted")})
            ledger.append(attempts[-1])
            prediction.update(execution_state="terminal", status="unknown_outcome")
            run["state"] = "in_progress"; common.save(output, evidence)
            tick = monotonic()
            result = send(run["model_id"], payload, 60)
            count += 1
            if result["status"] == "unknown_outcome":
                run["state"] = "stopped"; common.save(output, evidence); return evidence
            attempts[-1].update(result, finished_at=common.stamp(now()), latency_ms=min(60000, max(0, (monotonic()-tick)*1000)))
            action = next_action(attempts[-1])
            prediction.update(execution_state="quota_paused" if action == "pause_for_quota" else "terminal",
                              status=None if action == "pause_for_quota" else result["status"])
            run["state"] = "paused" if action == "pause_for_quota" else "stopped" if action == "stop_provider" else "in_progress"
            usage = result["usage"]
            if result["status"] == "success" and (usage is None or usage["input_tokens"] is None or usage["input_tokens"] > RESERVE):
                run["state"] = "stopped"
            common.save(output, evidence)
            if run["state"] in {"paused", "stopped"}: return evidence
    run["state"] = "complete"; common.save(output, evidence); return evidence


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--trial", type=Path, required=True)
    parser.add_argument("--access", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--budget", type=int, choices=range(1, 13), default=12)
    args = parser.parse_args(argv)
    try:
        qualifying = read_evidence(args.trial).root
        if args.execute and qualifying["evidence_status"] == "fixture": raise ValueError("No live fixture runs")
        plan, fresh = prepare(args.package, qualifying, common.read_json(args.trial.parent / "plan.json"))
        roots = (ROOT / "artifacts/gemma-probes", ROOT / "artifacts/gemma-evaluations")
        if any(p.is_symlink() or p.is_junction() for p in roots): raise ValueError("Regular ledger roots required")
        access = common.read_json(args.access) if args.execute and args.access else None
        if args.execute: allowance(access, list(ledger_attempts(roots)), fresh["run"]["model_id"], common.utc_now())
        output = roots[1] / plan["run_id"]
        if output.is_symlink() or output.is_junction(): raise ValueError("Regular output required")
        output.mkdir(parents=True, exist_ok=True)
        with common.run_lock(output):
            plan, evidence = open_run(output, plan, fresh)
            if args.execute:
                common.atomic_json(output / "access.json", access)
                lock = ROOT / "artifacts/gemini-trials"; lock.mkdir(parents=True, exist_ok=True)
                with common.run_lock(lock):
                    evidence = execute_batch(plan, evidence, args.package / "model-inputs", output, access, roots, budget=args.budget)
        done = sum(p["execution_state"] == "terminal" for p in evidence["predictions"])
        print(f"Gemma evaluation: {done}/115 terminal; state={evidence['run']['state']}; run={plan['run_id']}")
        return 0
    except (ValueError, OSError, KeyError, TypeError, RecursionError):
        print("FAIL Gemma evaluation: check frozen trial, inputs, access and ledger; no raw errors displayed.")
        return 1


if __name__ == "__main__": raise SystemExit(main())
