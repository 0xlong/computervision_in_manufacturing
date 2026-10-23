"""Follow up the saved preparation-boundary risks with bounded image registration.

No new visual sheets and no identity verdicts. Similarity cannot recover part IDs.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import sqrt
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageStat, __version__ as pillow_version

from pipeline.audit_mvtec_ad_directory import audit_directory
from pipeline.inventory_mvtec_ad import InventoryError
from pipeline.plan_preparation import build_plan, validate_plan
from pipeline.prepare_inputs import write_json
from pipeline.review_preparation import checked_image, related_pairs


def overlap(a: Image.Image, b: Image.Image, dx: int, dy: int) -> tuple[Image.Image, Image.Image]:
    """Compare shared valid pixels only; never wrap padded pixels into the score."""
    w, h = a.size
    left, top, right, bottom = max(0, dx), max(0, dy), min(w, w + dx), min(h, h + dy)
    return a.crop((left, top, right, bottom)), b.crop((left-dx, top-dy, right-dx, bottom-dy))


def correlation(a: Image.Image, b: Image.Image) -> float | None:
    count = a.width * a.height
    ma, mb = ImageStat.Stat(a).mean[0], ImageStat.Stat(b).mean[0]
    va, vb = ImageStat.Stat(a).var[0], ImageStat.Stat(b).var[0]
    if min(va, vb) < 1e-8:
        return None
    # Python integer accumulation avoids Pillow multiply's 8-bit clipping.
    product = sum(x*y for x, y in zip(a.get_flattened_data(), b.get_flattened_data())) / count
    return max(-1.0, min(1.0, (product-ma*mb) / sqrt(va*vb)))


def compare(a: Image.Image, b: Image.Image) -> dict:
    if a.size != b.size:
        raise InventoryError("Comparison requires equal dimensions")
    # Bounded coarse rigid search. The inner crop avoids rotation fill and background.
    size = 128
    small_a = a.convert("L").resize((size, size), Image.Resampling.LANCZOS)
    small_b = b.convert("L").resize((size, size), Image.Resampling.LANCZOS)
    crop = (20, 20, 108, 108)
    best = None
    for angle in (-4, -2, 0, 2, 4):
        rotated = small_b.rotate(angle, Image.Resampling.BICUBIC)
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                aa = small_a.crop(crop)
                bb = rotated.crop((20-dx, 20-dy, 108-dx, 108-dy))
                score = correlation(aa, bb)
                key = (-(score if score is not None else -2), abs(angle), abs(dx)+abs(dy), angle, dx, dy)
                if best is None or key < best[0]:
                    best = (key, angle, dx, dy, score)
    _, angle, dx, dy, coarse = best
    ga, gb = a.convert("L"), b.convert("L").rotate(angle, Image.Resampling.BICUBIC)
    dx, dy = round(dx*a.width/size), round(dy*a.height/size)
    ga, gb = overlap(ga, gb, dx, dy)
    # Same central full-resolution crop for both; no selection using model results.
    margin_x, margin_y = ga.width//6, ga.height//6
    box = (margin_x, margin_y, ga.width-margin_x, ga.height-margin_y)
    ga, gb = ga.crop(box), gb.crop(box)
    # FIND_EDGES removes broad illumination changes; it cannot prove object identity.
    ea, eb = ga.filter(ImageFilter.FIND_EDGES), gb.filter(ImageFilter.FIND_EDGES)
    inner = (2, 2, ea.width-2, ea.height-2)
    if min(ea.size) <= 4:
        raise InventoryError("Comparison images are too small")
    ea, eb = ea.crop(inner), eb.crop(inner)
    return {"rotation_deg": angle, "translation_source_px": [dx, dy],
            "coarse_gray_correlation": coarse, "native_gray_correlation": correlation(ga, gb),
            "native_edge_correlation": correlation(ea, eb),
            "native_gray_mae": ImageStat.Stat(ImageChops.difference(ga, gb)).mean[0],
            "compared_detail_pixels": ea.width*ea.height,
            "search_boundary_hit": abs(angle) == 4 or abs(best[2]) == 4 or abs(best[3]) == 4}


def follow_up(root: Path, plan: dict, review: dict) -> dict:
    validate_plan(plan)
    if root.is_symlink() or root.is_junction():
        raise InventoryError("Select a real source directory")
    root = root.resolve(strict=True)
    audit = audit_directory(root)
    if build_plan(root, audit) != plan or review["input_membership_sha256"] != audit["membership_sha256"]:
        raise InventoryError("Saved inputs are stale")
    canonical = sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if review["plan_canonical_sha256"] != canonical:
        raise InventoryError("Review does not refer to this plan")
    records = {i["image_id"]: i for i in plan["images"]}
    # Recreate the entire shortlist so tampered/omitted pairs cannot pass unnoticed.
    thumbs = {key: checked_image(root, i["source_member"], i["source_sha256"])
              .convert("L").resize((32,32), Image.Resampling.LANCZOS) for key, i in records.items()}
    candidates, count = related_pairs(plan["images"], thumbs)
    expected = [{**p, "pair_id": f"P{n:03d}", "review_status": "pending_visual_review"}
                for n, p in enumerate(candidates, 1)]
    if review["candidates"] != expected or review["all_pair_count"] != count:
        raise InventoryError("Review shortlist no longer matches audited inputs")
    results = []
    for pair in expected:
        if pair["boundary"] != ["calibration", "fitting"]:
            continue
        a, b = (checked_image(root, records[pair[k]]["source_member"], records[pair[k]]["source_sha256"])
                for k in ("left", "right"))
        measured = compare(a, b)
        # A same-photo positive control exercises every pair's search at its own scale.
        shifted = ImageChops.offset(a, round(a.width/128), -round(a.height/128))
        control = compare(a, shifted)
        results.append({"pair_id": pair["pair_id"], "left": pair["left"], "right": pair["right"],
                        "measurement": measured, "same_photo_shift_control": control,
                        "identity_status": "unresolved"})
    return {"comparison_version": 1, "evidence_status": "development_only",
        "input_membership_sha256": audit["membership_sha256"], "plan_canonical_sha256": canonical,
        "pillow_version": pillow_version, "results": results,
        "method": {"registration": "128px grayscale NCC; rotations -4,-2,0,2,4 degrees; x/y shifts -4..4 pixels; central 88px crop",
            "detail": "Apply best rigid transform at source size; common overlap; central two-thirds crop; grayscale and FIND_EDGES correlations",
            "selection": "Only saved fitting/calibration boundary risks; no evaluation labels, masks or predictions used",
            "controls": "Each left image shifted by one coarse pixel in x/-y; wrap exists only outside scored central crop"},
        "freeze_status": "blocked_by_unresolved_related_object_risk",
        "limitations": ["Bounded rigid registration misses scale, perspective, larger rotation, deformation and relighting.",
            "High correlation is not a physical-object identifier; low correlation cannot rule out a related object.",
            "No groups are confirmed and no seed-42 membership changed. Official test images remain intact.",
            "No new images were viewed. Existing visual findings remain separate."]}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", type=Path)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--review", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        if args.output.exists() or args.output.resolve().is_relative_to(args.directory.resolve()):
            raise InventoryError("Choose new output outside source data")
        report = follow_up(args.directory, json.loads(args.plan.read_text(encoding="utf-8")),
                           json.loads(args.review.read_text(encoding="utf-8")))
        write_json(args.output, report)
    except (OSError, ValueError, KeyError):
        print("FAIL similarity follow-up: check saved inputs and new output location")
        return 1
    print(f"MEASURED {len(report['results'])} boundary risks; physical-object identity unresolved; split NOT frozen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
