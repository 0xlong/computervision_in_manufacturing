"""Generated pictures check the review aid, never real annotation correctness."""

from copy import deepcopy
from hashlib import sha256
import json

from PIL import Image
import pytest

from pipeline.audit_mvtec_ad_directory import audit_directory
from pipeline.inventory_mvtec_ad import InventoryError
from pipeline.plan_preparation import build_plan
from pipeline.review_preparation import generate_review, main, overlay, related_pairs


@pytest.fixture
def sample(tmp_path):
    root = tmp_path / "fixture"
    for number in range(10):
        path = root / f"train/good/{number:03d}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (16, 16), (number * 20, 40, 20)).save(path)
    for member, mode, value in (("test/good/000.png", "RGB", (0, 90, 0)),
            ("test/scratch/000.png", "RGB", (0, 120, 0)),
            ("ground_truth/scratch/000_mask.png", "L", 0)):
        path = root / member
        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new(mode, (16, 16), value)
        if mode == "L":
            image.paste(255, (8, 3, 12, 7))
        image.save(path)
    return root, build_plan(root, audit_directory(root))


def test_overlay_preserves_original_background_and_marks_known_coordinates():
    original = Image.new("RGB", (16, 16), (40, 60, 80))
    mask = Image.new("L", original.size)
    mask.paste(255, (8, 3, 12, 7))
    result = overlay(original, mask)
    assert result.getpixel((8, 3)) == (255, 255, 0)
    assert result.getpixel((9, 4)) != original.getpixel((9, 4))
    assert result.getpixel((7, 3)) == original.getpixel((7, 3))
    assert original.getpixel((8, 3)) == (40, 60, 80)
    assert mask.getbbox() == (8, 3, 12, 7)


@pytest.mark.parametrize("mode,size,value", [("L", (8, 8), 255), ("RGB", (16, 16), 255),
                                               ("L", (16, 16), 10), ("L", (16, 16), 0)])
def test_bad_masks_fail(mode, size, value):
    with pytest.raises(InventoryError):
        overlay(Image.new("RGB", (16, 16)), Image.new(mode, size, value))


def test_shortlist_includes_close_same_split_and_distant_boundary_and_is_stable():
    items = [{"image_id": f"img-{n:06d}", "split": split} for n, split in
             ((1, "fitting"), (2, "fitting"), (3, "calibration"), (4, "evaluation"))]
    thumbs = {item["image_id"]: Image.new("L", (32, 32), value)
              for item, value in zip(items, (0, 1, 100, 240))}
    pairs, count = related_pairs(items, thumbs)
    assert count == 6 and len(pairs) == 6
    assert pairs[0]["distance"] == 1
    assert pairs[0]["boundary"] == ["fitting"]
    assert any(p["distance"] > 6 and len(p["boundary"]) == 2 for p in pairs)
    assert related_pairs(items[::-1], thumbs) == (pairs, count)


def test_generated_review_is_repeatable_complete_and_leaves_sources_unchanged(sample, tmp_path):
    root, plan = sample
    before = {p.relative_to(root): sha256(p.read_bytes()).hexdigest() for p in root.rglob("*.png")}
    first = generate_review(root, plan, tmp_path / "first")
    second = generate_review(root, plan, tmp_path / "second")
    assert first == second
    assert first["all_pair_count"] == 66
    assert len(first["masks"]) == 1
    assert first["masks"][0]["bbox_xyxy"] == [8, 3, 12, 7]
    assert first["masks"][0]["nearest_mask_pixels"]["256"] == 4096
    assert all(i["review_status"] == "pending_visual_review" for i in first["masks"] + first["candidates"])
    assert str(root) not in json.dumps(first)
    for name in first["sheets"]:
        assert sha256((tmp_path / "first" / name).read_bytes()).hexdigest() == first["sheet_sha256"][name]
        with Image.open(tmp_path / "first" / name) as sheet:
            assert sheet.size == (1440, 820)
    assert before == {p.relative_to(root): sha256(p.read_bytes()).hexdigest() for p in root.rglob("*.png")}


def test_existing_outputs_and_source_output_locations_are_refused(sample, tmp_path):
    root, plan = sample
    out = tmp_path / "previous"
    out.mkdir()
    (out / "review.json").write_text("KEEP TEST ONLY")
    with pytest.raises(InventoryError, match="already exists"):
        generate_review(root, plan, out)
    assert (out / "review.json").read_text() == "KEEP TEST ONLY"
    with pytest.raises(InventoryError, match="outside"):
        generate_review(root, plan, root / "new-review")
    assert not (root / "new-review").exists()


@pytest.mark.parametrize("change", ["plan", "image", "mask"])
def test_stale_or_modified_inputs_fail_before_output(sample, tmp_path, change):
    root, plan = sample
    plan = deepcopy(plan)
    if change == "plan":
        plan["input_membership_sha256"] = "0" * 64
    elif change == "image":
        Image.new("RGB", (16, 16), (10, 20, 30)).save(root / "train/good/000.png")
    else:
        mask = Image.new("L", (16, 16))
        mask.paste(255, (0, 0, 2, 2))
        mask.save(root / "ground_truth/scratch/000_mask.png")
    with pytest.raises(InventoryError, match="does not match"):
        generate_review(root, plan, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_cli_reports_pending_visual_review_and_preserves_output(sample, tmp_path, capsys):
    root, plan = sample
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan))
    args = [str(root), "--plan", str(path), "--output-dir", str(tmp_path / "out")]
    assert main(args) == 0
    assert "Visual review is pending" in capsys.readouterr().out
    assert main(args) == 1
    assert "already exists" in capsys.readouterr().out
    path.write_text("TEST ONLY invalid JSON")
    assert main(args) == 1
    assert str(root) not in capsys.readouterr().out
