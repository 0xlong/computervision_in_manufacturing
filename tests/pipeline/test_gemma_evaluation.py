"""Generated inputs/fake answers only. No credentials/network."""

from copy import deepcopy
from datetime import timedelta

import pytest

from pipeline import probe_gemma
from pipeline import run_gemma_evaluation as runner
from pipeline import run_gemini_trial as common
from pipeline.api_contracts import request_fingerprint
from pipeline.gemini_transport import outcome
from pipeline.public_bundle import public_configuration, FrozenConfiguration
from test_gemini_evaluation import prepared as prepared, success


def setup(prepared):
    package, _, _, _, _, _, access, clock = prepared
    plan, trial = probe_gemma.prepare(package, probe_gemma.MODELS[0], now=clock.now())
    access.update(model_id=probe_gemma.MODELS[0], requests_per_minute=30, input_tokens_per_minute=16000,
                  requests_per_day=14400, remaining_requests_today=14400)
    roots = (package.parent / 'gemma-probes', package.parent / 'gemma-evaluations')
    normal = roots[0] / trial['run']['run_id']; normal.mkdir(parents=True)
    common.execute(plan, trial, package / 'model-inputs', normal, access, send=success,
        now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep)
    evaluation, evidence = runner.prepare(package, trial, plan, now=clock.now)
    output = roots[1] / evaluation['run_id']; output.mkdir(parents=True)
    common.save(output, evidence)
    return package, trial, plan, evaluation, evidence, output, access, clock, roots


def batch(data, send=success, budget=12):
    package, _, _, plan, evidence, output, access, clock, roots = data
    return runner.execute_batch(plan, evidence, package / 'model-inputs', output, access, roots,
        budget=budget, send=send, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep)


def test_prepare_freezes_same_115_members_prompt_reference_and_minimal(prepared):
    package, trial, normal_plan, plan, evidence, _, _, clock, _ = setup(prepared)
    assert runner.prepare(package, trial, normal_plan, now=clock.now)[0] == plan
    assert len(plan['probes']) == len(evidence['predictions']) == 115
    assert plan['reference'] == prepared[3]['reference']
    assert plan['configuration']['prompt'] == prepared[3]['configuration']['prompt']
    assert plan['configuration']['reserved_input_tokens_per_request'] == 4096
    assert common.build_payload(plan, plan['probes'][0], package / 'model-inputs')['generationConfig']['thinkingConfig'] == {'thinkingLevel':'minimal'}
    assert evidence['predictions'][0]['request_sha256'] == request_fingerprint(evidence['run'], evidence['run']['inputs'][0])
    assert not (package / 'evaluator').exists()
    changed = deepcopy(normal_plan); changed['configuration']['prompt'] += ' altered'
    with pytest.raises(ValueError): runner.prepare(package, trial, changed)
    trial['predictions'][0]['attempts'][-1]['reported_model_version'] = None
    with pytest.raises(ValueError): runner.prepare(package, trial, normal_plan)


def test_full_fake_run_resumes_without_duplicate_successes_and_paces_across_phases(prepared):
    data = setup(prepared)
    starts = []
    def send(*_):
        persisted = common.read_json(data[5] / 'evidence.json')
        assert any(p['status']=='unknown_outcome' for p in persisted['predictions'])
        starts.append(data[7].now())
        return success()
    for _ in range(10): batch(data, send)
    batch(data, send)
    assert len(starts) == 115 and data[4]['run']['state']=='complete'
    normal_last = data[1]['predictions'][-1]['attempts'][-1]['started_at']
    assert starts[0].timestamp() - runner.timestamp(normal_last) >= 10
    assert all((b-a).total_seconds() >= 10 for a,b in zip(starts,starts[1:]))


def test_rolling_window_reserves_next_request_and_counts_failed_usage(prepared):
    data=setup(prepared); clock=data[7]; access=data[6]
    def attempt(age, status='success', tokens=4000):
        return {'started_at':common.stamp(clock.now()-timedelta(seconds=age)), 'status':status,
                'usage':{'input_tokens':tokens}, 'retry_not_before':None}
    ledger=[attempt(30), attempt(20), attempt(10, 'timeout')]
    earliest=runner.earliest_start(ledger, access, clock.now())
    assert earliest > clock.now().timestamp()+30
    assert earliest < clock.now().timestamp()+31
    ledger[0]['usage']['input_tokens']=50
    assert runner.earliest_start(ledger, access, clock.now()) == clock.now().timestamp()
    # Retry windows apply across models/phases even if token headroom exists.
    ledger[0]['retry_not_before']=common.stamp(clock.now()+timedelta(hours=1))
    assert runner.earliest_start(ledger,access,clock.now()) >= clock.now().timestamp()+3600


