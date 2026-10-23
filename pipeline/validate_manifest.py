"""Local manifest checker. Run from the repository root with python -m."""

import argparse
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from pipeline.contracts import AssetValidationError, read_manifest, verify_assets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an image manifest; makes no network calls.")
    parser.add_argument("manifest", type=Path, help="UTF-8 manifest JSON")
    parser.add_argument("--asset-root", type=Path, help="Also check display/mask file existence and SHA-256")
    args = parser.parse_args(argv)
    try:
        manifest = read_manifest(args.manifest)
        checked = verify_assets(manifest, args.asset_root) if args.asset_root is not None else None
    except ValidationError as error:
        # Pydantic's default repr can echo the entire input; report only our message.
        print("FAIL: " + error.errors(include_input=False, include_url=False)[0]["msg"])
        return 1
    except AssetValidationError as error:
        print("FAIL: " + str(error))
        return 1
    except (OSError, ValueError):
        # Never echo filesystem paths or raw invalid JSON in command output.
        print("FAIL: Cannot read valid manifest/assets. Check UTF-8 JSON, unique keys, file access and asset hashes.")
        return 1
    counts = Counter(image["split"] for image in manifest.root["images"])
    print(f"PASS manifest contract: {manifest.root['manifest_id']} ({manifest.root['evidence_status']})")
    print("Images: " + ", ".join(f"{split}={counts[split]}" for split in ("fitting", "calibration", "evaluation")))
    if checked is None:
        print("Asset bytes NOT checked; use --asset-root to check file existence and SHA-256.")
    else:
        print(f"PASS asset bytes: {checked} files; decoded dimensions/alignment remain unchecked.")
    overlap = manifest.test_overlap_ids()
    if overlap:
        print("WARNING exact-byte test contamination: " + ", ".join(overlap))
    print("Not a release check: official membership, related images and authenticity need separate evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
