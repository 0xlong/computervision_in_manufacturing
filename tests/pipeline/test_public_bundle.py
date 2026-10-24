"""Generated bundle fixtures, kept separate from authentic saved inference."""

from hashlib import sha256
import json
from pathlib import Path

import pytest

from pipeline.api_contracts import fingerprint
from pipeline.public_bundle import FastenerBundle, VisitorStateArtifact, build, validate_bundle
from test_evaluate_api import package, sample, rebind  # Shared generated-image fixtures.


@pytest.fixture
def bundled(package):
    root, saved = package
    (root / "evaluator/license.txt").write_text("TEST ONLY: no real dataset images; fixture notice.", encoding="utf-8")
    (root / "evaluator/readme.txt").write_text("TEST ONLY: generated shapes and invented predictions.", encoding="utf-8")
    manifest_path = root / "evaluator/image-manifest.v2.json"
    manifest = json.loads(manifest_path.read_text())
    for n, image in enumerate(manifest["images"]):
        if image["split"] == "evaluation": image["source_member"] = f"test/synthetic{n}/{n}.png"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    evidence = json.loads(saved.read_text())
    evidence["run"]["hashes"]["manifest"] = sha256(manifest_path.read_bytes()).hexdigest()
    rebind(evidence)
    saved.write_text(json.dumps(evidence), encoding="utf-8")
    output = root / "bundle"
    return build(root, [saved], output), root, saved, output


def seal(data):
    data["bundle_id"] = "fasteners-" + fingerprint({k: v for k, v in data.items() if k != "bundle_id"})[:16]


def test_shared_schema_pydantic_and_builder_preserve_fixture_status(bundled):
    bundle, root, saved, output = bundled
    assert bundle["execution"] == "fixture" and bundle["evidence_status"] == "fixture"
    assert FastenerBundle.model_validate(bundle).root == bundle
    assert len(bundle["challenge"]["image_ids"]) == 5
    assert len(list((output / "images").glob("*.png"))) == 5
    assert len(list((output / "masks").glob("*.png"))) == 3
    assert len(bundle["runs"][0]["report"]["images"]) == 6
    assert not any(word in json.dumps(bundle) for word in ('"access"', 'Authorization', str(root)))
    assert build(root, [saved], root / "bundle-again") == bundle
    before = (output / "bundle.json").read_bytes()
    with pytest.raises(ValueError): build(root, [saved], output)
    assert (output / "bundle.json").read_bytes() == before


@pytest.mark.parametrize("change", ["metric", "coverage", "membership", "manifest", "mask", "unsafe", "fixture_promotion", "version", "duplicate_run"])
def test_inconsistent_evidence_is_rejected_after_resealing(bundled, change):
    data = bundled[0]
    if change == "metric": data["runs"][0]["report"]["full_set_routing"]["fn"] += 1
    elif change == "coverage": data["runs"][0]["report"]["succeeded"] += 1
    elif change == "membership": data["runs"][0]["report"]["images"].pop()
    elif change == "manifest": data["manifest_sha256"] = "f" * 64
    elif change == "mask": next(i for i in data["images"] if i["mask"])["mask"]["dimensions"]["width_px"] += 1
    elif change == "unsafe": data["images"][0]["display"]["path"] = "../private.png"
    elif change == "fixture_promotion": data.update(execution="recorded_live", evidence_status="development_only")
    elif change == "version": data["schema_version"] = 999
    elif change == "duplicate_run": data["runs"].append(data["runs"][0])
    seal(data)
    with pytest.raises(ValueError): validate_bundle(data)


def test_content_hash_change_is_detected(bundled):
    data = bundled[0]; data["limitations"].append("TEST altered after hashing")
    with pytest.raises(ValueError, match="fingerprint"): validate_bundle(data)


def test_shared_fixture_contract():
    data = json.loads(Path("tests/fixtures/fastener-bundle.fixture.json").read_text(encoding="utf-8"))
    assert FastenerBundle.model_validate(data).root["execution"] == "fixture"


def test_visitor_state_canonical_schema_and_pydantic_agree():
    bundle = json.loads(Path("tests/fixtures/fastener-bundle.fixture.json").read_text(encoding="utf-8"))
    state = {"schema_version": 1, "bundle_id": bundle["bundle_id"], "track_id": "fasteners",
        "screen": "start", "selectedImage": bundle["challenge"]["image_ids"][0],
        "selectedRun": bundle["runs"][0]["evidence"]["run"]["run_id"], "comparisonRun": "",
        "answers": {}, "revealed": [], "scenario": {"volume": 1000, "prevalence": .01,
        "minutes": 2, "capacity": 240, "reviewCost": 1, "missedCost": 100}, "decision": "", "rationale": ""}
    assert VisitorStateArtifact.model_validate(state).root == state
    for key, value in (("schema_version", 999), ("rationale", "x" * 2001), ("extra", "unsupported")):
        with pytest.raises(ValueError): VisitorStateArtifact.model_validate({**state, key: value})
