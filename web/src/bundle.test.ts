import { expect, it } from 'vitest';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json';
import { parseBundle } from './bundle';
import { buildBrief } from './brief';
import { freshState } from './state';

it('uses the same checked Python fixture and canonical schema', () => {
  const b = parseBundle(structuredClone(fixture));
  expect(b.execution).toBe('fixture');
  expect(b.images).toHaveLength(5);
  expect(b.runs[0].report.expected).toBe(6);
  expect(b.runs[0].report.full_set_routing.fn).toBe(1);
});

it.each(['version', 'missing', 'unsafe', 'metrics', 'coverage', 'wilson', 'fixture', 'identity', 'infinite'])('rejects bad bundle: %s', change => {
  const data = structuredClone(fixture);
  if (change === 'version') data.schema_version = 999;
  if (change === 'missing') data.runs[0].report.images.pop();
  if (change === 'unsafe') data.images[0].display.path = 'https://example.invalid/private.png';
  if (change === 'metrics') data.runs[0].report.full_set_routing.fn++;
  if (change === 'coverage') data.runs[0].report.succeeded++;
  if (change === 'wilson') data.runs[0].report.full_set_routing.recall_wilson_95 = [0, 1];
  if (change === 'fixture') data.execution = 'recorded_live';
  if (change === 'identity') data.manifest_sha256 = 'a'.repeat(64);
  if (change === 'infinite') data.runs[0].report.full_set_routing.recall = Infinity;
  expect(() => parseBundle(data)).toThrow();
});

it('exports deterministic current evidence/assumptions and escapes untrusted text', () => {
  const bundle = parseBundle(structuredClone(fixture)), state = freshState(bundle);
  state.decision = 'Collect more evidence';
  state.rationale = '<script>alert(1)</script>\n[click](javascript:alert(2))';
  state.scenario.capacity = 0;
  const text = buildBrief(bundle, state);
  expect(buildBrief(bundle, structuredClone(state))).toBe(text);
  expect(text).toContain(bundle.runs[0].evidence.run.run_id);
  expect(text).toContain('coverage: 0.5');
  expect(text).toContain('available review minutes/day: 0');
  expect(text).toContain('fixture');
  expect(text).toContain('Representative site images');
  expect(text).not.toContain('<script>');
  expect(text).not.toContain('[click](javascript:');
  expect(text).toContain('&lt;script&gt;');
});

it('suspends export for invalid assumptions, missing decision or incompatible state', () => {
  const bundle = parseBundle(structuredClone(fixture)), state = freshState(bundle);
  expect(() => buildBrief(bundle, state)).toThrow();
  state.decision = 'Pilot with human review'; state.scenario.volume = NaN;
  expect(() => buildBrief(bundle, state)).toThrow();
  state.scenario.volume = 1000; state.bundle_id = 'changed';
  expect(() => buildBrief(bundle, state)).toThrow();
});
