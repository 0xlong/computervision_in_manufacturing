"""Build a validated local-only evidence package; no inference or publication."""

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import argparse
import json
from pathlib import Path
import shutil

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import JsonValue, RootModel, model_validator
from referencing import Registry, Resource

from pipeline.api_contracts import ApiEvidence, fingerprint, read_evidence, strict_json
from pipeline.contracts import read_manifest
from pipeline.evaluate_api import evaluate_files, metrics
from pipeline.run_gemini_trial import TRIAL_SCHEMA


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {name: json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8")) for name in
    ("api-evidence.v1.schema.json", "evaluation-report.v1.schema.json", "fastener-bundle.v2.schema.json", "visitor-state.v1.schema.json", "model-inputs.v1.schema.json", "frozen-configuration.v1.schema.json", "frozen-configuration.v2.schema.json", "frozen-configuration.v3.schema.json")}
for schema in SCHEMAS.values(): Draft202012Validator.check_schema(schema)
REGISTRY = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in SCHEMAS.values())
VALIDATOR = Draft202012Validator(SCHEMAS["fastener-bundle.v2.schema.json"], registry=REGISTRY, format_checker=FormatChecker())


def validate_bundle(data):
    json.dumps(data, allow_nan=False)
    if next(VALIDATOR.iter_errors(data), None): raise ValueError("Invalid local fastener bundle schema")
    if data["bundle_id"] != "fasteners-" + fingerprint({k: v for k, v in data.items() if k != "bundle_id"})[:16]:
        raise ValueError("Bundle content fingerprint mismatch")
    images = {i["image_id"]: i for i in data["images"]}
    if len(images) != 5 or set(images) != set(data["challenge"]["image_ids"]) or Counter(i["label"] for i in images.values()) != {"normal": 2, "anomalous": 3}:
        raise ValueError("Challenge requires exactly two normal and three anomalous evaluation images")
    for i in images.values():
        if i["display"]["path"] != f"images/{i['image_id']}.png" or (i["mask"] is None) != (i["label"] == "normal"):
            raise ValueError("Challenge asset identity mismatch")
        if i["mask"] and (i["mask"]["path"] != f"masks/{i['image_id']}.png" or i["mask"]["dimensions"] != i["display"]["dimensions"]):
            raise ValueError("Challenge mask identity/alignment mismatch")
    if {n["path"] for n in data["notices"]} != {"notices/license.txt", "notices/readme.txt"}:
        raise ValueError("Dataset notices must be complete")
    run_ids = set()
    config_ids = [c["run_id"] for c in data["configuration_assets"]]
    if len(config_ids) != len(set(config_ids)):
        raise ValueError("Duplicate configuration asset identity")
    membership = None
    for saved in data["runs"]:
        evidence = ApiEvidence.model_validate(saved["evidence"]).root
        run, report = evidence["run"], saved["report"]
        if run["state"] != "complete" or run["track_id"] != "fasteners" or run["run_id"] in run_ids:
            raise ValueError("Bundle needs distinct completed fastener runs")
        run_ids.add(run["run_id"])
        if data["execution"] == "recorded_live" and run["run_id"] not in config_ids:
            raise ValueError("Live evidence needs its frozen public configuration")
        if (report["run_id"], report["model_id"], report["manifest_sha256"], report["inputs_sha256"], report["evidence_sha256"]) != (
                run["run_id"], run["model_id"], data["manifest_sha256"], run["hashes"]["inputs"], fingerprint(evidence)) or run["hashes"]["manifest"] != data["manifest_sha256"]:
            raise ValueError("Bundle run/report provenance mismatch")
        rows = {i["image_id"]: i for i in report["images"]}
        inputs = {i["image_id"] for i in run["inputs"]}
        if len(rows) != len(report["images"]) or set(rows) != inputs or not set(images) <= inputs:
            raise ValueError("Bundle complete-set membership mismatch")
        identity = [(k, rows[k]["label"]) for k in sorted(rows)]
        if membership is not None and identity != membership: raise ValueError("Models must share evaluation labels/membership")
        membership = identity
        if report["membership_sha256"] != fingerprint(sorted(rows)): raise ValueError("Membership fingerprint mismatch")
        successful = dict.fromkeys(("tp", "fn", "fp", "tn"), 0)
        routing = successful.copy(); failures = Counter(); technical = {"normal": 0, "anomalous": 0}
        for p in evidence["predictions"]:
            row = rows[p["image_id"]]; a = p["attempts"][-1] if p["attempts"] else None
            if p["execution_state"] != "terminal" or p["status"] == "unknown_outcome" or a is None:
                raise ValueError("Pending or unreconciled bundle prediction")
            success = p["status"] == "success"
            decision = a["response"]["decision"] if success else None
            review = not success or decision != "looks_acceptable"
            if (row["status"], row["decision"], row["review"], row["technical_review"]) != (p["status"], decision, review, not success):
                raise ValueError("Report routing disagrees with saved response")
            key = ("tp" if review else "fn") if row["label"] == "anomalous" else ("fp" if review else "tn")
            routing[key] += 1
            if success: successful[key] += 1
            else: failures[a["reason"]] += 1; technical[row["label"]] += 1
        n, failed = len(rows), sum(failures.values())
        if (report["expected"], report["attempted"], report["succeeded"], report["failed"], report["coverage"]) != (n, n, n - failed, failed, (n - failed) / n):
            raise ValueError("Bundle coverage/count mismatch")
        if report["successful_output"] != metrics(successful) or report["full_set_routing"] != metrics(routing) or report["failure_breakdown"] != dict(failures) or report["technical_reviews"] != technical:
            raise ValueError("Bundle metrics disagree with complete saved responses")
        if any(rows[k]["label"] != i["label"] for k, i in images.items()): raise ValueError("Challenge reference mismatch")
        if "fixture" in (evidence["evidence_status"], report["evidence_status"]) and (data["execution"] != "fixture" or data["evidence_status"] != "fixture"):
            raise ValueError("Fixture predictions must stay labelled fixture")
    if data["execution"] == "recorded_live" and set(config_ids) != run_ids:
        raise ValueError("Configuration assets must match all completed runs")
    return deepcopy(data)


