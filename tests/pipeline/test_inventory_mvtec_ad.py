"""Tiny synthetic PNG/TARs exercise acquisition checks; no official data is used."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import tarfile

from PIL import Image
import pytest

from pipeline.inventory_mvtec_ad import InventoryError, inventory_archive, main


PROVENANCE = {
    "source_url": "https://example.invalid/TEST-ONLY-metal_nut.tar.xz",
    "acquired_at": "2026-10-23T10:00:00Z", "evidence_status": "fixture",
}


def png(size=(8, 6), mode="RGB", color=80):
    stream = BytesIO()
    Image.new(mode, size, color).save(stream, format="PNG")
    return stream.getvalue()


@pytest.fixture
def members():
    return {
        "metal_nut/train/good/000.png": png(color=10),
        "metal_nut/train/good/001.png": png(color=20),
        "metal_nut/test/good/000.png": png(color=30),
        "metal_nut/test/scratch/000.png": png(color=40),
        "metal_nut/ground_truth/scratch/000_mask.png": png(mode="L", color=255),
        "license.txt": b"TEST ONLY notice, not the dataset licence.",
    }


def write_archive(path: Path, members: dict, extras=(), mode="w:xz"):
    with tarfile.open(path, mode) as tar:
        directory = tarfile.TarInfo("./")
        directory.type = tarfile.DIRTYPE
        tar.addfile(directory)
        for name, content in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            tar.addfile(info, BytesIO(content))
        for info, content in extras:
            tar.addfile(info, BytesIO(content))
    return path


@pytest.mark.parametrize("mode", ["w", "w:gz", "w:xz"])
@pytest.mark.parametrize("layout", ["prefixed", "category_only", "leading_dot"])
def test_inventory_preserves_members_hashes_and_decodes_pixels(members, tmp_path, mode, layout):
    if layout == "category_only":
        members = {k.removeprefix("metal_nut/"): v for k, v in members.items()}
    elif layout == "leading_dot":
        members = {"./" + k: v for k, v in members.items()}
    archive = write_archive(tmp_path / "fixture.tar", members, mode=mode)
    before = archive.read_bytes()
    report = inventory_archive(archive, **PROVENANCE)
    assert report["counts"] == {"train_normal": 2, "test_normal": 1, "test_anomalous": 1, "masks": 1}
    assert report["evidence_status"] == "fixture"
    assert report["archive"]["sha256"] == sha256(before).hexdigest()
    assert report["archive"]["size_bytes"] == len(before)
    assert report["download_url"] == PROVENANCE["source_url"]
    assert report["acquired_at"] == PROVENANCE["acquired_at"]
    assert report["published_licence"] == "CC-BY-NC-SA-4.0"
    assert all(i["dimensions"] == {"width_px": 8, "height_px": 6} for i in report["images"])
    anomalous = next(i for i in report["images"] if i["label"] == "anomalous")
    mask = anomalous["mask"]
    assert mask["nonzero_pixels"] == 48
    assert mask["source_member"].endswith("ground_truth/scratch/000_mask.png")
    assert mask["sha256"] == sha256(members[("./" if layout == "leading_dot" else "") + mask["source_member"]]).hexdigest()
    assert report["other_selected_files"][0]["sha256"] == sha256(members[("./" if layout == "leading_dot" else "") + "license.txt"]).hexdigest()
    assert archive.read_bytes() == before
    assert list(tmp_path.iterdir()) == [archive]  # No extracted images or notices.
    assert str(tmp_path) not in json.dumps(report)


@pytest.mark.parametrize("name", [
    "../escape.png", "/absolute.png", "C:/private.png", "metal_nut\\bad.png",
    "metal_nut/../bad.png", "metal_nut//bad.png", "metal_nut/./bad.png",
    "metal_nut/test/good/NUL.png", "metal_nut/.env", "metal_nut/name.",
    "metal_nut/name ", "metal_nut/%2e%2e/bad.png",
])
def test_rejects_unsafe_paths_even_in_unselected_members(members, tmp_path, name):
    members[name] = b"TEST ONLY"
    archive = write_archive(tmp_path / "fixture.tar.xz", members)
    with pytest.raises(InventoryError, match="Unsafe"):
        inventory_archive(archive, **PROVENANCE)


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE, tarfile.CHRTYPE])
def test_rejects_links_and_special_files(members, tmp_path, kind):
    info = tarfile.TarInfo("other_category/link")
    info.type, info.linkname = kind, "../outside"
    archive = write_archive(tmp_path / "fixture.tar.xz", members, [(info, b"")])
    with pytest.raises(InventoryError, match="links"):
        inventory_archive(archive, **PROVENANCE)


def test_rejects_absolute_root_directory(members, tmp_path):
    info = tarfile.TarInfo("/")
    info.type = tarfile.DIRTYPE
    archive = write_archive(tmp_path / "fixture.tar.xz", members, [(info, b"")])
    with pytest.raises(InventoryError, match="Unsafe"):
        inventory_archive(archive, **PROVENANCE)


@pytest.mark.parametrize("name", ["metal_nut/train/good/000.png", "METAL_NUT/TRAIN/GOOD/000.PNG"])
def test_rejects_duplicate_and_case_colliding_members(members, tmp_path, name):
    info = tarfile.TarInfo(name)
    archive = write_archive(tmp_path / "fixture.tar.xz", members, [(info, b"")])
    with pytest.raises(InventoryError, match="Duplicate"):
        inventory_archive(archive, **PROVENANCE)


@pytest.mark.parametrize("problem", [
    "missing_mask", "orphan_mask", "wrong_dimensions", "empty_mask", "nonbinary_mask",
    "color_mask", "unexpected_image", "bad_layout", "missing_train", "missing_normal_test",
    "mixed_layout",
])
def test_rejects_incomplete_or_misaligned_membership(members, tmp_path, problem):
    mask = "metal_nut/ground_truth/scratch/000_mask.png"
    if problem == "missing_mask":
        del members[mask]
    elif problem == "orphan_mask":
        members[mask.replace("000", "999")] = members[mask]
    elif problem == "wrong_dimensions":
        members[mask] = png(size=(4, 3), mode="L", color=255)
    elif problem == "empty_mask":
        members[mask] = png(mode="L", color=0)
    elif problem == "nonbinary_mask":
        members[mask] = png(mode="L", color=100)
    elif problem == "color_mask":
        members[mask] = png(mode="RGB", color=255)
    elif problem == "unexpected_image":
        members["metal_nut/unknown.png"] = png()
    elif problem == "bad_layout":
        members["metal_nut/train/bad/000.png"] = png()
    elif problem == "missing_train":
        members = {k: v for k, v in members.items() if "/train/" not in k}
    elif problem == "missing_normal_test":
        del members["metal_nut/test/good/000.png"]
    else:
        members["train/good/002.png"] = png()
    archive = write_archive(tmp_path / "fixture.tar.xz", members)
    with pytest.raises(InventoryError):
        inventory_archive(archive, **PROVENANCE)


def cli_args(archive, output):
    return [str(archive), "--source-url", PROVENANCE["source_url"],
            "--acquired-at", PROVENANCE["acquired_at"], "--evidence-status", "fixture",
            "--output", str(output)]


def bad_crc_png():
    content = bytearray(png())
    content[-13] ^= 1  # Alter the IDAT checksum without changing image dimensions.
    return bytes(content)


@pytest.mark.parametrize("bad_image", [b"not an image", png()[:45], bad_crc_png()])
def test_cli_corrupt_image_leaves_no_report_or_private_path(members, tmp_path, capsys, bad_image):
    members["metal_nut/test/scratch/000.png"] = bad_image
    archive = write_archive(tmp_path / "fixture.tar.xz", members)
    output = tmp_path / "report.json"
    assert main(cli_args(archive, output)) == 1
    assert not output.exists()
    stdout = capsys.readouterr().out
    assert "FAIL inventory" in stdout and str(tmp_path) not in stdout


@pytest.mark.parametrize("problem", ["orientation", "animation"])
def test_rejects_unrecorded_orientation_and_animated_png(members, tmp_path, problem):
    stream = BytesIO()
    image = Image.new("RGB", (8, 6), 80)
    if problem == "orientation":
        exif = Image.Exif()
        exif[274] = 6
        image.save(stream, format="PNG", exif=exif)
    else:
        image.save(stream, format="PNG", save_all=True,
                   append_images=[Image.new("RGB", (8, 6), 90)], duration=100)
    members["metal_nut/test/scratch/000.png"] = stream.getvalue()
    archive = write_archive(tmp_path / "fixture.tar.xz", members)
    with pytest.raises(InventoryError):
        inventory_archive(archive, **PROVENANCE)


def test_cli_success_never_overwrites_existing_report(members, tmp_path, capsys):
    archive = write_archive(tmp_path / "fixture.tar.xz", members)
    output = tmp_path / "report.json"
    assert main(cli_args(archive, output)) == 0
    stdout = capsys.readouterr().out
    assert "fixture" in stdout and "Nothing extracted" in stdout
    report_bytes = output.read_bytes()
    assert main(cli_args(archive, output)) == 1
    assert "already exists" in capsys.readouterr().out
    assert output.read_bytes() == report_bytes


@pytest.mark.parametrize("source_url,acquired_at", [
    ("http://example.invalid/a.tar", PROVENANCE["acquired_at"]),
    ("https://user:password@example.invalid/a.tar", PROVENANCE["acquired_at"]),
    ("https://example.invalid/a.tar?private=value", PROVENANCE["acquired_at"]),
    ("https://example.invalid/a.tar#private", PROVENANCE["acquired_at"]),
    (PROVENANCE["source_url"], "2026-10-23T12:00:00+02:00"),
    (PROVENANCE["source_url"], "2026-02-30T10:00:00Z"),
])
def test_rejects_private_links_and_invalid_download_times(tmp_path, source_url, acquired_at):
    with pytest.raises(InventoryError):
        inventory_archive(tmp_path / "not-opened.tar", source_url=source_url, acquired_at=acquired_at)


@pytest.mark.parametrize("limit,value", [("MAX_FILE_BYTES", 4), ("MAX_TOTAL_BYTES", 4),
                                          ("MAX_MEMBERS", 2), ("MAX_PIXELS", 4)])
def test_resource_limits_fail_explicitly(members, tmp_path, monkeypatch, limit, value):
    monkeypatch.setattr("pipeline.inventory_mvtec_ad." + limit, value)
    archive = write_archive(tmp_path / "fixture.tar.xz", members)
    with pytest.raises(InventoryError, match="limit"):
        inventory_archive(archive, **PROVENANCE)


def test_other_categories_are_not_decoded(members, tmp_path):
    members["bottle/train/good/000.png"] = b"Not decoded: unselected category"
    archive = write_archive(tmp_path / "fixture.tar.xz", members)
    report = inventory_archive(archive, **PROVENANCE)
    assert len(report["images"]) == 4
    assert report["archive_members_scanned"] == 8


def test_cli_missing_and_invalid_archive_errors_are_sanitized(tmp_path, capsys):
    archive, output = tmp_path / "missing.tar", tmp_path / "report.json"
    assert main(cli_args(archive, output)) == 1
    archive.write_bytes(b"not a tar")
    assert main(cli_args(archive, output)) == 1
    stdout = capsys.readouterr().out
    assert str(tmp_path) not in stdout and "Traceback" not in stdout
    assert not output.exists()
