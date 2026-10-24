import { expect, it } from 'vitest';
import { answerImage, freshState, loadState, restoreState, revealImage, storageKey } from './state';
import type { Bundle } from './types';

// Minimal state-test contract, not image/model evidence and never served by the app.
const bundle = { bundle_id: 'test-state-contract', challenge: { image_ids: ['img-000001', 'img-000002'] },
  runs: [{ evidence: { run: { run_id: 'test-model-a' } } }, { evidence: { run: { run_id: 'test-model-b' } } }] } as Bundle;

it('requires an answer before reveal and fixes revealed answers across navigation', () => {
  const initial = freshState(bundle);
  expect(revealImage(initial, 'img-000001')).toBe(initial);
  const answered = answerImage(initial, 'img-000001', 'needs_review');
  expect(answerImage(answered, 'img-000001', 'looks_acceptable').answers['img-000001']).toBe('looks_acceptable');
  const revealed = revealImage(answered, 'img-000001');
  expect(answerImage(revealed, 'img-000001', 'looks_acceptable')).toBe(revealed);
  const navigated = { ...revealed, selectedImage: 'img-000002', selectedRun: 'test-model-b', screen: 'lab' as const };
  expect(restoreState(JSON.stringify(navigated), bundle).state).toEqual(navigated);
});

it('keeps scenario and rationale through refresh without storing identity or keys', () => {
  const state = freshState(bundle);
  state.scenario.capacity = 0;
  state.scenario.minutes = .25;
  state.rationale = '<script>TEST ONLY</script>';
  state.decision = 'Collect more evidence';
  expect(restoreState(JSON.stringify(state), bundle).state).toEqual(state);
  expect(Object.keys(state)).not.toContain('credentials');
});

it.each(['{broken', 'null', JSON.stringify({ schema_version: 999 }), JSON.stringify([])])('recovers corrupt/unsupported progress: %s', raw => {
  expect(restoreState(raw, bundle).state).toEqual(freshState(bundle));
  expect(restoreState(raw, bundle).notice).not.toBe('');
});

it('visibly restarts progress on evidence updates and rejects revealed unanswered images', () => {
  const state = freshState(bundle);
  expect(restoreState(JSON.stringify({ ...state, bundle_id: 'old' }), bundle).notice).toContain('bundle changed');
  expect(restoreState(JSON.stringify({ ...state, revealed: ['img-000001'] }), bundle).notice).toContain('could not be read');
  expect(restoreState(JSON.stringify({ ...state, answers: { 'img-999999': 'needs_review' } }), bundle).notice).toContain('could not be read');
  expect(restoreState(JSON.stringify({ ...state, scenario: { ...state.scenario, prevalence: 2 } }), bundle).notice).not.toBe('');
  expect(restoreState(JSON.stringify({ ...state, rationale: 'a'.repeat(2001) }), bundle).notice).not.toBe('');
});

it('uses memory when browser storage is blocked and reads only its own key', () => {
  expect(loadState({ getItem: () => { throw Error(); }, setItem: () => {} }, bundle).persistent).toBe(false);
  let read = '';
  expect(loadState({ getItem: key => { read = key; return null; }, setItem: () => {} }, bundle).state).toEqual(freshState(bundle));
  expect(read).toBe(storageKey);
});