class FastenerBundle(RootModel[dict[str, JsonValue]]):
    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, data): return validate_bundle(data)


class VisitorStateArtifact(RootModel[dict[str, JsonValue]]):
    """Canonical shape only; bundle-dependent selections are checked by the app."""
    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, data):
        json.dumps(data, allow_nan=False)
        if next(Draft202012Validator(SCHEMAS["visitor-state.v1.schema.json"]).iter_errors(data), None):
            raise ValueError("Invalid visitor state schema")
        return deepcopy(data)


class FrozenConfiguration(RootModel[dict[str, JsonValue]]):
    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, data):
        version = data.get("schema_version")
        if version not in (1, 2, 3): raise ValueError("Unsupported frozen configuration version")
        validator = Draft202012Validator(SCHEMAS[f"frozen-configuration.v{version}.schema.json"], registry=REGISTRY, format_checker=FormatChecker())
        if next(validator.iter_errors(data), None): raise ValueError("Invalid frozen configuration schema")
        plan = data["frozen_plan"]
        identity = fingerprint({k: v for k, v in plan.items() if k not in {"frozen_at", "run_id"}})
        prefix = {1: "eval-flash-lite-", 2: "eval-comparison-", 3: "eval-gemma-"}[version]
        if data["run_id"] != plan["run_id"] or plan["run_id"] != prefix + identity[:16]:
            raise ValueError("Frozen configuration identity mismatch")
        config = deepcopy(plan["configuration"])
        if config["max_requests_per_model"] != 345 or config["minimum_interval_seconds"] != 10:
            raise ValueError("Unexpected evaluation bounds")
        config.update(max_requests_per_model=3 if version == 3 else 6,
                      minimum_interval_seconds={1: 65, 2: 10, 3: 60}[version])
        schema = (TRIAL_SCHEMA if version == 1 else json.loads((ROOT / "schemas" /
            ("gemma-trial.v1.schema.json" if version == 3 else "gemini-trial.v2.schema.json")).read_text(encoding="utf-8")))
        if not Draft202012Validator(schema).is_valid(config): raise ValueError("Frozen request settings mismatch")
        ids = [i["image_id"] for i in plan["probes"]]
        if len(set(ids)) != 115 or plan["reference"]["image_id"] in ids:
            raise ValueError("Frozen reference/evaluation membership mismatch")
        return deepcopy(data)


