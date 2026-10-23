from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError
import pytest

from pipeline.contracts import ImageManifest, MANIFEST_SCHEMA, read_manifest, verify_assets
from pipeline.validate_manifest import main


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/image-manifest.fixture.json"


@pytest.fixture
def data():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_schema_is_draft_2020_12_and_accepts_explicit_fixture(data):
    assert MANIFEST_SCHEMA["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(MANIFEST_SCHEMA)
    Draft202012Validator(MANIFEST_SCHEMA, format_checker=FormatChecker()).validate(data)
    manifest = read_manifest(FIXTURE)
    assert manifest.root == data
    assert manifest.root["evidence_status"] == "fixture"
    assert json.loads(manifest.model_dump_json()) == data


@pytest.mark.parametrize("path,value", [
    (("schema_version",), 2),
    (("schema_version",), "1"),
    (("schema_version",), True),
    (("evidence_status",), "release_approved"),
    (("dataset", "category"), "sheet_metal"),
    (("dataset", "source_url"), "https://example.invalid"),
    (("dataset", "licence"), "MIT"),
    (("dataset", "acquired_at"), "2026-02-30T00:00:00Z"),
    (("dataset", "acquired_at"), "2026-10-23T00:00:00+02:00"),
    (("dataset", "archive_sha256"), "a" * 63),
    (("dataset", "archive_sha256"), "a" * 64 + "\n"),
    (("images", 0, "image_id"), "normal-001"),
    (("images", 0, "track_id"), "metal_surfaces"),
    (("images", 0, "official_split"), "test_public"),
    (("images", 1, "official_split"), "validation"),
    (("images", 2, "official_split"), "test_private"),
    (("images", 0, "label"), "anomalous"),
    (("images", 0, "original_dimensions", "width_px"), 0),
    (("images", 0, "original_dimensions", "width_px"), "32"),
    (("images", 0, "transform", "operation"), "resize"),
    (("images", 0, "unexpected"), "untrusted"),
])
def test_schema_and_pydantic_reject_the_same_invalid_fields(data, path, value):
    target = data
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    # The Pydantic envelope must not coerce or weaken the authoritative schema.
    assert not Draft202012Validator(MANIFEST_SCHEMA, format_checker=FormatChecker()).is_valid(data)
    with pytest.raises(ValidationError):
        ImageManifest.model_validate(data)


@pytest.mark.parametrize("path", [
    "../outside.png", "/absolute.png", "C:/private.png", "images\\a.png",
    "https://example.invalid/a.png", "//host/a.png", "images/../a.png",
    "images/%2e%2e/a.png", "images/a.png?query=1", "images/.hidden/a.png",
    "images/a.png\n", "images//a.png", "images/./a.png", "images/a.png#fragment",
])
def test_unsafe_asset_paths_rejected(data, path):
    data["images"][0]["display"]["path"] = path
    with pytest.raises(ValidationError):
        ImageManifest.model_validate(data)


def test_ad2_uses_official_validation_for_calibration(data):
    data["track_id"] = "metal_surfaces"
    data["dataset"].update(
        dataset_id="mvtec_ad2", category="sheet_metal",
        source_url="https://www.mvtec.com/research-teaching/datasets/mvtec-ad-2",
    )
    for image in data["images"]:
        image["track_id"] = "metal_surfaces"
    with pytest.raises(ValidationError):
        ImageManifest.model_validate(data)
    data["images"][1]["official_split"] = "validation"
    assert ImageManifest.model_validate(data).root == data


@pytest.mark.parametrize("field", ["image_id", "source_member"])
def test_duplicate_identity_rejected(data, field):
    data["images"][1][field] = data["images"][0][field]
    with pytest.raises(ValidationError, match=f"Duplicate {field}"):
        ImageManifest.model_validate(data)


def test_missing_calibration_rejected(data):
    data["images"][1]["split"] = "fitting"
    with pytest.raises(ValidationError, match="nonempty"):
        ImageManifest.model_validate(data)


def test_identical_preparation_bytes_rejected_but_test_members_retained(data):
    duplicate_hash = data["images"][0]["source_sha256"]
    data["images"][1]["source_sha256"] = duplicate_hash
    data["images"][1]["display"]["sha256"] = duplicate_hash
    with pytest.raises(ValidationError, match="overlap fitting and calibration"):
        ImageManifest.model_validate(data)
    data["images"][1]["source_sha256"] = "2" * 64
    data["images"][1]["display"]["sha256"] = "2" * 64
    data["images"][2]["source_sha256"] = duplicate_hash
    data["images"][2]["display"]["sha256"] = duplicate_hash
    manifest = ImageManifest.model_validate(data)
    assert manifest.test_overlap_ids() == ["img-000003"]
    assert len(manifest.root["images"]) == 3


@pytest.mark.parametrize("change", ["dimensions", "hash", "mask_dimensions", "duplicate_asset"])
def test_alignment_and_asset_identity(data, change):
    if change == "dimensions":
        data["images"][0]["display"]["dimensions"]["width_px"] = 16
    elif change == "hash":
        data["images"][0]["display"]["sha256"] = "9" * 64
    elif change == "mask_dimensions":
        data["images"][2]["label"] = "anomalous"
        data["images"][2]["mask"] = deepcopy(data["images"][2]["display"])
        data["images"][2]["mask"]["path"] = "masks/img-000003.png"
        data["images"][2]["mask"]["dimensions"]["width_px"] = 16
    else:
        data["images"][1]["display"]["path"] = data["images"][0]["display"]["path"].upper()
    with pytest.raises(ValidationError):
        ImageManifest.model_validate(data)


def test_anomalous_image_with_aligned_mask_accepted(data):
    image = data["images"][2]
    image["label"] = "anomalous"
    image["mask"] = deepcopy(image["display"])
    image["mask"]["path"] = "masks/img-000003.png"
    assert ImageManifest.model_validate(data).root == data


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_values_rejected_even_through_python_api(data, value):
    data["images"][0]["original_dimensions"]["width_px"] = value
    with pytest.raises(ValidationError, match="finite JSON"):
        ImageManifest.model_validate(data)


@pytest.mark.parametrize("content", [
    '{"schema_version":1,"schema_version":2}', '{"bad":NaN}',
    '{"bad":Infinity}', '{"bad":1e9999}', '{broken',
])
def test_strict_json_reader(tmp_path, content):
    path = tmp_path / "invalid.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises((ValueError, ValidationError)):
        read_manifest(path)


def materialize_assets(data, root):
    # Synthetic byte files test hashing only. They deliberately are not real images.
    for index, image in enumerate(data["images"]):
        content = f"TEST-ONLY-BYTES-{index}".encode()
        digest = sha256(content).hexdigest()
        image["source_sha256"] = digest
        image["display"]["sha256"] = digest
        path = root / image["display"]["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def test_asset_files_hashes_missing_and_modified(data, tmp_path):
    materialize_assets(data, tmp_path)
    manifest = ImageManifest.model_validate(data)
    assert verify_assets(manifest, tmp_path) == 3
    asset = tmp_path / data["images"][0]["display"]["path"]
    asset.write_bytes(b"changed")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        verify_assets(manifest, tmp_path)
    asset.unlink()
    with pytest.raises(ValueError, match="missing"):
        verify_assets(manifest, tmp_path)


def test_resolved_asset_must_stay_under_root(data, tmp_path, monkeypatch):
    root = tmp_path / "assets"
    root.mkdir()
    original = Path.resolve
    # Windows may deny creating symlinks; exercise resolved-path containment directly.
    def resolve(path, *args, **kwargs):
        if path.name == "img-000001.png":
            return tmp_path / "outside.png"
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "resolve", resolve)
    with pytest.raises(ValueError, match="escapes asset root"):
        verify_assets(ImageManifest.model_validate(data), root)


def test_cli_fixture_limitations_and_failure_exit(data, tmp_path, capsys):
    assert main([str(FIXTURE)]) == 0
    output = capsys.readouterr().out
    assert "fixture" in output and "Asset bytes NOT checked" in output
    assert "Not a release check" in output
    data["schema_version"] = 999
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert main([str(path)]) == 1
    output = capsys.readouterr().out
    assert "schema_version" in output and str(tmp_path) not in output


def test_cli_reports_test_overlap_without_deleting_test_image(data, tmp_path, capsys):
    data["images"][2]["source_sha256"] = data["images"][0]["source_sha256"]
    data["images"][2]["display"]["sha256"] = data["images"][0]["source_sha256"]
    path = tmp_path / "overlap.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert main([str(path)]) == 0
    output = capsys.readouterr().out
    assert "WARNING exact-byte test contamination: img-000003" in output
    assert "evaluation=1" in output


def test_cli_checks_asset_bytes_and_explains_corruption(data, tmp_path, capsys):
    materialize_assets(data, tmp_path)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert main([str(path), "--asset-root", str(tmp_path)]) == 0
    assert "PASS asset bytes: 3 files" in capsys.readouterr().out
    (tmp_path / data["images"][0]["display"]["path"]).write_bytes(b"modified")
    assert main([str(path), "--asset-root", str(tmp_path)]) == 1
    output = capsys.readouterr().out
    assert "SHA-256 mismatch" in output and str(tmp_path) not in output
