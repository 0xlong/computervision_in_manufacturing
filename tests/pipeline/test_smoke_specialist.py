"""Check pretrained-weight integrity without requiring the ML stack in routine tests."""

import json
from pathlib import Path

import pytest

from pipeline.smoke_specialist import pretrained_feature_state, run


def test_legacy_batch_counters_are_distinguished_from_all_learned_features():
    state, missing = pretrained_feature_state({"conv1.weight", "bn1.running_mean", "bn1.num_batches_tracked"},
        {"conv1.weight": "TEST weight", "bn1.running_mean": "TEST statistic", "fc.weight": "TEST unused"})
    assert state == {"conv1.weight": "TEST weight", "bn1.running_mean": "TEST statistic"}
    assert missing == ["bn1.num_batches_tracked"]
    with pytest.raises(ValueError):
        pretrained_feature_state({"conv1.weight", "bn1.running_mean"}, {"conv1.weight": "TEST weight"})
    with pytest.raises(ValueError):
        pretrained_feature_state(set(), {})


def test_smoke_rejects_replaced_preparation_index_before_loading_models(tmp_path):
    config = json.loads(Path("configs/specialist-smoke.v1.json").read_text(encoding="utf-8"))
    inputs = tmp_path/"inputs"
    inputs.mkdir()
    # Replacing a fitting index with test data cannot silently enter a smoke run.
    (inputs/"fitting.json").write_text('{"TEST": "replaced by evaluation"}')
    (inputs/"calibration.json").write_text('{}')
    with pytest.raises(ValueError, match="fingerprints"):
        run("padim", inputs, tmp_path/"no-checkpoint", config, tmp_path/"output")
    assert not (tmp_path/"output").exists()