def public_configuration(plan):
    version = 3 if plan["model_id"].startswith("gemma-4-") else 2 if plan["configuration"]["schema_version"] == 2 else 1
    limits = {"submissions_per_batch": 12, "batch_request_wait_seconds": 900,
              "request_timeout_seconds": 60, "minimum_start_interval_seconds": 10,
              "maximum_run_submissions": 345, "attempts_per_image": 3}
    if version == 2:
        limits.update(daily_request_headroom=1, shared_trial_evaluation_allowance=True, automatic_daily_reset=False,
                      quota_start_spacing="max(10 seconds, 120 / verified RPM)")
    if version == 3:
        limits.update(daily_request_headroom=1, shared_trial_evaluation_allowance=True, automatic_daily_reset=False,
                      shared_gemma_allowance=True, input_window_seconds=60, input_reservation=4096,
                      quota_start_spacing="max(10 seconds, 120 / verified RPM), plus shared rolling input-token reservation")
    data = {"schema_version": version, "run_id": plan["run_id"], "frozen_plan": plan,
            "effective_execution_limits": limits,
            "notes": ["The frozen dictionary retains trial-purpose/probe-count/runtime fields as inherited history; the outer purpose/probes and effective execution limits describe complete evaluation.",
                "No evaluator labels, masks, visitor data or credentials entered these requests. Input paths are neutral model-input-relative identities."]}
    if version == 2:
        data["notes"].append("Model-specific thinking settings are frozen configurations, not identical reasoning effort. Trials and evaluation share each model's verified daily allowance.")
    if version == 3:
        data["notes"].append("Gemma uses minimal thinking. All local Gemma trials/evaluations conservatively share the supplied request/token caps; failed or unknown requests reserve 4096 input tokens. This is a recorded model/configuration combination, not identical reasoning effort.")
    FrozenConfiguration.model_validate(data)
    return data


