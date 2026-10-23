"""Small generated images test split proposals; no source or model claim is made."""

from copy import deepcopy
import json

from PIL import Image, PngImagePlugin
import pytest

from pipeline.audit_mvtec_ad_directory import audit_directory
from pipeline.inventory_mvtec_ad import InventoryError
from pipeline.plan_preparation import build_plan, main, validate_plan


@pytest.fixture
def sample(tmp_path):
    root = tmp_path / "fixture"
    for index in range(10):
        p = root / f"train/good/{index:03d}.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (8, 6), (index * 20, 0, 0)).save(p)
    for name, mode, value in (("test/good/000.png", "RGB", (80, 80, 80)),
            ("test/bent/000.png", "RGB", (90, 90, 90)), ("ground_truth/bent/000_mask.png", "L", 255)):
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new(mode, (8, 6), value).save(p)
    return root, audit_directory(root)


def test_known_seeded_split_and_full_evaluation_membership(sample):
    root, audit = sample
    plan = build_plan(root, audit)
    assert plan["evidence_status"] == "development_only"
    assert {i["source_member"] for i in plan["images"] if i["split"] == "calibration"} == {
        "train/good/003.png", "train/good/007.png"}
    assert len([i for i in plan["images"] if i["split"] == "fitting"]) == 8
    assert {i["source_member"] for i in plan["images"] if i["split"] == "evaluation"} == {
        "test/good/000.png", "test/bent/000.png"}
    assert plan["evaluation_overlap_ids"] == []
    assert str(root) not in json.dumps(plan)
    validate_plan(plan)


def test_rounding_reserves_ceil_one_fifth(sample):
    root, _ = sample
    Image.new("RGB", (8, 6), (10, 20, 30)).save(root / "train/good/010.png")
    plan = build_plan(root, audit_directory(root))
    assert sum(i["split"] == "calibration" for i in plan["images"]) == 3


def test_order_independence_and_repeatability(sample):
    root, audit = sample
    first = build_plan(root, audit)
    audit["images"].reverse()
    assert build_plan(root, audit) == first
    first["method"]["seed"] = 99
    assert build_plan(root, audit)["method"]["seed"] == 42


def test_reencoded_identical_pixels_cannot_cross_preparation_groups(sample):
    root, _ = sample
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("fixture", "Different encoding of the same TEST ONLY picture")
    with Image.open(root / "train/good/000.png") as original:
        original.save(root / "train/good/003.png", pnginfo=metadata)
    assert (root / "train/good/000.png").read_bytes() != (root / "train/good/003.png").read_bytes()
    with pytest.raises(InventoryError, match="cross preparation"):
        build_plan(root, audit_directory(root))


def test_test_overlap_is_reported_without_dropping_any_test_image(sample):
    root, _ = sample
    (root / "test/good/000.png").write_bytes((root / "train/good/000.png").read_bytes())
    plan = build_plan(root, audit_directory(root))
    assert plan["evaluation_overlap_ids"] == ["img-000002"]
    assert sum(i["split"] == "evaluation" for i in plan["images"]) == 2


@pytest.mark.parametrize("change", ["schema", "status", "selection", "identity", "official", "overlap"])
def test_modified_plan_is_rejected(sample, change):
    root, audit = sample
    plan = build_plan(root, audit)
    if change == "schema":
        plan["schema_version"] = 2
    elif change == "status":
        plan["evidence_status"] = "authentic"
    elif change == "selection":
        for image in plan["images"]:
            if image["source_member"] == "train/good/003.png": image["split"] = "fitting"
    elif change == "identity":
        plan["images"][0]["image_id"] = plan["images"][1]["image_id"]
    elif change == "official":
        plan["images"][0].update(official_split="train", split="fitting")
    else:
        plan["evaluation_overlap_ids"] = ["img-000001"]
    with pytest.raises(InventoryError): validate_plan(plan)


def test_files_changed_after_audit_are_rejected(sample):
    root, audit = sample
    (root / "train/good/000.png").write_bytes(b"TEST ONLY changed file")
    with pytest.raises(InventoryError, match="changed"):
        build_plan(root, audit)


def test_unsafe_input_path_is_rejected_before_reading(sample):
    root, audit = sample
    audit["images"][0]["source_member"] = "../outside.png"
    with pytest.raises(InventoryError, match="path"):
        build_plan(root, audit)


def test_cli_failure_and_no_overwrite(sample, tmp_path, monkeypatch, capsys):
    root, audit = sample
    output = tmp_path / "plan.json"
    args = [str(root), "--output", str(output)]
    # The generated example fails the actual 335-image category summary.
    monkeypatch.setattr("pipeline.plan_preparation.audit_directory", lambda _: deepcopy(audit))
    assert main(args) == 1 and not output.exists()
    assert "mismatch" in capsys.readouterr().out
    # Isolate successful CLI writing from the separate real-count audit test.
    audit["published_summary_matches"] = True
    assert main(args) == 0
    assert "development-only" in capsys.readouterr().out
    original = output.read_bytes()
    assert main(args) == 1
    assert "already exists" in capsys.readouterr().out
    assert output.read_bytes() == original
