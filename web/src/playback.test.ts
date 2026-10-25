import { describe, expect, it } from 'vitest';
import { initialPlayback, playbackCounts, playbackReducer } from './playback';
import genuine from '../public/evidence/bundle.json';
import catalog from '../public/evidence/playback.v1.json';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json';
import { parseBundle } from './bundle';

describe('sequential model playback', () => {
  it('reveals two models before the reference and counts only at the reference', () => {
    let state = initialPlayback;
    const advance = { type: 'advance' as const, total: 115, referenceStage: 3 };
    expect(state.playing).toBe(false);
    expect(playbackReducer(state, advance)).toBe(state);
    state = playbackReducer(state, { type: 'play' });
    for (const stage of [1, 2]) {
      state = playbackReducer(state, advance);
      expect(state.stage).toBe(stage); expect(state.seen).toEqual([]);
    }
    state = playbackReducer(state, { type: 'pause' });
    expect(playbackReducer(state, advance)).toBe(state);
    state = playbackReducer(state, { type: 'play' });
    state = playbackReducer(state, advance);
    expect(state).toMatchObject({ stage: 3, seen: [0], finished: false });
    for (let n = 0; n < 457; n++) state = playbackReducer(state, advance);
    expect(state).toMatchObject({ index: 114, stage: 3, seen: Array.from({ length: 115 }, (_, i) => i), playing: false, finished: true });
    expect(playbackReducer(state, { type: 'play' })).toBe(state);
  });
  it('counts each reference once and restart retains only the filter', () => {
    let state = playbackReducer(initialPlayback, { type: 'filter', filter: 'different' });
    const advance = { type: 'advance' as const, total: 2, referenceStage: 3, referenceIndex: 70 };
    for (let revisit = 0; revisit < 2; revisit++) {
      state = playbackReducer(state, { type: 'navigate', index: 0 });
      state = playbackReducer(state, { type: 'play' });
      for (let n = 0; n < 3; n++) state = playbackReducer(state, advance);
      expect(state.seen).toEqual([70]);
    }
    expect(playbackReducer(state, { type: 'restart' })).toMatchObject({ filter: 'different', index: 0, stage: 0, playing: false, seen: [], finished: false });
    expect(playbackReducer(state, { type: 'filter', filter: 'all' })).toMatchObject({ filter: 'all', playing: false, seen: [] });
  });
  it('supports a single-model fixture without inventing a second result', () => {
    let state = playbackReducer(initialPlayback, { type: 'play' });
    for (let n = 0; n < 18; n++) state = playbackReducer(state, { type: 'advance', total: 6, referenceStage: 2 });
    expect(state).toMatchObject({ finished: true, index: 5, stage: 2, seen: [0, 1, 2, 3, 4, 5] });
    const bundle = parseBundle(fixture);
    const ids = bundle.runs[0].report.images.map(i => i.image_id);
    expect(playbackCounts(bundle, state.seen, bundle.runs[0].report.run_id, ids)).toEqual({ correct: 0, flagged: 0, missed: 1, falseAlarms: 1, unsure: 1, unavailable: 3, revealed: 6 });
  });
  it('complete playback totals match categorical benchmarks for both genuine models', () => {
    const bundle = parseBundle(genuine), ids = catalog.images.map(i => i.image_id), seen = ids.map((_, n) => n);
    expect(playbackCounts(bundle, [...seen, 0], bundle.runs[0].report.run_id, ids)).toEqual({ correct: 98, flagged: 81, missed: 12, falseAlarms: 5, unsure: 0, unavailable: 0, revealed: 115 });
    expect(playbackCounts(bundle, seen, bundle.runs[1].report.run_id, ids)).toEqual({ correct: 89, flagged: 72, missed: 20, falseAlarms: 5, unsure: 1, unavailable: 0, revealed: 115 });
  });
});
