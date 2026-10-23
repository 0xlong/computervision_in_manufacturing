"""Create local, development-only picture review sheets; never decide alignment automatically."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from io import BytesIO
from itertools import combinations
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat, __version__ as pillow_version

from pipeline.audit_mvtec_ad_directory import audit_directory
from pipeline.inventory_mvtec_ad import InventoryError
from pipeline.plan_preparation import build_plan, validate_plan


METHOD = {
    "thumbnail": "RGB to L, then 32x32 LANCZOS; no rotation, crop or registration",
    "distance": "Mean absolute grayscale difference, range 0..255; lower is closer",
    "selection": "All pairs with distance <= 6, plus 12 closest pairs for each distinct split boundary",
    "threshold": 6, "boundary_count": 12,
    "sheet": "Original beside mask overlay; 350x350 LANCZOS image, NEAREST mask",
    "overlay": "25% RGB(255,0,160) fill; RGB(255,255,0) inner edge from mask minus 3x3 minimum filter",
}


def checked_image(root: Path, member: str, expected_hash: str) -> Image.Image:
    """Read only audited category files; decode the bytes whose hash was checked."""
    path = root / member
    if path.is_symlink() or path.is_junction() or not path.resolve(strict=True).is_relative_to(root):
        raise InventoryError("Review image must remain a contained regular file")
    content = path.read_bytes()
    if sha256(content).hexdigest() != expected_hash:
        raise InventoryError("Source changed after audit; regenerate the review")
    with Image.open(BytesIO(content), formats=["PNG"]) as image:
        image.load()
        return image.copy()


def related_pairs(images: list[dict], thumbnails: dict[str, Image.Image]) -> tuple[list[dict], int]:
    """A bounded heuristic shortlist, not physical-object identity or a duplicate verdict."""
    pairs = []
    for left, right in combinations(sorted(images, key=lambda i: i["image_id"]), 2):
        distance = ImageStat.Stat(ImageChops.difference(
            thumbnails[left["image_id"]], thumbnails[right["image_id"]])).mean[0]
        pairs.append({"left": left["image_id"], "right": right["image_id"],
                      "distance": distance,
                      "boundary": sorted({left["split"], right["split"]})})
    pairs.sort(key=lambda p: (p["distance"], p["left"], p["right"]))
    counts = Counter()
    selected = []
    for pair in pairs:
        boundary = tuple(pair["boundary"])
        rank = counts[boundary]
        counts[boundary] += 1
        if pair["distance"] <= METHOD["threshold"] or (
                len(boundary) == 2 and rank < METHOD["boundary_count"]):
            selected.append(pair)
    return selected, len(pairs)


def overlay(image: Image.Image, mask: Image.Image) -> Image.Image:
    """Render the reference in the same coordinates; no geometric adjustment."""
    if image.size != mask.size or mask.mode != "L":
        raise InventoryError("Overlay needs a same-sized grayscale mask")
    if set(mask.get_flattened_data()) - {0, 255} or not mask.getbbox():
        raise InventoryError("Overlay needs a nonempty binary mask")
    fill = Image.new("RGB", image.size, (255, 0, 160))
    result = Image.composite(Image.blend(image.convert("RGB"), fill, 0.25), image, mask)
    edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(3)))
    result.paste((255, 255, 0), mask=edge)
    return result


def save_sheets(rows: list[tuple[str, Image.Image, Image.Image]], prefix: str, out: Path) -> list[str]:
    """Four comparisons per sheet; original always on the left of its partner."""
    names = []
    for start in range(0, len(rows), 4):
        sheet = Image.new("RGB", (1440, 820), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text((10, 5), f"DEVELOPMENT REVIEW / {prefix} / original LEFT / comparison RIGHT", fill="black")
        for index, (label, left, right) in enumerate(rows[start:start + 4]):
            x, y = (index % 2) * 720 + 5, (index // 2) * 395 + 28
            draw.text((x, y), label, fill="black")
            sheet.paste(left.resize((350, 350), Image.Resampling.LANCZOS), (x, y + 28))
            sheet.paste(right.resize((350, 350), Image.Resampling.LANCZOS), (x + 355, y + 28))
        name = f"{prefix}-{start // 4 + 1:03d}.png"
        sheet.save(out / name)
        names.append(name)
    return names


def generate_review(root: Path, plan: dict, out: Path) -> dict:
    if root.is_symlink() or root.is_junction():
        raise InventoryError("Select a real category directory, not a link or junction")
    root = root.resolve(strict=True)
    if out.resolve().is_relative_to(root):
        raise InventoryError("Review output must be outside the source dataset")
    if out.exists():
        raise InventoryError("Review output already exists; choose a new directory")
    validate_plan(plan)
    audit = audit_directory(root)
    if build_plan(root, audit) != plan:
        raise InventoryError("Saved preparation plan does not match the current dataset")
    records = {i["image_id"]: i for i in plan["images"]}
    audited = {i["source_member"]: i for i in audit["images"]}
    thumbnails = {}
    for item in plan["images"]:
        image = checked_image(root, item["source_member"], item["source_sha256"])
        thumbnails[item["image_id"]] = image.convert("L").resize((32, 32), Image.Resampling.LANCZOS)
    candidates, pair_count = related_pairs(plan["images"], thumbnails)
    # Exclusive directory creation prevents replacing a previous review or source file.
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for index, pair in enumerate(candidates, 1):
        left, right = (records[pair[key]] for key in ("left", "right"))
        label = (f"P{index:03d} {left['source_member']} [{left['split']}]\n"
                 f"vs {right['source_member']} [{right['split']}] MAE={pair['distance']:.4f}")
        rows.append((label, *(checked_image(root, i["source_member"], i["source_sha256"])
                              .resize((350, 350), Image.Resampling.LANCZOS) for i in (left, right))))
        pair["pair_id"] = f"P{index:03d}"
        pair["review_status"] = "pending_visual_review"
    pair_sheets = save_sheets(rows, "related", out)
    mask_rows, masks = [], []
    for item in plan["images"]:
        source = audited[item["source_member"]]
        if not source.get("mask"):
            continue
        image = checked_image(root, item["source_member"], item["source_sha256"])
        m = source["mask"]
        mask = checked_image(root, m["source_member"], m["sha256"])
        # Resize mask separately with NEAREST, so generated colours cannot shift its geometry.
        small = image.resize((350, 350), Image.Resampling.LANCZOS)
        small_mask = mask.resize((350, 350), Image.Resampling.NEAREST)
        rendered = overlay(small, small_mask)
        label = f"{item['image_id']} {item['source_member']}\nReference mask: pink fill / yellow edge; NOT an AI result"
        mask_rows.append((label, small, rendered))
        masks.append({"image_id": item["image_id"], "source_member": item["source_member"],
                      "mask_member": m["source_member"], "mask_sha256": m["sha256"],
                      "nonzero_pixels": m["nonzero_pixels"], "bbox_xyxy": list(mask.getbbox()),
                      "review_status": "pending_visual_review",
                      "nearest_mask_pixels": {str(size): mask.resize((size, size), Image.Resampling.NEAREST)
                          .histogram()[255] for size in (256, 384, 512)}})
    mask_sheets = save_sheets(mask_rows, "masks", out)
    report = {"review_version": 1, "evidence_status": "development_only",
              "input_membership_sha256": audit["membership_sha256"],
              "plan_canonical_sha256": sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
              "decoder": {"name": "Pillow", "version": pillow_version},
              "method": METHOD, "all_pair_count": pair_count, "candidates": candidates,
              "masks": masks, "sheets": pair_sheets + mask_sheets,
              "limitations": ["Visual decisions are recorded separately; generating sheets proves no alignment.",
                  "Similarity shortlist can miss rotated, cropped, relit or otherwise related pictures.",
                  "Similar manufactured objects do not establish the same physical object or acquisition session.",
                  "Downsampled mask survival does not prove that an AI model can see a defect.",
                  "No source images, split membership, acquisition facts or model evidence are changed."]}
    report["sheet_sha256"] = {name: sha256((out / name).read_bytes()).hexdigest() for name in report["sheets"]}
    (out / "review.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        report = generate_review(args.directory, plan, args.output_dir)
    except InventoryError as error:
        print(f"FAIL preparation review: {error}")
        return 1
    except (OSError, ValueError, SyntaxError, EOFError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        print("FAIL preparation review: cannot read checked inputs or write new review; incomplete output may remain")
        return 1
    print(f"CREATED development-only review: {len(report['candidates'])} related-picture candidates; {len(report['masks'])} masks")
    print("Visual review is pending. No model result, split change or source modification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
