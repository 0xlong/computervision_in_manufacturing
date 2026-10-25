"""Offline verification of the committed genuine local fastener package."""

from hashlib import sha256
import json
from pathlib import Path

from PIL import Image

from pipeline.public_bundle import FastenerBundle, FrozenConfiguration


ROOT = Path(__file__).resolve().parents[2] / "web/public/evidence"


def test_complete_authentic_bundle_regenerates_metrics_without_inference():
    data = json.loads((ROOT / "bundle.json").read_text(encoding="utf-8"))
    bundle = FastenerBundle.model_validate(data).root
    assert bundle["execution"] == "recorded_live"
    assert bundle["local_only"] is True
    for saved in bundle["runs"]:
        report = saved["report"]
        assert report["expected"] == 115
        assert report["full_set_routing"]["normal"] == 22
        assert report["full_set_routing"]["anomalous"] == 93
        assert report["succeeded"] + report["failed"] == 115
        assert len(saved["evidence"]["predictions"]) == 115


def test_committed_images_masks_and_original_notices_match_saved_hashes():
    bundle = json.loads((ROOT / "bundle.json").read_text(encoding="utf-8"))
    for item in bundle["images"]:
        for kind in ("display", "mask"):
            asset = item[kind]
            if asset is None: continue
            path = ROOT / asset["path"]
            assert sha256(path.read_bytes()).hexdigest() == asset["sha256"]
            with Image.open(path) as image:
                image.load()
                assert image.size == (asset["dimensions"]["width_px"], asset["dimensions"]["height_px"])
                if kind == "mask": assert set(image.tobytes()) == {0, 255}
    for notice in bundle["notices"]:
        assert sha256((ROOT / notice["path"]).read_bytes()).hexdigest() == notice["sha256"]
    from pipeline.api_contracts import fingerprint
    for config in bundle["configuration_assets"]:
        content = (ROOT / config["path"]).read_bytes()
        assert sha256(content).hexdigest() == config["sha256"]
        data = json.loads(content)
        assert FrozenConfiguration.model_validate(data).root == data
        expected_version = next(version for prefix, version in (
            ("eval-flash-lite-", 1), ("eval-comparison-", 2), ("eval-gemma-", 3))
            if config["run_id"].startswith(prefix))
        assert data["schema_version"] == expected_version and data["run_id"] == config["run_id"]
        run = next(r["evidence"]["run"] for r in bundle["runs"] if r["evidence"]["run"]["run_id"] == config["run_id"])
        plan = data["frozen_plan"]
        assert fingerprint({k: v for k, v in plan.items() if k not in {"frozen_at", "run_id"}}) == run["hashes"]["configuration"]
        assert fingerprint(plan["configuration"]["prompt"]) == run["hashes"]["prompt"]
        assert fingerprint([plan["reference"]]) == run["hashes"]["references"]
