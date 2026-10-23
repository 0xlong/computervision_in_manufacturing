"""Generated images test resize evidence; real visibility needs separate observations."""

from copy import deepcopy
from hashlib import sha256
import json

from PIL import Image
import pytest

from pipeline.audit_mvtec_ad_directory import audit_directory
from pipeline.inventory_mvtec_ad import InventoryError
from pipeline.plan_preparation import build_plan
from pipeline.review_resolution import RESIZE, comparison_sheet, generate_resolution_review, main, mask_measurement


@pytest.fixture
def sample(tmp_path):
    root = tmp_path / "fixture"
    for n in range(10):
        path = root / f"train/good/{n:03d}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (16, 16), (n * 20, 40, 20)).save(path)
    for member, mode, color in (("test/good/000.png", "RGB", (0, 90, 0)),
            ("test/scratch/000.png", "RGB", (0, 120, 0)),
            ("ground_truth/scratch/000_mask.png", "L", 0)):
        path = root / member
        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new(mode, (16, 16), color)
        if mode == "L":
            image.paste(255, (8, 4, 12, 8))
        image.save(path)
    plan = build_plan(root, audit_directory(root))
    selected = next(i["image_id"] for i in plan["images"] if "scratch" in i["source_member"])
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"schema_version": 1, "input_size_px": 256, "resize": RESIZE}))
    return root, plan, config, selected


def test_known_mask_mapping_and_disappearing_small_region():
    mask = Image.new("L", (16, 8))
    mask.paste(255, (8, 2, 12, 6))
    result = mask_measurement(mask, 4)
    assert result == {"nonzero_pixels": 2, "bbox_xyxy": [2, 1, 3, 3],
        "input_to_source": {"x_scale": 4.0, "y_scale": 2.0, "offset_px": [0, 0]}}
    tiny = Image.new("L", (16, 16))
    tiny.putpixel((0, 0), 255)
    assert mask_measurement(tiny, 4)["nonzero_pixels"] == 0
    assert mask_measurement(tiny, 4)["bbox_xyxy"] is None


def test_sheet_uses_bilinear_pixels_and_explicit_nearest_viewing_enlargement():
    original = Image.new("RGB", (4, 4))
    original.paste((255, 255, 255), (2, 0, 4, 4))
    small, sheet = comparison_sheet(original, 2, "fixture")
    assert small.size == (2, 2)
    assert small.getpixel((0, 0)) == (36, 36, 36)
    assert small.getpixel((1, 0)) == (219, 219, 219)
    assert sheet.crop((0, 55, 4, 59)).tobytes() == original.tobytes()
    assert sheet.crop((9, 55, 13, 59)).tobytes() == small.resize((4, 4), Image.Resampling.NEAREST).tobytes()


@pytest.mark.parametrize("mode,value", [("RGB", 255), ("L", 3), ("L", 0)])
def test_invalid_masks_fail(mode, value):
    with pytest.raises(InventoryError, match="binary"):
        mask_measurement(Image.new(mode, (8, 8), value), 4)


def test_complete_repeatable_review_preserves_source_and_records_fingerprints(sample, tmp_path):
    root, plan, config, selected = sample
    before = {p.relative_to(root): sha256(p.read_bytes()).hexdigest() for p in root.rglob("*.png")}
    first = generate_resolution_review(root, plan, config, [selected], tmp_path / "one")
    second = generate_resolution_review(root, plan, config, [selected], tmp_path / "two")
    assert first == second
    assert len(first["masks"]) == 1
    assert first["masks"][0]["source_nonzero_pixels"] == 16
    assert first["masks"][0]["sizes"]["256"]["nonzero_pixels"] == 4096
    assert first["displayed_example_count"] == 2
    assert first["visual_review_status"] == "pending_separate_observations"
    assert first["evidence_status"] == "development_only_evaluator_review"
    assert first["specialist_config_sha256"] == sha256(config.read_bytes()).hexdigest()
    assert str(root) not in json.dumps(first)
    for name, digest in first["asset_sha256"].items():
        assert sha256((tmp_path / "one" / name).read_bytes()).hexdigest() == digest
    assert before == {p.relative_to(root): sha256(p.read_bytes()).hexdigest() for p in root.rglob("*.png")}


@pytest.mark.parametrize("change", ["plan", "image", "mask"])
def test_changed_inputs_rejected_before_output(sample, tmp_path, change):
    root, plan, config, selected = sample
    plan = deepcopy(plan)
    if change == "plan":
        plan["input_membership_sha256"] = "0" * 64
    elif change == "image":
        Image.new("RGB", (16, 16), (1, 2, 3)).save(root / "test/scratch/000.png")
    else:
        Image.new("L", (16, 16), 255).save(root / "ground_truth/scratch/000_mask.png")
    with pytest.raises(InventoryError, match="does not match"):
        generate_resolution_review(root, plan, config, [selected], tmp_path / "out")
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("selection", [[], ["unknown"], ["normal"], ["selected", "selected"], ["a", "b", "c"]])
def test_selection_is_bounded_and_requires_anomalous_ids(sample, tmp_path, selection):
    root, plan, config, selected = sample
    normal = next(i["image_id"] for i in plan["images"] if i["source_member"].startswith("train"))
    selection = [selected if i == "selected" else normal if i == "normal" else i for i in selection]
    with pytest.raises(InventoryError):
        generate_resolution_review(root, plan, config, selection, tmp_path / "out")
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("field,value", [("resize", "LANCZOS"), ("input_size_px", 100000),
                                         ("input_size_px", 256.0), ("schema_version", 2)])
def test_unsupported_resize_configuration_fails(sample, tmp_path, field, value):
    root, plan, config, selected = sample
    settings = json.loads(config.read_text())
    settings[field] = value
    config.write_text(json.dumps(settings))
    with pytest.raises(InventoryError, match="configuration"):
        generate_resolution_review(root, plan, config, [selected], tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_previous_output_and_source_output_are_preserved(sample, tmp_path):
    root, plan, config, selected = sample
    out = tmp_path / "previous"
    out.mkdir()
    (out / "keep.txt").write_text("fixture")
    with pytest.raises(InventoryError, match="already exists"):
        generate_resolution_review(root, plan, config, [selected], out)
    assert (out / "keep.txt").read_text() == "fixture"
    with pytest.raises(InventoryError, match="outside"):
        generate_resolution_review(root, plan, config, [selected], root / "out")
    assert not (root / "out").exists()


def test_cli_states_limits_and_handles_invalid_json_without_private_paths(sample, tmp_path, capsys):
    root, plan, config, selected = sample
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan))
    args = [str(root), "--plan", str(plan_path), "--config", str(config),
            "--image-id", selected, "--output-dir", str(tmp_path / "out")]
    assert main(args) == 0
    assert "No model-quality result or frozen resolution" in capsys.readouterr().out
    assert main(args) == 1
    config.write_text("not JSON")
    args[-1] = str(tmp_path / "new")
    assert main(args) == 1
    assert str(root) not in capsys.readouterr().out