def build(package: Path, evidence_paths: list[Path], output: Path, *, challenge_from: Path | None = None):
    if output.exists(): raise ValueError("Preserve existing bundle; choose unused output directory")
    manifest = read_manifest(package / "evaluator/image-manifest.v2.json").root
    runs = [{"evidence": read_evidence(p).root, "report": evaluate_files(package, p)} for p in evidence_paths]
    by_id = {i["image_id"]: i for i in manifest["images"] if i["split"] == "evaluation"}
    rows = {i["image_id"]: i for i in runs[0]["report"]["images"]}
    # Curate only after complete evaluation; prefer a real mistake if available.
    normal = sorted((i for i in by_id if by_id[i]["label"] == "normal"), key=lambda i: (not rows[i]["review"], i))[:2]
    anomalies = sorted((i for i in by_id if by_id[i]["label"] == "anomalous"), key=lambda i: (rows[i]["review"], i))
    selected = []; groups = set()
    for i in anomalies:
        group = by_id[i]["source_member"].split("/")[-2]
        if group not in groups: selected.append(i); groups.add(group)
        if len(selected) == 3: break
    challenge_ids = [normal[0], selected[0], normal[1], selected[1], selected[2]]
    if challenge_from is not None:
        previous = validate_bundle(strict_json(challenge_from.read_text(encoding="utf-8")))
        if previous["manifest_sha256"] != runs[0]["report"]["manifest_sha256"]:
            raise ValueError("Previous challenge uses another manifest")
        challenge_ids = previous["challenge"]["image_ids"]
        for image in previous["images"]:
            if {k: by_id[image["image_id"]][k] for k in ("image_id", "label", "display", "mask")} != image:
                raise ValueError("Previous challenge assets/labels changed")
    images = [{k: deepcopy(by_id[i][k]) for k in ("image_id", "label", "display", "mask")} for i in challenge_ids]
    fixture = any(r["report"]["evidence_status"] == "fixture" for r in runs)
    configurations = []
    if not fixture:
        for path, saved in zip(evidence_paths, runs, strict=True):
            access = strict_json((path.parent / "access.json").read_text(encoding="utf-8"))
            plan = strict_json((path.parent / "plan.json").read_text(encoding="utf-8"))
            if not all(access.get(k) is True for k in ("free_execution_verified", "paid_execution_disabled", "terms_and_data_use_verified")) or plan["run_id"] != saved["evidence"]["run"]["run_id"]:
                raise ValueError("Missing local execution/access audit records")
            if fingerprint({k: v for k, v in plan.items() if k not in {"frozen_at", "run_id"}}) != saved["evidence"]["run"]["hashes"]["configuration"]:
                raise ValueError("Frozen configuration does not match run")
            public_config = public_configuration(plan)
            content = (json.dumps(public_config, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
            configurations.append((f"configurations/{plan['run_id']}.json", content, plan["run_id"]))
    dataset = {k: manifest["dataset"][k] for k in ("dataset_id", "category", "attribution", "licence", "licence_url", "source_url", "modification_notice")}
    notices = []
    for name in ("license.txt", "readme.txt"):
        source = package / "evaluator" / name
        if not source.is_file() or source.is_symlink() or source.is_junction(): raise ValueError("Original notices are required")
        notices.append({"path": f"notices/{name}", "sha256": sha256(source.read_bytes()).hexdigest()})
    bundle = {"schema_version": 2, "bundle_id": "pending", "track_id": "fasteners", "local_only": True,
        "evidence_status": "fixture" if fixture else "development_only", "execution": "fixture" if fixture else "recorded_live",
        "dataset": dataset, "manifest_sha256": runs[0]["report"]["manifest_sha256"],
        "challenge": {"version": "fastener-challenge-v1", "image_ids": challenge_ids,
            "rationale": "Five teaching examples selected after complete evaluation: two normal and three anomalous images from distinct defect groups; prefer a genuine missed anomaly or normal review when available. Curated examples do not change benchmark membership or establish superiority."},
        "images": images, "runs": runs, "notices": notices,
        "configuration_assets": [{"run_id": run_id, "path": path, "sha256": sha256(content).hexdigest()} for path, content, run_id in configurations],
        "limitations": ["Local noncommercial development evidence; not cleared for publication.",
            "Public MVTec fasteners are GIS manufacturing proxies, not validated factory criteria or affiliation.",
            "General-purpose models may have encountered this public benchmark during training.",
            "Unpacked acquisition has missing URL/time/archive receipt; physical-object/session independence is unverified.",
            "API decisions have no authentic heatmap, calibrated probability or adjustable sensitivity.",
            "Human review is required; this does not establish production readiness."]}
    bundle["bundle_id"] = "fasteners-" + fingerprint({k: v for k, v in bundle.items() if k != "bundle_id"})[:16]
    validate_bundle(bundle)
    output.mkdir(parents=True)
    for image in images:
        for asset in (image["display"], image["mask"]):
            if asset:
                target = output / asset["path"]; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(package / "evaluator" / asset["path"], target)
                if sha256(target.read_bytes()).hexdigest() != asset["sha256"]: raise ValueError("Copied asset changed")
    (output / "notices").mkdir()
    for name in ("license.txt", "readme.txt"):
        shutil.copyfile(package / "evaluator" / name, output / "notices" / name)
    if any(sha256((output / n["path"]).read_bytes()).hexdigest() != n["sha256"] for n in notices):
        raise ValueError("Copied dataset notice changed")
    for path, content, _ in configurations:
        target = output / path; target.parent.mkdir(exist_ok=True); target.write_bytes(content)
    (output / "bundle.json").write_text(json.dumps(bundle, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return bundle


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--challenge-from", type=Path, help="Preserve five teaching IDs/assets from an existing validated bundle")
    args = parser.parse_args(argv)
    try:
        bundle = build(args.package, args.evidence, args.out, challenge_from=args.challenge_from)
    except (ValueError, OSError, KeyError, IndexError):
        print("FAIL bundle: check complete evidence, identities, source assets and unused destination"); return 1
    print(f"PASS local bundle: {bundle['bundle_id']}; {len(bundle['runs'])} run(s); 5 challenge pictures"); return 0


if __name__ == "__main__": raise SystemExit(main())
