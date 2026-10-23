"""Validate the canonical JSON contract, then relationships JSON Schema cannot express.

This Pydantic envelope deliberately has no second set of field definitions. Future
frontend consumers must use the same schema plus equivalent relationship checks.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import file_digest
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import JsonValue, RootModel, model_validator


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas/image-manifest.v1.schema.json"
MANIFEST_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
Draft202012Validator.check_schema(MANIFEST_SCHEMA)
if "date-time" not in FormatChecker.checkers:
    raise RuntimeError("Install the contract lock: date-time format validation is required")
_VALIDATOR = Draft202012Validator(MANIFEST_SCHEMA, format_checker=FormatChecker())


class AssetValidationError(ValueError):
    """Safe actionable error without filesystem details or artifact values."""


def _reject_constant(value: str) -> None:
    raise ValueError("Nonfinite numbers are not valid artifact JSON")


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def read_manifest(path: Path) -> ImageManifest:
    """Read UTF-8 JSON without ambiguous duplicate keys or NaN/Infinity extensions."""
    data = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique_keys,
        parse_constant=_reject_constant,
    )
    return ImageManifest.model_validate(data)


def _validate_shape(data: Any) -> None:
    error = next(_VALIDATOR.iter_errors(data), None)
    if error is not None:
        # Do not echo untrusted artifact values, private paths or provider text.
        location = "/".join(str(part) for part in error.absolute_path) or "root"
        raise ValueError(f"Manifest contract violation at {location} ({error.validator})")


def _validate_relationships(data: dict[str, Any]) -> None:
    images = data["images"]
    for key in ("image_id", "source_member"):
        values = [image[key].casefold() for image in images]
        if len(values) != len(set(values)):
            raise ValueError(f"Duplicate {key} in manifest")

    splits = Counter(image["split"] for image in images)
    if any(splits[split] == 0 for split in ("fitting", "calibration", "evaluation")):
        raise ValueError("Fitting, calibration and evaluation sets must each be nonempty")

    hashes = {
        split: {image["source_sha256"] for image in images if image["split"] == split}
        for split in ("fitting", "calibration")
    }
    if hashes["fitting"] & hashes["calibration"]:
        raise ValueError("Identical source bytes overlap fitting and calibration sets")

    asset_paths: set[str] = set()
    for image in images:
        if image["display"]["dimensions"] != image["original_dimensions"]:
            raise ValueError("Identity transform requires matching source/display dimensions")
        if image["display"]["sha256"] != image["source_sha256"]:
            raise ValueError("Identity transform requires matching source/display hashes")
        mask = image["mask"]
        if mask is not None and mask["dimensions"] != image["display"]["dimensions"]:
            raise ValueError("Mask dimensions must match the displayed image")
        for asset in (image["display"], mask):
            if asset is None:
                continue
            path = asset["path"].casefold()
            if path in asset_paths:
                raise ValueError("Duplicate asset path in manifest")
            asset_paths.add(path)


class ImageManifest(RootModel[dict[str, JsonValue]]):
    """Schema-backed envelope; .root is validated manifest data, not inference input.

    Validation does not establish authenticity, actual pixel dimensions, split
    construction, official membership completeness or publication suitability.
    """

    @model_validator(mode="before")
    @classmethod
    def validate_manifest(cls, data: Any) -> Any:
        # Reject JSON extensions even through the Python API, without coercion.
        try:
            json.dumps(data, allow_nan=False)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("Manifest must contain finite JSON values") from error
        _validate_shape(data)
        _validate_relationships(data)
        return deepcopy(data)

    def test_overlap_ids(self) -> list[str]:
        """Report known exact-byte contamination without dropping test members."""
        preparation = {
            image["source_sha256"] for image in self.root["images"]
            if image["split"] != "evaluation"
        }
        return sorted(
            image["image_id"] for image in self.root["images"]
            if image["split"] == "evaluation" and image["source_sha256"] in preparation
        )


def verify_assets(manifest: ImageManifest, asset_root: Path) -> int:
    """Verify referenced display/mask bytes, failing on missing files or escapes.

    This does not decode images or validate their actual pixel dimensions.
    """
    # Revalidate because callers may have mutated a nested dictionary after loading.
    manifest = ImageManifest.model_validate(manifest.root)
    root = asset_root.resolve(strict=True)
    if not root.is_dir():
        raise AssetValidationError("Asset root must be a directory")
    count = 0
    for image in manifest.root["images"]:
        for kind in ("display", "mask"):
            asset = image[kind]
            if asset is None:
                continue
            path = (root / asset["path"]).resolve()
            if not path.is_relative_to(root):
                raise AssetValidationError(f"{kind} asset escapes asset root")
            if not path.is_file():
                raise AssetValidationError(f"{kind} asset is missing")
            with path.open("rb") as stream:
                actual = file_digest(stream, "sha256").hexdigest()
            if actual != asset["sha256"]:
                raise AssetValidationError(f"{kind} asset SHA-256 mismatch")
            count += 1
    return count
