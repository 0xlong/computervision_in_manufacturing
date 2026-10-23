"""Check an unpacked metal_nut folder without inventing download provenance."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path

from PIL import Image, __version__ as pillow_version

from pipeline.inventory_mvtec_ad import (
    InventoryError, MAX_FILE_BYTES, MAX_MEMBERS, MAX_TOTAL_BYTES,
    _classify, _pair_masks, _png_info, _safe_name,
)


# Table 1 in the paper linked by the official dataset page, checked 2026-10-23.
REFERENCE = "https://www.mvtec.com/fileadmin/Redaktion/mvtec.com/05_research_teaching/datasets/mvtec_ad.pdf"
EXPECTED = {"train_normal": 220, "test_normal": 22, "test_anomalous": 93, "masks": 93}


def audit_directory(root: Path) -> dict:
    """Hash/decode all dataset files; leave source files and missing provenance alone.

    Matching published totals does not establish exact official membership or origin.
    Do not follow directory links, junctions, file links or secret-bearing paths.
    """
    if root.is_symlink() or root.is_junction() or not root.is_dir():
        raise InventoryError("Select a real, unpacked category directory")
    root = root.resolve(strict=True)
    images, masks, notices, excluded = [], {}, [], []
    seen = set()
    total = 0
    def walk_error(error: OSError) -> None:
        raise error

    for current, directories, filenames in os.walk(root, followlinks=False, onerror=walk_error):
        for name in list(directories) + filenames:
            path = Path(current) / name
            relative = path.relative_to(root).as_posix()
            parts = [part.lower() for part in path.relative_to(root).parts]
            if any(part in ("done", ".git", ".aws") or part.startswith(".env")
                   or any(word in part for word in ("credential", "token", "secret")) for part in parts):
                if name in directories:
                    directories.remove(name)
                excluded.append("excluded private/configuration entry")
                continue
            if path.is_symlink() or path.is_junction():
                raise InventoryError("Dataset directory contains a link or junction")
            _safe_name(relative)
            if relative.casefold() in seen:
                raise InventoryError("Duplicate or case-colliding directory member")
            seen.add(relative.casefold())
            if len(seen) > MAX_MEMBERS:
                raise InventoryError("Dataset directory exceeds member limit")
            if path.is_dir():
                continue
            if not path.is_file() or not path.resolve(strict=True).is_relative_to(root):
                raise InventoryError("Dataset member is not a contained regular file")
            before = path.stat()
            total += before.st_size
            if before.st_size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                raise InventoryError("Dataset directory exceeds file or total size limit")
            content = path.read_bytes()
            after = path.stat()
            if len(content) != before.st_size or any(getattr(before, k) != getattr(after, k)
                    for k in ("st_size", "st_mtime_ns", "st_ino", "st_dev")):
                raise InventoryError("Dataset file changed during checking")
            kind, label = _classify(relative)
            record = {"source_member": relative, "category_member": relative,
                      "size_bytes": len(content), "sha256": sha256(content).hexdigest()}
            if kind == "notice":
                notices.append(record)
            else:
                record.update(_png_info(content, mask=kind == "mask"))
                if kind == "mask":
                    masks[relative] = record
                else:
                    record.update(official_split=kind, label=label)
                    images.append(record)
    _pair_masks(images, masks)
    images.sort(key=lambda item: item["source_member"])
    notices.sort(key=lambda item: item["source_member"])
    counts = {
        "train_normal": sum(i["official_split"] == "train" for i in images),
        "test_normal": sum(i["official_split"] == "test" and i["label"] == "normal" for i in images),
        "test_anomalous": len(masks), "masks": len(masks),
    }
    all_files = sorted(images + list(masks.values()) + notices, key=lambda item: item["source_member"])
    membership = [{key: item[key] for key in ("source_member", "size_bytes", "sha256")} for item in all_files]
    dimensions = Counter((i["dimensions"]["width_px"], i["dimensions"]["height_px"]) for i in images)
    hashes = defaultdict(list)
    for image in images:
        hashes[image["sha256"]].append(image["source_member"])
    return {
        "audit_version": 1, "evidence_status": "local_source_unverified",
        "dataset_id": "mvtec_ad", "category": "metal_nut",
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "download_url": None, "acquired_at": None, "archive_sha256": None,
        "decoder": {"name": "Pillow", "version": pillow_version},
        "reference": {"url": REFERENCE, "table": 1, "expected_counts": EXPECTED, "side_length_px": 700},
        "counts": counts,
        "published_summary_matches": counts == EXPECTED and set(dimensions) == {(700, 700)} and not excluded,
        "image_dimensions": [{"width_px": w, "height_px": h, "count": n} for (w, h), n in sorted(dimensions.items())],
        "test_defect_counts": dict(sorted(Counter(i["category_member"].split("/")[1]
            for i in images if i["official_split"] == "test").items())),
        "membership_sha256": sha256(json.dumps(membership, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "total_files_checked": len(all_files), "total_bytes_checked": total,
        "excluded_entries": len(excluded),
        "exact_byte_duplicate_images": sorted(v for v in hashes.values() if len(v) > 1),
        "images": images, "other_files": notices,
        "limitations": [
            "Published counts and dimensions are a summary check, not an official per-file checksum comparison.",
            "Download origin, acquisition time and original archive hash are unknown.",
            "Mask dimensions and binary values are checked; visual annotation alignment needs review.",
            "No preparation split, related-image audit, release manifest or AI output is produced.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="New local audit JSON; never overwrites")
    args = parser.parse_args(argv)
    try:
        report = audit_directory(args.directory)
        content = json.dumps(report, indent=2, allow_nan=False) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(content)
    except InventoryError as error:
        print(f"FAIL directory audit: {error}")
        return 1
    except FileExistsError:
        print("FAIL directory audit: output already exists; choose a new filename")
        return 1
    except (OSError, ValueError, SyntaxError, EOFError,
            Image.DecompressionBombWarning, Image.DecompressionBombError):
        print("FAIL directory audit: cannot read dataset images or write report")
        return 1
    print(f"PASS local file integrity: {report['total_files_checked']} files; counts={report['counts']}")
    matches = report["published_summary_matches"]
    print(f"Published count/dimension summary: {'MATCH' if matches else 'MISMATCH'}; original source UNVERIFIED")
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
