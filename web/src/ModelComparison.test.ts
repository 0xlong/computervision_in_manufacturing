import { expect, it } from 'vitest';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json';
import { parseBundle } from './bundle';
import { requestTimes } from './ModelComparison';

it('includes failed and retried requests in median timing, preserving missing measurements', () => {
  const saved = parseBundle(structuredClone(fixture)).runs[0];
  const attempt = saved.evidence.predictions[0].attempts[0];
  saved.evidence.predictions[0].attempts = [{ ...attempt, latency_ms: 1000 }, { ...attempt, latency_ms: 5000 }];
  saved.evidence.predictions.slice(1).forEach(p => { p.attempts = [{ ...p.attempts[0], latency_ms: null }]; });
  saved.evidence.predictions[1].attempts[0].latency_ms = 60000;
  saved.evidence.predictions[1].status = 'timeout';
  expect(requestTimes(saved)).toEqual({ median: 5000, measured: 3, total: 7 });
  saved.evidence.predictions[1].attempts[0].latency_ms = null;
  expect(requestTimes(saved)).toEqual({ median: 3000, measured: 2, total: 7 });
  saved.evidence.predictions.forEach(p => p.attempts.forEach(a => { a.latency_ms = null; }));
  expect(requestTimes(saved)).toEqual({ median: null, measured: 0, total: 7 });
});
