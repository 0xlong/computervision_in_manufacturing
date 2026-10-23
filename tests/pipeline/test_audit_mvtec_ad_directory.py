"""Generated directory examples; no official dataset is needed for routine tests."""

import json
from pathlib import Path

from PIL import Image
import pytest

from pipeline.audit_mvtec_ad_directory import audit_directory, main
from pipeline.inventory_mvtec_ad import InventoryError


@pytest.fixture
def directory(tmp_path):
    root = tmp_path / "metal_nut"
    for index, name in enumerate(("train/good/000.png", "train/good/001.png",
            "test/good/000.png", "test/bent/000.png", "ground_truth/bent/000_mask.png")):
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        mask = name.startswith("ground_truth/")
        Image.new("L" if mask else "RGB", (700, 700), 255 if mask else index * 20).save(p)
    (root / "license.txt").write_text("TEST ONLY notice", encoding="utf-8")
    return root


def test_local_audit_hashes_every_file_without_inventing_origin(directory, monkeypatch):
    monkeypatch.setattr("pipeline.audit_mvtec_ad_directory.EXPECTED",
                        {"train_normal": 2, "test_normal": 1, "test_anomalous": 1, "masks": 1})
    report = audit_directory(directory)
    assert report["published_summary_matches"]
    assert report["total_files_checked"] == 6
    assert report["download_url"] is None and report["acquired_at"] is None
    assert report["archive_sha256"] is None
    assert report["evidence_status"] == "local_source_unverified"
    assert str(directory) not in json.dumps(report)
    repeated = audit_directory(directory)
    assert report["membership_sha256"] == repeated["membership_sha256"]
    (directory / "license.txt").write_text("Changed TEST ONLY notice", encoding="utf-8")
    assert audit_directory(directory)["membership_sha256"] != report["membership_sha256"]


def test_summary_mismatch_is_visible_and_existing_report_is_preserved(directory, tmp_path, capsys):
    output = tmp_path / "audit.json"
    args = [str(directory), "--output", str(output)]
    assert main(args) == 1
    assert "MISMATCH" in capsys.readouterr().out
    assert not json.loads(output.read_text())["published_summary_matches"]
    original = output.read_bytes()
    assert main(args) == 1
    assert "already exists" in capsys.readouterr().out
    assert output.read_bytes() == original


@pytest.mark.parametrize("problem", ["missing_mask", "corrupt_image"])
def test_bad_files_cannot_produce_successful_report(directory, tmp_path, problem, capsys):
    if problem == "missing_mask":
        (directory / "ground_truth/bent/000_mask.png").unlink()
    else:
        (directory / "test/bent/000.png").write_bytes(b"TEST ONLY broken PNG")
    output = tmp_path / "audit.json"
    assert main([str(directory), "--output", str(output)]) == 1
    assert not output.exists()
    stdout = capsys.readouterr().out
    assert "FAIL" in stdout and str(directory) not in stdout


def test_private_paths_are_excluded_without_reading_contents(directory, monkeypatch):
    private = directory / "done"
    private.mkdir()
    # Name only: never create or read secret contents in the test.
    original_read = Path.read_bytes
    def read_bytes(path):
        assert "done" not in path.parts
        return original_read(path)
    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    report = audit_directory(directory)
    assert report["excluded_entries"] == 1
    assert not report["published_summary_matches"]


def test_links_are_rejected_before_reading(directory, monkeypatch):
    original = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda path: path.name == "000.png" or original(path))
    with pytest.raises(InventoryError, match="link"):
        audit_directory(directory)


def test_duplicate_image_bytes_are_reported(directory):
    (directory / "test/good/000.png").write_bytes((directory / "train/good/000.png").read_bytes())
    assert audit_directory(directory)["exact_byte_duplicate_images"] == [
        ["test/good/000.png", "train/good/000.png"]]
