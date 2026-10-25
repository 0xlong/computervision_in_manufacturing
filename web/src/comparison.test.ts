import { describe, expect, it } from 'vitest';
import genuine from '../public/evidence/bundle.json';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json';
import { parseBundle } from './bundle';
import { benchmarkCounts, differentAnswerIndices, percentage } from './comparison';
import { initialPlayback, playbackCounts, playbackReducer } from './playback';

describe('categorical comparison against saved evidence', () => {
  it('recounts both complete genuine benchmarks, excluding Gemma uncertainty from correct decisions', () => {
    const bundle = parseBundle(genuine);
    const baseline = benchmarkCounts(bundle.runs[0]);
    const gemma = benchmarkCounts(bundle.runs[1]);
    expect(baseline).toEqual({ correct: 98, flagged: 81, missed: 12, falseAlarms: 5, unsure: 0, unavailable: 0, revealed: 115, defective: 93, good: 22 });
    expect(gemma).toEqual({ correct: 89, flagged: 72, missed: 20, falseAlarms: 5, unsure: 1, unavailable: 0, revealed: 115, defective: 93, good: 22 });
    expect(percentage(baseline.correct, 115)).toBe('85.2%');
    expect(percentage(gemma.correct, 115)).toBe('77.4%');
    expect(gemma.correct).not.toBe(bundle.runs[1].report.successful_output.tp + bundle.runs[1].report.successful_output.tn);
    // Every record's outcome is accounted for, including unknown/failure categories.
    for (const saved of bundle.runs) {
      const c = benchmarkCounts(saved);
      expect(c.correct + c.missed + c.falseAlarms + c.unsure + c.unavailable).toBe(saved.report.expected);
    }
  });
  it('uses all class members as denominators, including failures, and preserves unavailable timing', () => {
    const bundle = parseBundle(fixture);
    expect(benchmarkCounts(bundle.runs[0])).toEqual({ correct: 0, flagged: 0, missed: 1, falseAlarms: 1, unsure: 1, unavailable: 3, revealed: 6, defective: 3, good: 3 });
    expect(percentage(0, 0)).toBe('N/A');
    expect(differentAnswerIndices(bundle)).toEqual([]);
  });
  it('filters by categorical answer, not observations, and preserves complete benchmark scores', () => {
    const bundle = parseBundle(structuredClone(genuine));
    const before = bundle.runs.map(benchmarkCounts);
    expect(differentAnswerIndices(bundle)).toEqual([0, 2]);
    let state = playbackReducer(initialPlayback, { type: 'filter', filter: 'different' });
    state = playbackReducer(state, { type: 'play' });
    const indices = differentAnswerIndices(bundle);
    for (let n = 0; n < 6; n++) state = playbackReducer(state, { type: 'advance', total: 2, referenceIndex: indices[state.index] });
    expect(state).toMatchObject({ finished: true, playing: false, seen: [0, 2] });
    expect(playbackCounts(bundle, state.seen, bundle.runs[0].report.run_id)).toMatchObject({ flagged: 0, missed: 0, falseAlarms: 2, revealed: 2 });
    expect(playbackCounts(bundle, state.seen, bundle.runs[1].report.run_id)).toMatchObject({ flagged: 0, missed: 0, falseAlarms: 0, revealed: 2 });
    expect(bundle.runs.map(benchmarkCounts)).toEqual(before);
    expect(playbackReducer(state, { type: 'restart' })).toMatchObject({ filter: 'different', playing: false, seen: [], finished: false, index: 0 });
    expect(playbackReducer({ ...state, playing: true }, { type: 'filter', filter: 'all' })).toMatchObject({ filter: 'all', playing: false, seen: [], index: 0, stage: 0 });
  });
  it('treats unsure, unavailable and categorical answers as different, but two failures as the same category', () => {
    const bundle = parseBundle(structuredClone(fixture));
    const second = structuredClone(bundle.runs[0]);
    bundle.runs.push(second); // Pure-function input only; never packaged as authentic evidence.
    const uncertain = second.evidence.predictions.find(p => p.attempts.at(-1)?.response?.decision === 'uncertain')!;
    uncertain.attempts.at(-1)!.response!.decision = 'needs_review';
    const unavailable = second.evidence.predictions.find(p => p.status === 'invalid_response')!;
    unavailable.status = 'timeout';
    const uncertainIndex = bundle.challenge.image_ids.indexOf(uncertain.image_id);
    expect(differentAnswerIndices(bundle)).toEqual([uncertainIndex]);
    unavailable.status = 'success';
    unavailable.attempts.at(-1)!.response = { decision: 'uncertain', observation: 'Generated test answer' };
    expect(differentAnswerIndices(bundle)).toEqual([uncertainIndex, bundle.challenge.image_ids.indexOf(unavailable.image_id)].sort());
  });
});
