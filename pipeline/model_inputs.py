"""The inference-side boundary: neutral identifiers and checked clean RGB pixels only."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from PIL import Image

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "schemas/model-inputs.v1.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)


def validate_inputs(index: dict, root: Path) -> None:
    if next(VALIDATOR.iter_errors(index), None):
        raise ValueError("Invalid answer-free input contract")
    root = root.resolve(strict=True)
    ids, paths = set(), set()
    for item in index["images"]:
        if item["image_id"] in ids or item["path"] in paths:
            raise ValueError("Duplicate input identity")
        ids.add(item["image_id"])
        paths.add(item["path"])
        if item["path"] != f"images/{item['image_id']}.png":
            raise ValueError("Input path must match neutral ID")
        path = root / item["path"]
        if path.is_symlink() or path.is_junction() or not path.resolve(strict=True).is_relative_to(root):
            raise ValueError("Input escapes model root")
        content = path.read_bytes()
        if sha256(content).hexdigest() != item["sha256"]:
            raise ValueError("Input bytes changed")
        with Image.open(BytesIO(content), formats=["PNG"]) as image:
            image.verify()
        with Image.open(BytesIO(content), formats=["PNG"]) as image:
            image.load()
            if image.mode != "RGB" or image.info or image.n_frames != 1:
                raise ValueError("Input must be a metadata-free single RGB image")
            if item["dimensions"] != {"width_px": image.width, "height_px": image.height}:
                raise ValueError("Input dimensions mismatch")


def read_inputs(path: Path) -> dict:
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON input key")
            result[key] = value
        return result
    def reject_constant(_):
        raise ValueError("Nonfinite input JSON")
    index = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys,
                       parse_constant=reject_constant)
    validate_inputs(index, path.parent)
    return index
