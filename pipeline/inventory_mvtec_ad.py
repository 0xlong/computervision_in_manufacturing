"""Inventory a local MVTec AD metal_nut TAR without extracting or downloading it.

This is an acquisition aid, not a release manifest or proof of official origin.
Labels and archive paths are evaluator metadata, never provider inputs.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import file_digest, sha256
from io import BytesIO
import json
from pathlib import Path
import re
import tarfile
from urllib.parse import urlsplit
import warnings

from PIL import Image, __version__ as pillow_version


SOURCE_PAGE = "https://www.mvtec.com/research-teaching/datasets/mvtec-ad"
MAX_MEMBERS = 100_000
MAX_TOTAL_BYTES = 50 * 1024**3
MAX_FILE_BYTES = 64 * 1024**2
MAX_PIXELS = 25_000_000
_DEVICES = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}


class InventoryError(ValueError):
    """Actionable error that does not echo private paths or untrusted values."""


def _safe_name(name: str) -> str:
    # A leading ./ and the root directory entry are common in TARs.
    if not name or name.startswith("/"):
        raise InventoryError("Unsafe archive member path; no report written")
    if name.startswith("./"):
        name = name[2:]
    name = name.removesuffix("/")
    if name in ("", "."):
        return ""
    for part in name.split("/"):
        if (
            not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_. -]*", part)
            or part.endswith((".", " "))
            or part.split(".")[0].upper() in _DEVICES
        ):
            raise InventoryError("Unsafe archive member path; no report written")
    return name


def _provenance(source_url: str, acquired_at: str) -> None:
    url = urlsplit(source_url)
    if (
        url.scheme != "https" or not url.hostname or url.username or url.password
        or url.query or url.fragment or any(c.isspace() for c in source_url)
    ):
        raise InventoryError("Use a public HTTPS download URL without credentials, query or fragment")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", acquired_at):
        raise InventoryError("Acquisition time must be UTC: YYYY-MM-DDTHH:MM:SSZ")
    try:
        datetime.fromisoformat(acquired_at)
    except ValueError as error:
        raise InventoryError("Acquisition time is not a valid date") from error


def _png_info(content: bytes, *, mask: bool) -> dict:
    # verify checks PNG integrity; load separately forces actual pixel decoding.
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(BytesIO(content), formats=["PNG"]) as image:
            if image.width * image.height > MAX_PIXELS:
                raise InventoryError("Image exceeds pixel limit")
            image.verify()
        with Image.open(BytesIO(content), formats=["PNG"]) as image:
            image.load()
            if image.n_frames != 1:
                raise InventoryError("Image has multiple frames")
            if image.getexif().get(274, 1) != 1:
                raise InventoryError("Non-identity image orientation needs separate review")
            result = {
                "dimensions": {"width_px": image.width, "height_px": image.height},
                "mode": image.mode,
            }
            if mask:
                if image.mode not in ("1", "L"):
                    raise InventoryError("Expected a single-channel binary defect mask")
                colors = image.getcolors(maxcolors=3)
                if colors is None or not {color for _, color in colors} <= {0, 1, 255}:
                    raise InventoryError("Expected binary defect mask values")
                result["nonzero_pixels"] = sum(count for count, color in colors if color != 0)
                if result["nonzero_pixels"] == 0:
                    raise InventoryError("Anomalous image has an empty defect mask")
            return result


def _classify(relative: str) -> tuple[str, str | None]:
    parts = relative.split("/")
    if len(parts) == 3 and parts[2].endswith(".png"):
        split, defect, filename = parts
        if split == "train" and defect == "good":
            return "train", "normal"
        if split == "test":
            return "test", "normal" if defect == "good" else "anomalous"
        if split == "ground_truth" and defect != "good" and filename.endswith("_mask.png"):
            return "mask", None
    # No files inside the image trees may be silently skipped.
    if parts[0] in ("train", "test", "ground_truth") or relative.lower().endswith(".png"):
        raise InventoryError("Unexpected metal_nut image layout; review official archive contents")
    return "notice", None


def _pair_masks(images: list[dict], masks: dict[str, dict]) -> None:
    used = set()
    counts = Counter(image["official_split"] for image in images)
    if not counts["train"] or not counts["test"]:
        raise InventoryError("Archive must contain both metal_nut training and test images")
    if not any(image["label"] == "normal" and image["official_split"] == "test" for image in images):
        raise InventoryError("Archive has no normal metal_nut test images")
    for image in images:
        image["mask"] = None
        if image["label"] == "normal":
            continue
        _, defect, filename = image["category_member"].split("/")
        key = f"ground_truth/{defect}/{filename[:-4]}_mask.png"
        if key not in masks:
            raise InventoryError("Anomalous test image is missing its defect mask")
        mask = masks[key]
        if mask["dimensions"] != image["dimensions"]:
            raise InventoryError("Image and defect mask have different decoded dimensions")
        image["mask"] = mask
        used.add(key)
    if set(masks) != used:
        raise InventoryError("Archive contains defect masks without matching test images")
    if not used:
        raise InventoryError("Archive has no anomalous metal_nut test images with masks")


def inventory_archive(
    archive: Path, *, source_url: str, acquired_at: str, evidence_status: str = "acquired",
) -> dict:
    """Read one archive, retaining exact membership and decoded dimensions.

    Supports metal_nut/ at archive root or category-only train/test/ground_truth.
    Other categories are not decoded. All member paths/types are still checked.
    Nothing is extracted, resized, reoriented, selected for fitting, or sent online.
    """
    _provenance(source_url, acquired_at)
    if evidence_status not in ("fixture", "acquired"):
        raise InventoryError("Evidence status must be fixture or acquired")
    images, notices, masks = [], [], {}
    seen, layouts = set(), set()
    scanned = total_bytes = 0
    with archive.open("rb") as raw:
        initial_stat = archive.stat()
        archive_hash = file_digest(raw, "sha256").hexdigest()
        raw.seek(0)
        # Streaming avoids repeated decompression and never invokes extract/extractall.
        with tarfile.open(fileobj=raw, mode="r|*") as tar:
            for member in tar:
                scanned += 1
                if scanned > MAX_MEMBERS:
                    raise InventoryError("Archive exceeds member limit")
                name = _safe_name(member.name)
                if (not member.isdir() and not member.isfile()) or member.issparse():
                    raise InventoryError("Archive links, sparse files and special files are not supported")
                if not name:
                    if not member.isdir():
                        raise InventoryError("Archive file needs a nonempty safe name")
                    continue
                if name.casefold() in seen:
                    raise InventoryError("Duplicate or case-colliding archive member")
                seen.add(name.casefold())
                if member.isdir():
                    continue
                total_bytes += member.size
                if member.size < 0 or total_bytes > MAX_TOTAL_BYTES:
                    raise InventoryError("Archive exceeds unpacked size limit")
                if name.startswith("metal_nut/"):
                    relative = name[len("metal_nut/"):]
                    layouts.add("prefixed")
                elif name.split("/")[0] in ("train", "test", "ground_truth"):
                    relative = name
                    layouts.add("category_only")
                elif "/" not in name:
                    relative = name  # Retain root-level licence/readme notices too.
                else:
                    continue
                if len(layouts) > 1:
                    raise InventoryError("Ambiguous mixed category layouts in archive")
                kind, label = _classify(relative)
                if member.size > MAX_FILE_BYTES:
                    raise InventoryError("Selected archive member exceeds file size limit")
                with tar.extractfile(member) as stream:
                    content = stream.read(MAX_FILE_BYTES + 1)
                if len(content) != member.size:
                    raise InventoryError("Incomplete archive member bytes")
                record = {
                    "source_member": name, "category_member": relative,
                    "size_bytes": member.size, "sha256": sha256(content).hexdigest(),
                }
                if kind == "notice":
                    notices.append(record)
                    continue
                record.update(_png_info(content, mask=kind == "mask"))
                if kind == "mask":
                    masks[relative] = record
                else:
                    record.update(official_split=kind, label=label)
                    images.append(record)
        # Detect ordinary concurrent replacement/modification during this local check.
        current_stat = archive.stat()
        if any(getattr(current_stat, key) != getattr(initial_stat, key) for key in (
            "st_size", "st_mtime_ns", "st_ctime_ns", "st_ino", "st_dev",
        )):
            raise InventoryError("Archive changed during inventory; rerun on a stable file")
    _pair_masks(images, masks)
    images.sort(key=lambda image: image["source_member"])
    return {
        "inventory_version": 1,
        "evidence_status": evidence_status,
        "dataset_id": "mvtec_ad", "category": "metal_nut",
        "source_page": SOURCE_PAGE, "download_url": source_url,
        "published_licence": "CC-BY-NC-SA-4.0",
        "licence_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "acquired_at": acquired_at,
        "inventoried_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "archive": {"filename": archive.name, "size_bytes": initial_stat.st_size, "sha256": archive_hash},
        "decoder": {"name": "Pillow", "version": pillow_version},
        "counts": {
            "train_normal": sum(i["official_split"] == "train" for i in images),
            "test_normal": sum(i["official_split"] == "test" and i["label"] == "normal" for i in images),
            "test_anomalous": len(masks), "masks": len(masks),
        },
        "archive_members_scanned": scanned,
        "images": images,
        "other_selected_files": sorted(notices, key=lambda item: item["source_member"]),
        "limitations": [
            "Download URL and acquisition time are supplied by the operator; official origin needs review.",
            "Other selected files remain unchanged in the archive; licence contents need review.",
            "Matching mask dimensions do not prove visual annotation alignment.",
            "No preparation split, duplicate audit, release manifest or model evidence is produced.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Local .tar / .tar.gz / .tar.xz downloaded through MVTec")
    parser.add_argument("--source-url", required=True, help="Public download URL (no private links or query strings)")
    parser.add_argument("--acquired-at", required=True, help="Actual download time in UTC, YYYY-MM-DDTHH:MM:SSZ")
    parser.add_argument("--output", required=True, type=Path, help="New local JSON report; existing files are never overwritten")
    parser.add_argument("--evidence-status", choices=("fixture", "acquired"), default="acquired")
    args = parser.parse_args(argv)
    try:
        report = inventory_archive(
            args.archive, source_url=args.source_url, acquired_at=args.acquired_at,
            evidence_status=args.evidence_status,
        )
        content = json.dumps(report, indent=2, allow_nan=False) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(content)
    except InventoryError as error:
        print(f"FAIL inventory: {error}")
        return 1
    except FileExistsError:
        print("FAIL inventory: output already exists; choose a new report filename")
        return 1
    except (OSError, ValueError, SyntaxError, EOFError, tarfile.TarError,
            Image.DecompressionBombWarning, Image.DecompressionBombError):
        print("FAIL inventory: cannot read archive/image or write report; check files and permissions")
        return 1
    c = report["counts"]
    print(f"PASS local inventory ({report['evidence_status']}): train={c['train_normal']}, "
          f"test normal={c['test_normal']}, test anomalous={c['test_anomalous']}, masks={c['masks']}")
    print("Nothing extracted. Not proof of official origin, benchmark completeness or model performance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
