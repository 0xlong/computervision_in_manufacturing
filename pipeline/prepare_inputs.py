"""Create a checked evaluator manifest and a separate answer-free pixel package.

Source bytes remain unchanged. Model PNGs are re-encoded RGB pixels without source
metadata. This is development preparation, not a frozen benchmark/public bundle.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image

from pipeline.audit_mvtec_ad_directory import audit_directory
from pipeline.contracts import ImageManifest, MANIFEST_SCHEMA_V2, verify_assets
from pipeline.inventory_mvtec_ad import InventoryError
from pipeline.plan_preparation import build_plan, validate_plan
from pipeline.review_preparation import checked_image


def write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def prepare(root: Path, plan: dict, acquisition: dict, out: Path, *, require_summary: bool = True) -> dict:
    if root.is_symlink() or root.is_junction():
        raise InventoryError("Select a real source directory")
    root = root.resolve(strict=True)
    if out.exists() or out.resolve().is_relative_to(root):
        raise InventoryError("Choose a new output directory outside source data")
    validate_plan(plan)
    audit = audit_directory(root)
    if require_summary and not audit["published_summary_matches"]:
        raise InventoryError("Resolve published category summary mismatch first")
    if build_plan(root, audit) != plan:
        raise InventoryError("Preparation plan is stale")
    if acquisition["content_membership_sha256"] != audit["membership_sha256"]:
        raise InventoryError("Acquisition content fingerprint does not match audited data")
    by_member = {i["source_member"]: i for i in audit["images"]}
    dataset = {
        "dataset_id": "mvtec_ad", "category": "metal_nut",
        "source_url": "https://www.mvtec.com/research-teaching/datasets/mvtec-ad",
        "licence": "CC-BY-NC-SA-4.0",
        "licence_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "attribution": "MVTec Software GmbH, MVTec AD metal_nut; included source notices retained.",
        "modification_notice": "Evaluator display/masks use unchanged source bytes. Separate model inputs re-encode unchanged RGB pixels without metadata.",
        "acquisition": deepcopy(acquisition),
    }
    manifest = {"schema_version": 2, "manifest_id": "metal-nut-development-v2",
                "evidence_status": "development_only", "track_id": "fasteners",
                "dataset": dataset, "images": []}
    for item in plan["images"]:
        source = by_member[item["source_member"]]
        def asset(s: dict, path: str) -> dict:
            return {"path": path, "sha256": s["sha256"], "dimensions": s["dimensions"]}
        mask = source["mask"]
        manifest["images"].append({
            "image_id": item["image_id"], "track_id": "fasteners", "split": item["split"],
            "official_split": item["official_split"], "source_member": item["source_member"],
            "source_sha256": item["source_sha256"], "original_dimensions": source["dimensions"],
            "display": asset(source, f"images/{item['image_id']}.png"), "label": source["label"],
            "mask": asset(mask, f"masks/{item['image_id']}.png") if mask else None,
            "transform": deepcopy(MANIFEST_SCHEMA_V2["$defs"]["image"]["properties"]["transform"]["const"]),
        })
    validated = ImageManifest.model_validate(manifest)  # Fail before creating output.
    out.mkdir(parents=True, exist_ok=False)
    evaluator, model_root = out / "evaluator", out / "model-inputs"
    for directory in (evaluator / "images", evaluator / "masks", model_root / "images"):
        directory.mkdir(parents=True)
    inputs = {split: {"schema_version": 1, "evidence_status": "development_only", "images": []}
              for split in ("fitting", "calibration", "evaluation")}
    for item in manifest["images"]:
        source = by_member[item["source_member"]]
        pixels = checked_image(root, item["source_member"], item["source_sha256"])
        # Copy original encoded assets only to evaluator space, then verify them.
        (evaluator / item["display"]["path"]).write_bytes((root / item["source_member"]).read_bytes())
        if source["mask"]:
            m = source["mask"]
            checked_image(root, m["source_member"], m["sha256"])
            (evaluator / item["mask"]["path"]).write_bytes((root / m["source_member"]).read_bytes())
        clean = Image.frombytes("RGB", pixels.size, pixels.tobytes())
        name = f"images/{item['image_id']}.png"
        clean.save(model_root / name)
        content = (model_root / name).read_bytes()
        with Image.open(model_root / name) as decoded:
            decoded.load()
            if decoded.info or decoded.tobytes() != pixels.tobytes():
                raise InventoryError("Answer-free pixel export failed verification")
        inputs[item["split"]]["images"].append({"image_id": item["image_id"], "path": name,
            "sha256": sha256(content).hexdigest(), "dimensions": item["original_dimensions"]})
    verify_assets(validated, evaluator)
    write_json(evaluator / "image-manifest.v2.json", manifest)
    from pipeline.model_inputs import validate_inputs
    for split, index in inputs.items():
        validate_inputs(index, model_root)
        write_json(model_root / f"{split}.json", index)
    # Notices are evaluator/publication metadata, never inference context.
    for notice in audit["other_files"]:
        name = notice["source_member"]
        path = root / name
        if path.is_symlink() or path.is_junction() or not path.resolve(strict=True).is_relative_to(root):
            raise InventoryError("Source notice must remain a contained file")
        content = path.read_bytes()
        if sha256(content).hexdigest() != notice["sha256"]:
            raise InventoryError("Source notice changed after audit")
        destination = evaluator / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    summary = {"evidence_status": "development_only", "input_membership_sha256": audit["membership_sha256"],
        "manifest_sha256": sha256((evaluator / "image-manifest.v2.json").read_bytes()).hexdigest(),
        "indexes": {s: {"count": len(v["images"]), "sha256": sha256((model_root / f"{s}.json").read_bytes()).hexdigest()}
                    for s, v in inputs.items()},
        "limitations": ["Preparation groups remain provisional; physical-object identity unresolved.",
            "Unknown acquisition details are not recovered by exporting.",
            "No selected model resolution, normalization, model outputs or final evaluation.",
            "Inference must read only model-inputs; evaluator metadata must stay separate."]}
    write_json(out / "preparation.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--acquisition", type=Path, required=True, help="Explicit v2 acquisition object; no inferred dates/hashes")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = prepare(args.directory, json.loads(args.plan.read_text(encoding="utf-8")),
                         json.loads(args.acquisition.read_text(encoding="utf-8")), args.output_dir)
    except (OSError, ValueError, KeyError, SyntaxError):
        print("FAIL preparation: check plan, acquisition, source integrity and new output location; partial output may remain")
        return 1
    print("PASS development-only answer-free export: " + str({s: i["count"] for s, i in report["indexes"].items()}))
    print("Evaluator labels/masks are separate. Split freeze, official acquisition and model feasibility remain unverified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
