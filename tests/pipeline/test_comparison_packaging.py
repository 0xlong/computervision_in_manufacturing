"""Generated configuration/challenge examples only; no provider access."""

from copy import deepcopy
from pathlib import Path
import json

import pytest

from pipeline import run_gemini_comparison as comparison
from pipeline import run_gemini_evaluation as evaluation
from pipeline import run_gemini_trial as trial
from pipeline.api_contracts import fingerprint
from pipeline.public_bundle import FrozenConfiguration, build, public_configuration
from test_gemini_evaluation import prepared as prepared, success
from test_public_bundle import bundled as bundled, package as package, sample as sample


def test_v1_public_configuration_stays_byte_equivalent_to_existing_saved_asset():
    path = Path('web/public/evidence/configurations/eval-flash-lite-46e242a298f20b6f.json')
    existing = json.loads(path.read_text(encoding='utf-8'))
    assert public_configuration(existing['frozen_plan']) == existing
    assert FrozenConfiguration.model_validate(existing).root == existing


@pytest.mark.parametrize('model', comparison.COMPARISON_MODELS)
def test_new_configuration_keeps_settings_complete_membership_and_execution_limits(prepared, tmp_path, model):
    package, *_, clock = prepared
    plan, evidence = comparison.prepare_trial(package, model, now=clock.now())
    output = tmp_path / 'qualification'; output.mkdir()
    access = {'provider':'gemini','model_id':model,'evidence_sha256':'c'*64,
        'verified_at':'2026-10-24T00:00:00Z','valid_until':'2026-10-25T00:00:00Z',
        'free_execution_verified':True,'paid_execution_disabled':True,'terms_and_data_use_verified':True,
        'requests_per_minute':5,'input_tokens_per_minute':250000,'requests_per_day':20,'remaining_requests_today':20}
    evidence = evaluation.execute_batch(plan, evidence, package/'model-inputs', output, access,
        budget=6, send=success, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep)
    frozen, _ = comparison.prepare_evaluation(package, model, evidence, plan, now=clock.now)
    public = public_configuration(frozen)
    assert public['schema_version'] == 2 and public['frozen_plan']['model_id'] == model
    assert len(public['frozen_plan']['probes']) == 115
    assert public['effective_execution_limits']['daily_request_headroom'] == 1
    assert public['frozen_plan']['configuration']['thinking_configs'] == plan['configuration']['thinking_configs']
    for change in ('model', 'limits', 'identity', 'settings', 'version'):
        broken = deepcopy(public)
        if change == 'model': broken['frozen_plan']['model_id'] = 'unverified-model'
        if change == 'limits': broken['effective_execution_limits']['automatic_daily_reset'] = True
        if change == 'identity': broken['run_id'] = 'altered-run'
        if change == 'settings':
            broken['frozen_plan']['configuration']['thinking_configs'][model] = {'thinkingBudget':9999}
            identity = fingerprint({k:v for k,v in broken['frozen_plan'].items() if k not in {'frozen_at','run_id'}})
            broken['run_id'] = broken['frozen_plan']['run_id'] = 'eval-comparison-' + identity[:16]
        if change == 'version': broken['schema_version'] = 999
        with pytest.raises(ValueError): FrozenConfiguration.model_validate(broken)


def test_adding_models_can_keep_existing_teaching_picture_ids_and_reject_changed_assets(bundled):
    first, root, saved, output = bundled
    preserved = build(root, [saved], root/'preserved', challenge_from=output/'bundle.json')
    assert preserved['challenge']['image_ids'] == first['challenge']['image_ids']
    assert preserved['images'] == first['images']
    previous = deepcopy(first)
    previous['manifest_sha256'] = 'e'*64
    previous['bundle_id'] = 'fasteners-' + fingerprint({k:v for k,v in previous.items() if k != 'bundle_id'})[:16]
    changed = root/'invalid-previous.json'; changed.write_text(json.dumps(previous),encoding='utf-8')
    with pytest.raises(ValueError): build(root,[saved],root/'rejected',challenge_from=changed)
    assert not (root/'rejected').exists()