def test_token_heavy_answers_wait_for_window_expiry_before_advancing(prepared):
    data=setup(prepared); starts=[]; waits=[]
    def send(*_):
        starts.append(data[7].now().timestamp())
        result=success(); result['usage']['input_tokens']=4000
        return result
    original_sleep=data[7].sleep
    def sleep(seconds):
        waits.append(seconds)
        assert len(waits)<1000, 'Timer must advance at fractional window boundaries'
        original_sleep(seconds)
    data[7].sleep=sleep
    batch(data,send,budget=8)
    assert len(starts)==8 and any(b-a>10 for a,b in zip(starts,starts[1:]))
    for index,start in enumerate(starts):
        assert sum(4000 for old in starts[:index] if old+60>=start)+4096<16000


@pytest.mark.parametrize('kind', ['unknown', 'oversize', 'missing', 'timeout', 'quota', 'auth'])
def test_failures_remain_honest_and_bounded(prepared, kind):
    data=setup(prepared); calls=[]
    def send(*_):
        calls.append(1)
        if kind=='unknown': return outcome('unknown_outcome','interrupted')
        if kind=='timeout': return outcome('timeout','timeout')
        if kind=='quota':
            result=outcome('provider_error','quota')
            result['retry_not_before']=common.stamp(data[7].now()+timedelta(days=1))
            return result
        if kind=='auth': return outcome('provider_error','authentication')
        result=success(); result['usage']['input_tokens']=4097 if kind=='oversize' else None
        return result
    batch(data,send,budget=3)
    assert len(calls)==(3 if kind=='timeout' else 1)
    assert data[4]['run']['state']==('paused' if kind in {'timeout','quota'} else 'stopped')
    if kind not in {'timeout','quota'}:
        batch(data,send)
        assert len(calls)==1
    assert sum(p['execution_state']=='pending' for p in data[4]['predictions']) >= 114


def test_current_shared_daily_allowance_and_stale_access_pause_without_calls(prepared):
    data=setup(prepared); calls=[]
    data[6]['remaining_requests_today']=3  # Two normal submissions across the shared ledger leave one.
    batch(data, lambda *_:calls.append(1))
    assert not calls and data[4]['run']['state']=='paused'
    data[6]['remaining_requests_today']=14400
    data[6]['valid_until']=common.stamp(data[7].now())
    batch(data,lambda *_:calls.append(1))
    assert not calls and all(p['status'] is None for p in data[4]['predictions'])


def test_unknown_in_another_gemma_run_stops_before_new_submission(prepared):
    data=setup(prepared)
    saved=deepcopy(data[1]); saved['predictions'][-1]['attempts'][0].update(outcome('unknown_outcome','interrupted'), finished_at=None,latency_ms=None)
    saved['predictions'][-1]['status']='unknown_outcome'; saved['run']['state']='stopped'
    common.save(data[8][0] / saved['run']['run_id'],saved)
    batch(data,lambda *_:pytest.fail('Unknown shared-ledger outcome must stop requests'))
    assert data[4]['run']['state']=='stopped'


def test_public_gemma_configuration_preserves_frozen_request_and_token_policy(prepared):
    data=setup(prepared)
    artifact=public_configuration(data[3])
    assert artifact['schema_version']==3
    assert artifact['frozen_plan']==data[3]
    assert artifact['effective_execution_limits']['input_reservation']==4096
    assert FrozenConfiguration.model_validate(artifact).root==artifact
    artifact['effective_execution_limits']['input_reservation']=16000
    with pytest.raises(ValueError): FrozenConfiguration.model_validate(artifact)


@pytest.mark.parametrize('budget', [0,13,True])
def test_invalid_batch_budget_never_submits(prepared,budget):
    data=setup(prepared)
    with pytest.raises(ValueError): batch(data,lambda *_:pytest.fail('No submission'),budget)
