"""Invented answers and generated images only; no provider requests."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image
import pytest

from pipeline.api_contracts import fingerprint, request_fingerprint
from pipeline.evaluate_api import evaluate, evaluate_files, main, wilson


FIXTURES = Path(__file__).parents[1] / "fixtures"


def rebind(evidence):
    for prediction, item in zip(evidence["predictions"], evidence["run"]["inputs"], strict=True):
        prediction["request_sha256"] = request_fingerprint(evidence["run"], item)


@pytest.fixture
def sample():
    evidence = json.loads((FIXTURES / "api-evidence.fixture.json").read_text())
    manifest = json.loads((FIXTURES / "image-manifest.fixture.json").read_text())
    template = manifest["images"].pop()
    manifest["images"][0]["image_id"] = "img-000101"
    manifest["images"][1]["image_id"] = "img-000102"
    for image in manifest["images"]:
        image["display"]["path"] = f"images/{image['image_id']}.png"
    inputs = {"schema_version": 1, "evidence_status": "development_only", "images": []}
    for n, item in enumerate(evidence["run"]["inputs"]):
        image = deepcopy(template)
        image.update(image_id=item["image_id"], source_member=f"test/synthetic/{n}.png",
                     label="anomalous" if n in (0, 2, 4) else "normal")
        image["display"]["path"] = f"images/{item['image_id']}.png"
        if image["label"] == "anomalous":
            image["mask"] = deepcopy(image["display"])
            image["mask"]["path"] = f"masks/{item['image_id']}.png"
        manifest["images"].append(image)
        inputs["images"].append({**item, "path": f"images/{item['image_id']}.png",
                                 "dimensions": image["original_dimensions"]})
    evidence["run"]["hashes"].update(manifest="a" * 64, inputs="b" * 64)
    rebind(evidence)
    return evidence, manifest, inputs


def counter(sample):
    return evaluate(*sample, manifest_sha256="a" * 64, inputs_sha256="b" * 64)


def test_success_metrics_are_separate_from_failure_routing(sample):
    report = counter(sample)
    assert (report["expected"], report["attempted"], report["succeeded"], report["failed"]) == (6, 6, 3, 3)
    assert report["coverage"] == .5
    assert report["failure_breakdown"] == {"refusal": 1, "schema": 1, "timeout": 1}
    assert report["technical_reviews"] == {"normal": 2, "anomalous": 1}
    successful, routing = report["successful_output"], report["full_set_routing"]
    assert [successful[k] for k in ("tp", "fn", "fp", "tn")] == [1, 1, 1, 0]
    assert [routing[k] for k in ("tp", "fn", "fp", "tn")] == [2, 1, 3, 0]
    assert successful["recall"] == .5 and routing["recall"] == 2 / 3
    assert report["images"][2]["decision"] == "uncertain" and report["images"][2]["review"]
    assert report["evidence_status"] == "fixture"
    assert counter(sample) == report  # Reproducible without timestamp or new inference.


def test_zero_denominators_and_wilson_known_values(sample):
    evidence, manifest, _ = sample
    for image in manifest["images"]:
        if image["split"] == "evaluation":
            image.update(label="normal", mask=None)
    report = counter(sample)
    assert report["successful_output"]["recall"] is None
    assert report["full_set_routing"]["recall_wilson_95"] is None
    assert wilson(0, 0) is None
    assert wilson(5, 10) == pytest.approx([0.236593090512564, 0.763406909487436])
    assert wilson(0, 10)[0] == pytest.approx(0, abs=1e-15)
    assert wilson(10, 10)[1] == pytest.approx(1)


@pytest.mark.parametrize("change", ["missing", "extra", "duplicate", "pixel_hash", "manifest_hash", "input_hash", "track", "pending", "preparation"])
def test_cannot_evaluate_partial_changed_or_wrong_membership(sample, change):
    evidence, manifest, inputs = sample
    if change == "missing": inputs["images"].pop()
    elif change == "extra": inputs["images"].append({**inputs["images"][0], "image_id": "img-000999"})
    elif change == "duplicate": inputs["images"].append(inputs["images"][0])
    elif change == "pixel_hash": inputs["images"][0]["sha256"] = "f" * 64
    elif change == "manifest_hash": evidence["run"]["hashes"]["manifest"] = "f" * 64
    elif change == "input_hash": evidence["run"]["hashes"]["inputs"] = "f" * 64
    elif change == "track": evidence["run"]["track_id"] = "metal_surfaces"
    elif change == "pending": evidence["run"]["state"] = "in_progress"
    elif change == "preparation": manifest["images"][2]["split"] = "fitting"; manifest["images"][2]["official_split"] = "train"; manifest["images"][2].update(label="normal", mask=None)
    rebind(evidence)
    with pytest.raises(ValueError): counter(sample)


def test_unreconciled_submission_is_not_a_terminal_inspection(sample):
    evidence = sample[0]
    prediction = evidence["predictions"][-1]
    prediction["status"] = "unknown_outcome"
    prediction["attempts"][-1].update(status="unknown_outcome", reason="interrupted", finished_at=None, latency_ms=None)
    with pytest.raises(ValueError, match="reconciliation"): counter(sample)


@pytest.fixture
def package(sample, tmp_path):
    evidence, manifest, inputs = sample
    # Use v2's honest unpacked-acquisition representation for the file entry point.
    manifest["schema_version"] = 2
    dataset = manifest["dataset"]
    del dataset["acquired_at"], dataset["archive_sha256"]
    dataset["acquisition"] = {"kind": "unpacked_directory", "assurance": "user_supplied_unverified",
        "download_url": None, "acquired_at": None, "archive_sha256": None,
        "content_membership_sha256": "c" * 64, "checked_at": "2026-10-24T10:00:00Z", "context": "TEST ONLY"}
    evaluator, model_root = tmp_path / "evaluator", tmp_path / "model-inputs"
    for folder in (evaluator / "images", evaluator / "masks", model_root / "images"):
        folder.mkdir(parents=True, exist_ok=True)
    for n, image in enumerate(manifest["images"]):
        path = evaluator / image["display"]["path"]
        Image.new("RGB", (32, 24), (n * 25, 20, 30)).save(path)
        digest = sha256(path.read_bytes()).hexdigest()
        image["source_sha256"] = image["display"]["sha256"] = digest
        if image["mask"]:
            mask = evaluator / image["mask"]["path"]
            Image.new("L", (32, 24), 255).save(mask)
            image["mask"]["sha256"] = sha256(mask.read_bytes()).hexdigest()
        if n >= 2:
            (model_root / inputs["images"][n - 2]["path"]).write_bytes(path.read_bytes())
            inputs["images"][n - 2]["sha256"] = digest
            evidence["run"]["inputs"][n - 2]["sha256"] = digest
    manifest_path = evaluator / "image-manifest.v2.json"
    input_path = model_root / "evaluation.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    input_path.write_text(json.dumps(inputs), encoding="utf-8")
    evidence["run"]["hashes"].update(manifest=sha256(manifest_path.read_bytes()).hexdigest(), inputs=sha256(input_path.read_bytes()).hexdigest())
    rebind(evidence)
    saved = tmp_path / "evidence.json"
    saved.write_text(json.dumps(evidence), encoding="utf-8")
    return tmp_path, saved


def test_file_pipeline_and_output_preservation(package):
    root, evidence = package
    output = root / "report.json"
    args = ["--package", str(root), "--evidence", str(evidence), "--out", str(output)]
    assert main(args) == 0
    assert json.loads(output.read_text())["expected"] == 6
    before = output.read_bytes()
    assert main(args) == 1
    assert output.read_bytes() == before


def test_same_ids_different_pixels_are_rejected_even_with_rebound_hashes(package):
    root, saved = package
    evidence = json.loads(saved.read_text())
    index_path = root / "model-inputs/evaluation.json"
    inputs = json.loads(index_path.read_text())
    path = root / "model-inputs" / inputs["images"][0]["path"]
    Image.new("RGB", (32, 24), (254, 253, 252)).save(path)
    inputs["images"][0]["sha256"] = evidence["run"]["inputs"][0]["sha256"] = sha256(path.read_bytes()).hexdigest()
    index_path.write_text(json.dumps(inputs), encoding="utf-8")
    evidence["run"]["hashes"]["inputs"] = sha256(index_path.read_bytes()).hexdigest()
    rebind(evidence)
    saved.write_text(json.dumps(evidence), encoding="utf-8")
    with pytest.raises(ValueError, match="display pixels"): evaluate_files(root, saved)
