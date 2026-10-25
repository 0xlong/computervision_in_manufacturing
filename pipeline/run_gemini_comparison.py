"""Versioned multi-model preparation/evaluation; offline unless --execute is given.

Uses the existing fixed-host transport, durable submission journal and hard deadline.
New runs have separate identities/directories; the completed Lite baseline is read-only.
"""

import argparse
from copy import deepcopy
from datetime import datetime
from pathlib import Path

from pipeline import run_gemini_trial as trial
from pipeline import run_gemini_evaluation as evaluation
from pipeline.api_contracts import ApiEvidence, check_access, fingerprint, read_evidence, request_fingerprint
from pipeline.check_gemini_metadata import COMPARISON_MODELS

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = trial.read_json(ROOT / "schemas/gemini-trial.v2.schema.json")
CONFIG = ROOT / "configs/gemini-comparison.v2.json"


class AllowancePause(ValueError):
    """A normal pause before submission; never manufacture a failed AI answer."""


def prepare_trial(package, model, *, configuration=None, now=None):
    configuration = trial.read_json(CONFIG) if configuration is None else configuration
    plan, fresh = trial.prepare(package, configuration, model, now=now, schema=SCHEMA)
    plan["comparison_runner_sha256"] = trial.sha256(Path(__file__).read_text(encoding="utf-8").encode()).hexdigest()
    identity = fingerprint(plan)
    run = fresh["run"]
    run["hashes"]["configuration"] = identity
    run["run_id"] = f"trial-comparison-{model}-{identity[:12]}"
    for p in fresh["predictions"]:
        p["run_id"] = run["run_id"]
        p["request_sha256"] = request_fingerprint(run, next(i for i in run["inputs"] if i["image_id"] == p["image_id"]))
    ApiEvidence.model_validate(fresh)
    return plan, fresh


def prepare_evaluation(package, model, qualifying, qualifying_plan, *, now=trial.utc_now):
    expected_plan, expected = prepare_trial(package, model)
    if expected_plan != qualifying_plan:
        raise ValueError("Qualification plan is not the unchanged comparison configuration")
    stable = lambda r: {k: v for k, v in r.items() if k not in {"created_at", "state"}}
    if stable(qualifying["run"]) != stable(expected["run"]):
        raise ValueError("Qualification identity changed")
    plan, fresh = evaluation.prepare(package, qualifying, qualifying_plan, models=COMPARISON_MODELS, now=now)
    return plan, fresh


def model_attempts(directory, model):
    for path in sorted(directory.glob("*/evidence.json")):
        if path.is_symlink() or path.parent.is_symlink() or path.parent.is_junction():
            raise ValueError("Run ledger must contain regular local snapshots")
        evidence = read_evidence(path).root
        if evidence["run"]["model_id"] == model:
            yield from (a for p in evidence["predictions"] for a in p["attempts"])


def next_model_start(directory, model, interval):
    attempts = list(model_attempts(directory, model))
    starts = [datetime.fromisoformat(a["started_at"].replace("Z", "+00:00")).timestamp() + interval for a in attempts]
    retries = [datetime.fromisoformat(a["retry_not_before"].replace("Z", "+00:00")).timestamp()
               for a in attempts if a["retry_not_before"]]
    return max([0, *starts, *retries])


def current_allowance(snapshot, directory, model, *, now=trial.utc_now):
    """Deduct every locally journaled submission since this account snapshot.

    Both preparation and evaluation consume the SAME model allowance. No automatic
    midnight refresh is inferred. A fresh user/account record is needed on resume.
    """
    current = deepcopy(snapshot)
    verified = datetime.fromisoformat(snapshot["verified_at"].replace("Z", "+00:00"))
    count = sum(datetime.fromisoformat(a["started_at"].replace("Z", "+00:00")) >= verified
                for a in model_attempts(directory, model))
    current["remaining_requests_today"] -= count
    # Preserve at least one request of headroom. All retries/unknown outcomes count.
    if current["remaining_requests_today"] <= 1:
        raise AllowancePause("Daily allowance headroom reached")
    check_access(current, model_id=model, now=now(), request_budget=1, input_token_budget=16000)
    return current


