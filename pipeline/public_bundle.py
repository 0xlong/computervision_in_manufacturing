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


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {name: json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8")) for name in
    ("api-evidence.v1.schema.json", "evaluation-report.v1.schema.json", "fastener-bundle.v1.schema.json", "visitor-state.v1.schema.json")}
for schema in SCHEMAS.values(): Draft202012Validator.check_schema(schema)
REGISTRY = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in SCHEMAS.values())
VALIDATOR = Draft202012Validator(SCHEMAS["fastener-bundle.v1.schema.json"], registry=REGISTRY, format_checker=FormatChecker())


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
    membership = None
    for saved in data["runs"]:
        evidence = ApiEvidence.model_validate(saved["evidence"]).root
        run, report = evidence["run"], saved["report"]
        if run["state"] != "complete" or run["track_id"] != "fasteners" or run["run_id"] in run_ids:
            raise ValueError("Bundle needs distinct completed fastener runs")
        run_ids.add(run["run_id"])
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


def build(package: Path, evidence_paths: list[Path], output: Path):
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
    images = [{k: deepcopy(by_id[i][k]) for k in ("image_id", "label", "display", "mask")} for i in challenge_ids]
    fixture = any(r["report"]["evidence_status"] == "fixture" for r in runs)
    if not fixture:
        for path, saved in zip(evidence_paths, runs, strict=True):
            access = strict_json((path.parent / "access.json").read_text(encoding="utf-8"))
            plan = strict_json((path.parent / "plan.json").read_text(encoding="utf-8"))
            if not all(access.get(k) is True for k in ("free_execution_verified", "paid_execution_disabled", "terms_and_data_use_verified")) or plan["run_id"] != saved["evidence"]["run"]["run_id"]:
                raise ValueError("Missing local execution/access audit records")
    dataset = {k: manifest["dataset"][k] for k in ("dataset_id", "category", "attribution", "licence", "licence_url", "source_url", "modification_notice")}
    notices = []
    for name in ("license.txt", "readme.txt"):
        source = package / "evaluator" / name
        if not source.is_file() or source.is_symlink() or source.is_junction(): raise ValueError("Original notices are required")
        notices.append({"path": f"notices/{name}", "sha256": sha256(source.read_bytes()).hexdigest()})
    bundle = {"schema_version": 1, "bundle_id": "pending", "track_id": "fasteners", "local_only": True,
        "evidence_status": "fixture" if fixture else "development_only", "execution": "fixture" if fixture else "recorded_live",
        "dataset": dataset, "manifest_sha256": runs[0]["report"]["manifest_sha256"],
        "challenge": {"version": "fastener-challenge-v1", "image_ids": challenge_ids,
            "rationale": "Five teaching examples selected after complete evaluation: two normal and three anomalous images from distinct defect groups; prefer a genuine missed anomaly or normal review when available. Curated examples do not change benchmark membership or establish superiority."},
        "images": images, "runs": runs, "notices": notices,
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
    (output / "bundle.json").write_text(json.dumps(bundle, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return bundle


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        bundle = build(args.package, args.evidence, args.out)
    except (ValueError, OSError, KeyError, IndexError):
        print("FAIL bundle: check complete evidence, identities, source assets and unused destination"); return 1
    print(f"PASS local bundle: {bundle['bundle_id']}; {len(bundle['runs'])} run(s); 5 challenge pictures"); return 0


if __name__ == "__main__": raise SystemExit(main())
