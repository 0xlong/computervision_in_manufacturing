"""Generated fixtures test provenance and the answer-free inference boundary."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image, PngImagePlugin
from pydantic import ValidationError
import pytest

from pipeline.audit_mvtec_ad_directory import audit_directory
from pipeline.contracts import ImageManifest, verify_assets
from pipeline.model_inputs import read_inputs, validate_inputs
from pipeline.plan_preparation import build_plan
from pipeline.prepare_inputs import prepare


def acquisition(membership="a"*64):
    return {"kind": "unpacked_directory", "assurance": "user_supplied_unverified",
            "download_url": None, "acquired_at": None, "archive_sha256": None,
            "content_membership_sha256": membership, "checked_at": "2026-10-23T12:00:00Z",
            "context": "TEST ONLY user-supplied unpacked fixture; no download receipt."}


def v2():
    data = json.loads((Path(__file__).parents[1]/"fixtures/image-manifest.fixture.json").read_text())
    data["schema_version"] = 2
    del data["dataset"]["acquired_at"], data["dataset"]["archive_sha256"]
    data["dataset"]["acquisition"] = acquisition()
    return data


def test_v2_unknowns_are_explicit_and_v1_remains_strict():
    data = v2()
    assert ImageManifest.model_validate(data).root["dataset"]["acquisition"]["archive_sha256"] is None
    data["schema_version"] = 1
    with pytest.raises(ValidationError):
        ImageManifest.model_validate(data)


@pytest.mark.parametrize("key,value", [("kind", "official_verified"), ("assurance", "verified"),
    ("checked_at", "2026-02-30T00:00:00Z"), ("acquired_at", "unknown"),
    ("archive_sha256", "unknown"), ("download_url", "file:///private"),
    ("content_membership_sha256", None)])
def test_v2_rejects_invalid_acquisition_values(key, value):
    data = v2()
    data["dataset"]["acquisition"][key] = value
    with pytest.raises(ValidationError):
        ImageManifest.model_validate(data)


def test_archive_route_requires_receipt_fields_and_future_versions_fail():
    data = v2()
    data["dataset"]["acquisition"]["kind"] = "archive"
    with pytest.raises(ValidationError):
        ImageManifest.model_validate(data)
    data["dataset"]["acquisition"].update(download_url="https://example.invalid/test.tar",
        acquired_at="2026-10-23T11:00:00Z", archive_sha256="b"*64)
    assert ImageManifest.model_validate(data)
    data["schema_version"] = 3
    with pytest.raises(ValidationError):
        ImageManifest.model_validate(data)


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "source"
    for n in range(10):
        path = root/f"train/good/{n:03d}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("answer", "normal: TEST secret label in metadata")
        Image.new("RGB", (32,32), (n*20,30,40)).save(path, pnginfo=metadata)
    path = root/"test/good/000.png"
    path.parent.mkdir(parents=True)
    Image.new("RGB", (32,32), (0,70,80)).save(path)
    for member, mode, value in (("test/bent/000.png", "RGB", (0,80,90)),
                               ("ground_truth/bent/000_mask.png", "L", 255)):
        path = root/member
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new(mode, (32,32), value).save(path)
    audit = audit_directory(root)
    return root, build_plan(root, audit), acquisition(audit["membership_sha256"])


def test_export_cleans_metadata_preserves_pixels_and_exact_membership(source, tmp_path):
    root, plan, acq = source
    before = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*.png")}
    out = tmp_path/"output"
    report = prepare(root, plan, acq, out, require_summary=False)
    assert {s:r["count"] for s,r in report["indexes"].items()} == {"fitting":8,"calibration":2,"evaluation":2}
    manifest = ImageManifest.model_validate(json.loads((out/"evaluator/image-manifest.v2.json").read_text()))
    assert verify_assets(manifest, out/"evaluator") == 13
    by_id = {i["image_id"]: i for i in plan["images"]}
    seen = set()
    for split in ("fitting","calibration","evaluation"):
        index = read_inputs(out/f"model-inputs/{split}.json")
        assert not any(word in json.dumps(index) for word in ("label", "mask", "source_member", "good", "normal"))
        for image in index["images"]:
            seen.add(image["image_id"])
            original = Image.open(root/by_id[image["image_id"]]["source_member"])
            clean = Image.open(out/"model-inputs"/image["path"])
            assert clean.info == {} and clean.tobytes() == original.tobytes()
    assert seen == set(by_id)
    assert {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob("*.png")} == before
    assert not (out/"model-inputs/masks").exists()
    with pytest.raises(ValueError):
        prepare(root, plan, acq, out, require_summary=False)


@pytest.mark.parametrize("change", ["label", "path", "hash", "duplicate", "dimensions", "metadata"])
def test_input_boundary_rejects_leaks_corruption_and_mismatches(source, tmp_path, change):
    root, plan, acq = source
    out = tmp_path/"output"
    prepare(root, plan, acq, out, require_summary=False)
    model_root = out/"model-inputs"
    index = read_inputs(model_root/"fitting.json")
    item = index["images"][0]
    if change == "label": item["label"] = "normal"
    elif change == "path": item["path"] = "../evaluator/image.png"
    elif change == "hash": item["sha256"] = "0"*64
    elif change == "duplicate": index["images"].append(deepcopy(item))
    elif change == "dimensions": item["dimensions"]["width_px"] = 100
    else:
        meta = PngImagePlugin.PngInfo(); meta.add_text("label", "normal")
        Image.new("RGB", (32,32)).save(model_root/item["path"], pnginfo=meta)
        item["sha256"] = sha256((model_root/item["path"]).read_bytes()).hexdigest()
    with pytest.raises(ValueError): validate_inputs(index, model_root)


def test_stale_plan_content_provenance_and_output_containment_fail(source, tmp_path):
    root, plan, acq = source
    with pytest.raises(ValueError): prepare(root, plan, acq, root/"output", require_summary=False)
    bad = deepcopy(acq); bad["content_membership_sha256"] = "b"*64
    with pytest.raises(ValueError): prepare(root, plan, bad, tmp_path/"bad", require_summary=False)
    assert not (tmp_path/"bad").exists()
    plan["images"][0]["source_sha256"] = "0"*64
    with pytest.raises(ValueError): prepare(root, plan, acq, tmp_path/"stale", require_summary=False)


def test_similarity_followup_rebuilds_saved_shortlist_and_never_assigns_identity(source, tmp_path):
    from pipeline.compare_related import follow_up
    from pipeline.review_preparation import generate_review
    root, plan, _ = source
    review = generate_review(root, plan, tmp_path/"review")
    before = deepcopy(plan)
    report = follow_up(root, plan, review)
    assert report["results"]
    assert all(p["identity_status"] == "unresolved" for p in report["results"])
    assert report["freeze_status"] == "blocked_by_unresolved_related_object_risk"
    assert plan == before
    review["candidates"].pop()
    with pytest.raises(ValueError, match="shortlist"):
        follow_up(root, plan, review)


@pytest.mark.parametrize("content", ['{"images": [], "images": []}', '{"score": NaN}'])
def test_input_reader_rejects_ambiguous_or_nonfinite_json(tmp_path, content):
    path = tmp_path/"input.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError): read_inputs(path)
