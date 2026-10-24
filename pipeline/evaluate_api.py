"""Regenerate complete-set categorical metrics offline. Never calls a provider."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from math import sqrt
from pathlib import Path

from PIL import Image

from pipeline.api_contracts import ApiEvidence, fingerprint, read_evidence
from pipeline.contracts import ImageManifest, read_manifest, verify_assets
from pipeline.model_inputs import read_inputs, VALIDATOR


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def wilson(positive: int, total: int) -> list[float] | None:
    """Two-sided 95% Wilson score interval, without continuity correction."""
    if total == 0:
        return None
    z = 1.959963984540054
    p = positive / total
    scale = 1 + z * z / total
    center = (p + z * z / (2 * total)) / scale
    margin = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / scale
    return [max(0., center - margin), min(1., center + margin)]


def metrics(counts: dict) -> dict:
    tp, fn, fp, tn = (counts[key] for key in ("tp", "fn", "fp", "tn"))
    return dict(counts, anomalous=tp + fn, normal=fp + tn,
                recall=ratio(tp, tp + fn), false_positive_rate=ratio(fp, fp + tn),
                precision=ratio(tp, tp + fp), review_count=tp + fp,
                recall_wilson_95=wilson(tp, tp + fn),
                false_positive_rate_wilson_95=wilson(fp, fp + tn))


def evaluate(evidence: dict, manifest: dict, inputs: dict, *,
             manifest_sha256: str, inputs_sha256: str) -> dict:
    """Bindings are checked here; the file wrapper additionally checks actual pixels.

    Hash parameters are byte hashes of the source files, not semantic JSON hashes.
    Fixture/development status is preserved, never promoted to release authenticity.
    """
    evidence = ApiEvidence.model_validate(evidence).root
    manifest = ImageManifest.model_validate(manifest).root
    if next(VALIDATOR.iter_errors(inputs), None) is not None:
        raise ValueError("Invalid evaluation input index")
    run = evidence["run"]
    if run["state"] != "complete":
        raise ValueError("Evaluation requires a completed run; pending work is not a failure")
    if any(p["status"] == "unknown_outcome" for p in evidence["predictions"]):
        raise ValueError("Unknown submissions require reconciliation before evaluation")
    if run["track_id"] != manifest["track_id"]:
        raise ValueError("Evaluation track mismatch")
    if run["hashes"]["manifest"] != manifest_sha256 or run["hashes"]["inputs"] != inputs_sha256:
        raise ValueError("Evaluation manifest/input fingerprint mismatch")
    expected = {i["image_id"]: i for i in manifest["images"] if i["split"] == "evaluation"}
    actual = {i["image_id"]: i["sha256"] for i in inputs["images"]}
    declared = {i["image_id"]: i["sha256"] for i in run["inputs"]}
    if len(actual) != len(inputs["images"]) or set(actual) != set(expected) or declared != actual:
        raise ValueError("Every evaluation image must be included exactly once with matching pixels")
    successful = dict.fromkeys(("tp", "fn", "fp", "tn"), 0)
    routing = successful.copy()
    failures = Counter()
    technical = {"normal": 0, "anomalous": 0}
    rows = []
    for prediction in sorted(evidence["predictions"], key=lambda p: p["image_id"]):
        image_id = prediction["image_id"]
        label = expected[image_id]["label"]
        success = prediction["status"] == "success"
        attempt = prediction["attempts"][-1]
        response = attempt["response"] if success else None
        review = not success or response["decision"] != "looks_acceptable"
        key = ("tp" if review else "fn") if label == "anomalous" else ("fp" if review else "tn")
        routing[key] += 1
        if success:
            successful[key] += 1
        else:
            failures[attempt["reason"]] += 1
            technical[label] += 1
        rows.append({"image_id": image_id, "label": label, "status": prediction["status"],
                     "decision": response["decision"] if response else None,
                     "review": review, "technical_review": not success})
    n = len(expected)
    failed = sum(failures.values())
    attempted = sum(bool(p["attempts"]) for p in evidence["predictions"])
    versions = sorted({a["reported_model_version"] for p in evidence["predictions"]
                       for a in p["attempts"] if a["reported_model_version"]})
    return {"schema_version": 1,
            "evidence_status": "fixture" if "fixture" in (evidence["evidence_status"], manifest["evidence_status"])
                               else "development_only",
            "run_id": run["run_id"], "track_id": run["track_id"], "model_id": run["model_id"],
            "reported_model_versions": versions, "policy": run["policy"],
            "manifest_sha256": manifest_sha256, "inputs_sha256": inputs_sha256,
            "evidence_sha256": fingerprint(evidence),
            "membership_sha256": fingerprint(sorted(expected)),
            "expected": n, "attempted": attempted, "succeeded": n - failed, "failed": failed,
            "coverage": ratio(n - failed, n), "failure_breakdown": dict(sorted(failures.items())),
            "technical_reviews": technical, "successful_output": metrics(successful),
            "full_set_routing": metrics(routing), "images": rows,
            "limitations": ["Fixed categorical policy: uncertain and technical failures route to human review.",
                "Wilson intervals describe sample uncertainty, not dataset shift or public-benchmark contamination.",
                "Public fastener images are GIS proxies, not factory validation.",
                "Development evidence is not publication clearance or an authenticity certificate."]}


def evaluate_files(package: Path, evidence_path: Path) -> dict:
    """Evaluator-only entry point; verifies clean input/display pixel correspondence."""
    manifest_path = package / "evaluator/image-manifest.v2.json"
    inputs_path = package / "model-inputs/evaluation.json"
    manifest = read_manifest(manifest_path)
    verify_assets(manifest, manifest_path.parent)
    inputs = read_inputs(inputs_path)
    report = evaluate(read_evidence(evidence_path).root, manifest.root, inputs,
                      manifest_sha256=sha256(manifest_path.read_bytes()).hexdigest(),
                      inputs_sha256=sha256(inputs_path.read_bytes()).hexdigest())
    by_id = {i["image_id"]: i for i in manifest.root["images"]}
    for item in inputs["images"]:
        display = manifest_path.parent / by_id[item["image_id"]]["display"]["path"]
        clean = inputs_path.parent / item["path"]
        with Image.open(display) as original, Image.open(clean) as neutral:
            if original.size != neutral.size or original.convert("RGB").tobytes() != neutral.tobytes():
                raise ValueError("Evaluation inputs do not match manifest display pixels")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = evaluate_files(args.package, args.evidence)
        content = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
        with args.out.open("x", encoding="utf-8", newline="\n") as output:
            output.write(content)
    except (ValueError, OSError):
        print("FAIL evaluation: check complete run, package identities/assets and unused output path")
        return 1
    print(f"PASS evaluation ({report['evidence_status']}): {report['expected']} expected; "
          f"{report['succeeded']} successful; {report['failed']} technical reviews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
