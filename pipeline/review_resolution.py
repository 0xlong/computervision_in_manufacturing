"""Measure mask resizing and create a bounded RGB review, never model-quality evidence.

Evaluator-only: reads reference masks, not used by specialist/provider runners.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image, ImageDraw, __version__ as pillow_version

from pipeline.audit_mvtec_ad_directory import audit_directory
from pipeline.inventory_mvtec_ad import InventoryError
from pipeline.plan_preparation import build_plan, validate_plan
from pipeline.review_preparation import checked_image


SIZES = (256, 384, 512)
RESIZE = "Pillow BILINEAR, full frame, square; no crop/padding/rotation"


def mask_measurement(mask: Image.Image, size: int) -> dict:
    """Measure reference geometry only; a surviving mask is not visible RGB detail."""
    if mask.mode != "L" or set(mask.get_flattened_data()) - {0, 255} or not mask.getbbox():
        raise InventoryError("Resolution review needs a nonempty binary reference mask")
    small = mask.resize((size, size), Image.Resampling.NEAREST)
    bbox = small.getbbox()
    return {"nonzero_pixels": small.histogram()[255],
            "bbox_xyxy": list(bbox) if bbox else None,
            "input_to_source": {"x_scale": mask.width / size, "y_scale": mask.height / size,
                                "offset_px": [0, 0]}}


def comparison_sheet(image: Image.Image, size: int, image_id: str) -> tuple[Image.Image, Image.Image]:
    """Keep original pixels and enlarge the exact model RGB resize using NEAREST.

    Enlargement is a viewing aid, not extra detail. No reference marks obscure RGB.
    """
    small = image.resize((size, size), Image.Resampling.BILINEAR)
    sheet = Image.new("RGB", (image.width * 2 + 5, image.height + 55), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((5, 4), f"DEVELOPMENT / {image_id} / RGB visibility only; NOT an AI result", fill="black")
    draw.text((5, 23), f"Original {image.width}x{image.height}", fill="black")
    draw.text((image.width + 10, 23), f"{size}x{size} BILINEAR; NEAREST enlarged for viewing", fill="black")
    sheet.paste(image, (0, 55))
    sheet.paste(small.resize(image.size, Image.Resampling.NEAREST), (image.width + 5, 55))
    return small, sheet


def generate_resolution_review(root: Path, plan: dict, config_path: Path,
                               selected_ids: list[str], out: Path) -> dict:
    if root.is_symlink() or root.is_junction():
        raise InventoryError("Select a real category directory, not a link or junction")
    root = root.resolve(strict=True)
    if out.resolve().is_relative_to(root):
        raise InventoryError("Resolution output must be outside the source dataset")
    if out.exists():
        raise InventoryError("Resolution output already exists; choose a new directory")
    if not 1 <= len(selected_ids) <= 2 or len(set(selected_ids)) != len(selected_ids):
        raise InventoryError("Select one or two distinct anomalous image IDs (two views each)")
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    if (config.get("schema_version") != 1 or type(config.get("input_size_px")) is not int
            or config["input_size_px"] not in SIZES or config.get("resize") != RESIZE):
        raise InventoryError("Unsupported specialist resize configuration")
    size = config["input_size_px"]
    validate_plan(plan)
    audit = audit_directory(root)
    if build_plan(root, audit) != plan:
        raise InventoryError("Saved preparation plan does not match the current dataset")
    records = {i["image_id"]: i for i in plan["images"]}
    audited = {i["source_member"]: i for i in audit["images"]}
    if any(image_id not in records or not audited[records[image_id]["source_member"]].get("mask")
           for image_id in selected_ids):
        raise InventoryError("Selected IDs must identify audited anomalous images")
    # Recheck bytes against the fresh audit before decoding; no source writes.
    masks = []
    for item in plan["images"]:
        source = audited[item["source_member"]]
        reference = source.get("mask")
        if not reference:
            continue
        mask = checked_image(root, reference["source_member"], reference["sha256"])
        masks.append({"image_id": item["image_id"], "source_member": item["source_member"],
            "source_sha256": item["source_sha256"], "mask_sha256": reference["sha256"],
            "source_dimensions_px": list(mask.size), "source_nonzero_pixels": mask.histogram()[255],
            "sizes": {str(s): mask_measurement(mask, s) for s in SIZES}})
    selected = []
    for image_id in selected_ids:
        item = records[image_id]
        image = checked_image(root, item["source_member"], item["source_sha256"])
        small, sheet = comparison_sheet(image, size, image_id)
        selected.append((image_id, small, sheet))
    # Exclusive creation prevents replacement of previous evidence. Failures may
    # leave partial output; review.json is written only after all PNGs succeed.
    out.mkdir(parents=True, exist_ok=False)
    assets = {}
    for image_id, small, sheet in selected:
        for name, image in ((f"{image_id}-input-{size}.png", small), (f"{image_id}-comparison.png", sheet)):
            image.save(out / name)
            assets[name] = sha256((out / name).read_bytes()).hexdigest()
    report = {"review_version": 1, "evidence_status": "development_only_evaluator_review",
        "input_membership_sha256": audit["membership_sha256"],
        "plan_canonical_sha256": sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "specialist_config_sha256": sha256(config_bytes).hexdigest(),
        "decoder": {"name": "Pillow", "version": pillow_version},
        "method": {"rgb_resize": RESIZE, "input_size_px": size, "mask_resize": "Pillow NEAREST",
            "mask_sizes_px": list(SIZES), "sheet_enlargement": "NEAREST to original dimensions; no added detail",
            "coordinates": "Continuous image edges: source = input * scale; pixel centers: (input + 0.5) * scale - 0.5",
            "normalization": "RGB before tensor /255 and channel normalization; spatial detail only"},
        "masks": masks, "selected_image_ids": selected_ids,
        "visual_review_status": "pending_separate_observations", "displayed_example_count": len(selected_ids) * 2,
        "asset_sha256": assets,
        "limitations": ["Mask survival does not prove RGB visibility, survival of every small component, or model detection.",
            "Only selected comparisons may be visually inspected; this is not dataset-wide visual certification.",
            "No model inference, score, calibration, threshold or final configuration selection is performed.",
            "Reference masks are evaluator-only; this report must never be inference input.",
            "Provisional splits, unknown object/session identity and acquisition limitations are unchanged."]}
    (out / "review.json").write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--image-id", action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        report = generate_resolution_review(args.directory, plan, args.config, args.image_id, args.output_dir)
    except InventoryError as error:
        print(f"FAIL resolution review: {error}")
        return 1
    except (OSError, ValueError, TypeError, AttributeError, SyntaxError, EOFError,
            Image.DecompressionBombWarning, Image.DecompressionBombError):
        print("FAIL resolution review: cannot read checked inputs or write new review; incomplete output may remain")
        return 1
    print(f"CREATED development-only resolution review: {len(report['masks'])} masks; {report['displayed_example_count']} displayed examples")
    print("RGB visual review is pending. No model-quality result or frozen resolution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
