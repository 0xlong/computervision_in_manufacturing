"""Propose reproducible fastener preparation splits; never train or certify evidence."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import random
import re

from jsonschema import Draft202012Validator
from PIL import Image

from pipeline.audit_mvtec_ad_directory import audit_directory
from pipeline.inventory_mvtec_ad import InventoryError


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas/preparation-plan.v1.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)
METHOD = SCHEMA["properties"]["method"]["const"]


def validate_plan(plan: dict) -> None:
    error = next(VALIDATOR.iter_errors(plan), None)
    if error:
        raise InventoryError("Preparation plan violates its versioned schema")
    images = plan["images"]
    for field in ("image_id", "source_member"):
        values = [i[field].casefold() for i in images]
        if len(values) != len(set(values)):
            raise InventoryError("Duplicate image identity in preparation plan")
    for number, image in enumerate(sorted(images, key=lambda i: i["source_member"]), 1):
        if image["image_id"] != f"img-{number:06d}":
            raise InventoryError("Neutral IDs must follow stable sorted source membership")
        is_training_member = image["source_member"].startswith("train/good/")
        if is_training_member != (image["official_split"] == "train"):
            raise InventoryError("Official split does not match source membership")
    counts = Counter(i["split"] for i in images)
    if any(not counts[s] for s in ("fitting", "calibration", "evaluation")):
        raise InventoryError("Preparation groups and evaluation must each be nonempty")
    training = sorted(i["image_id"] for i in images if i["official_split"] == "train")
    random.Random(42).shuffle(training)
    # Exact integer ceil(n/5), avoiding floating-point rounding at integer boundaries.
    calibration = set(training[:(len(training) + 4) // 5])
    actual = {i["image_id"] for i in images if i["split"] == "calibration"}
    if actual != calibration:
        raise InventoryError("Calibration membership does not match the seeded holdout rule")
    for key in ("source_sha256", "pixel_sha256"):
        fitting = {i[key] for i in images if i["split"] == "fitting"}
        held_out = {i[key] for i in images if i["split"] == "calibration"}
        if fitting & held_out:
            raise InventoryError("Identical images cross preparation groups; group-aware review is required")
    preparation = {i["pixel_sha256"] for i in images if i["official_split"] == "train"}
    overlap = sorted(i["image_id"] for i in images
                     if i["split"] == "evaluation" and i["pixel_sha256"] in preparation)
    if plan["evaluation_overlap_ids"] != overlap:
        raise InventoryError("Evaluation overlap must be reported without removing test images")


def build_plan(root: Path, audit: dict) -> dict:
    """Consume an in-memory local audit; recheck bytes before pixel fingerprints.

    Production use obtains the audit from audit_directory, not arbitrary JSON.
    Exact duplicate groups that would cross the fixed split cause an explicit
    failure, never a silent move/drop. Related-image review remains separate.
    """
    root = root.resolve(strict=True)
    images = []
    for number, item in enumerate(sorted(audit["images"], key=lambda i: i["source_member"]), 1):
        if not re.fullmatch(SCHEMA["$defs"]["image"]["properties"]["source_member"]["pattern"], item["source_member"]):
            raise InventoryError("Unexpected source image path in preparation audit")
        path = root / item["source_member"]
        if path.is_symlink() or path.is_junction() or not path.resolve(strict=True).is_relative_to(root):
            raise InventoryError("Image must remain a contained regular file")
        content = path.read_bytes()
        if sha256(content).hexdigest() != item["sha256"]:
            raise InventoryError("Image changed after the directory audit")
        # Decode the very bytes just checked, without re-opening a changing path.
        with Image.open(BytesIO(content), formats=["PNG"]) as image:
            image.load()
            if image.mode != "RGB":
                raise InventoryError("Preparation pixel audit currently requires RGB photographs")
            header = f"RGB:{image.width}:{image.height}:".encode("ascii")
            pixel_hash = sha256(header + image.tobytes()).hexdigest()
        images.append({
            "image_id": f"img-{number:06d}", "source_member": item["source_member"],
            "source_sha256": item["sha256"], "pixel_sha256": pixel_hash,
            "official_split": "train" if item["official_split"] == "train" else "test_public",
            "split": "fitting" if item["official_split"] == "train" else "evaluation",
        })
    train_ids = sorted(i["image_id"] for i in images if i["official_split"] == "train")
    random.Random(42).shuffle(train_ids)
    calibration_ids = set(train_ids[:(len(train_ids) + 4) // 5])
    for item in images:
        if item["image_id"] in calibration_ids:
            item["split"] = "calibration"
    preparation_hashes = {i["pixel_sha256"] for i in images if i["official_split"] == "train"}
    plan = {
        "schema_version": 1, "evidence_status": "development_only", "track_id": "fasteners",
        "input_membership_sha256": audit["membership_sha256"], "method": deepcopy(METHOD),
        "images": images,
        "evaluation_overlap_ids": sorted(i["image_id"] for i in images if i["split"] == "evaluation"
                                         and i["pixel_sha256"] in preparation_hashes),
        "limitations": [
            "Draft preparation membership only; source provenance remains in a separate acquisition record.",
            "Original archive URL/time/hash are not inferred from unpacked files.",
            "Exact RGB-pixel duplicates are checked; related/near-duplicate and visual mask review remain pending.",
            "No model was trained and this is not the release image manifest or a frozen benchmark.",
        ],
    }
    validate_plan(plan)
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New development-only JSON plan; never overwrites")
    args = parser.parse_args(argv)
    try:
        audit = audit_directory(args.directory)
        if not audit["published_summary_matches"]:
            raise InventoryError("Resolve the directory audit mismatch before planning real-data splits")
        plan = build_plan(args.directory, audit)
        content = json.dumps(plan, indent=2, sort_keys=True, allow_nan=False) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(content)
    except InventoryError as error:
        print(f"FAIL preparation plan: {error}")
        return 1
    except FileExistsError:
        print("FAIL preparation plan: output already exists; choose a new filename")
        return 1
    except (OSError, ValueError, SyntaxError, EOFError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        print("FAIL preparation plan: cannot read images or write output")
        return 1
    print(f"PASS development-only preparation plan: {dict(Counter(i['split'] for i in plan['images']))}")
    print(f"Exact-pixel evaluation overlap: {len(plan['evaluation_overlap_ids'])}; related-image review pending")
    print("No training, image modifications or release manifest produced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