def open_run(output, plan, fresh):
    """Do not replace a frozen plan or repeat completed/unknown submissions."""
    if output.is_symlink() or output.is_junction():
        raise ValueError("Run output must be a regular local directory")
    output.mkdir(parents=True, exist_ok=True)
    if (output / "plan.json").exists():
        saved_plan = trial.read_json(output / "plan.json")
        without_time = lambda p: {k: v for k, v in p.items() if k != "frozen_at"}
        if without_time(plan) != without_time(saved_plan):
            raise ValueError("Frozen comparison plan changed")
        evidence = read_evidence(output / "evidence.json").root
        stable = lambda r: {k: v for k, v in r.items() if k not in {"created_at", "state"}}
        if stable(evidence["run"]) != stable(fresh["run"]):
            raise ValueError("Saved run differs from frozen comparison plan")
        return saved_plan, evidence
    if (output / "evidence.json").exists():
        raise ValueError("Preserve incomplete run directory for investigation")
    trial.atomic_json(output / "plan.json", plan)
    trial.save(output, fresh)
    return plan, fresh


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--model", choices=COMPARISON_MODELS, required=True)
    parser.add_argument("--phase", choices=("trial", "evaluation"), default="trial")
    parser.add_argument("--trial", type=Path, help="Qualifying comparison trial evidence for evaluation")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--access", type=Path, help="Current nonsecret model access/allowance snapshot")
    parser.add_argument("--budget", type=int, default=6, choices=range(1, 13))
    args = parser.parse_args(argv)
    try:
        if args.phase == "trial":
            plan, fresh = prepare_trial(args.package, args.model)
        else:
            if args.trial is None:
                raise ValueError("Evaluation requires a qualifying saved trial")
            qualifying = read_evidence(args.trial).root
            if qualifying["evidence_status"] == "fixture" and args.execute:
                raise ValueError("Fixture qualification cannot be used for live execution")
            plan, fresh = prepare_evaluation(args.package, args.model, qualifying, trial.read_json(args.trial.parent / "plan.json"))
        directory = ROOT / "artifacts/gemini-comparisons"
        snapshot = trial.read_json(args.access) if args.execute and args.access else None
        if args.execute:
            # No key/output access if eligibility/freshness is absent or invalid.
            check_access(snapshot, model_id=args.model, now=trial.utc_now(), request_budget=1, input_token_budget=16000)
        output = directory / fresh["run"]["run_id"]
        if directory.is_symlink() or directory.is_junction() or output.is_symlink() or output.is_junction():
            raise ValueError("Run directory must stay inside the local comparison ledger")
        output.mkdir(parents=True, exist_ok=True)
        with trial.run_lock(output):
            plan, evidence = open_run(output, plan, fresh)
            if args.execute and evidence["run"]["state"] not in {"complete", "stopped"}:
                lock_root = ROOT / "artifacts/gemini-trials"
                lock_root.mkdir(parents=True, exist_ok=True)
                with trial.run_lock(lock_root):
                    trial.atomic_json(output / "access.json", snapshot)
                    try:
                        evidence = evaluation.execute_batch(plan, evidence, args.package / "model-inputs", output, snapshot,
                            budget=args.budget, runtime=600 if args.phase == "trial" else 900,
                            current_access=lambda: current_allowance(snapshot, directory, args.model),
                            earliest_start=lambda: next_model_start(directory, args.model,
                                max(plan["configuration"]["minimum_interval_seconds"], 120 / snapshot["requests_per_minute"])))
                    except AllowancePause:
                        evidence["run"]["state"] = "paused"
                        trial.save(output, evidence)
                        print("PAUSE daily allowance headroom; pending pictures remain pending.")
        successes = sum(p["status"] == "success" for p in evidence["predictions"])
        terminal = sum(p["execution_state"] == "terminal" for p in evidence["predictions"])
        attempts = sum(len(p["attempts"]) for p in evidence["predictions"])
        print(f"PASS comparison {args.phase}: {successes} successes; {terminal}/{len(evidence['predictions'])} terminal; "
              f"{attempts} submissions; state={evidence['run']['state']}; run={evidence['run']['run_id']}")
        print("Saved development evidence only; website unchanged until a complete evaluated run is packaged.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        print("FAIL comparison: check configuration, qualification, input integrity, access freshness and saved snapshot. No raw errors displayed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
