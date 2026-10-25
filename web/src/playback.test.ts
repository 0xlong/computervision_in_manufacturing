import { describe, expect, it } from 'vitest';
import { initialPlayback, playbackCounts, playbackReducer } from './playback';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json';
import { parseBundle } from './bundle';

describe('saved playback', () => {
  it('starts paused, freezes the stage and stops after five pictures', () => {
    let s = initialPlayback;
    expect(s.playing).toBe(false);
    expect(playbackReducer(s, { type: 'advance', total: 5 })).toBe(s);
    s = playbackReducer(s, { type: 'play' });
    s = playbackReducer(s, { type: 'advance', total: 5 });
    expect(s.stage).toBe(1);
    expect(s.seen).toEqual([]);
    s = playbackReducer(s, { type: 'pause' });
    expect(playbackReducer(s, { type: 'advance', total: 5 })).toBe(s);
    s = playbackReducer(s, { type: 'play' });
    for (let n = 0; n < 14; n++) s = playbackReducer(s, { type: 'advance', total: 5 });
    expect(s).toMatchObject({ index: 4, stage: 2, playing: false, finished: true, seen: [0, 1, 2, 3, 4] });
    expect(playbackReducer(s, { type: 'play' })).toBe(s);
  });
  it('counts references only once across revisits and clears them on restart', () => {
    let s = playbackReducer(initialPlayback, { type: 'play' });
    s = playbackReducer(s, { type: 'advance', total: 5 });
    expect(s.seen).toEqual([]);
    s = playbackReducer(s, { type: 'advance', total: 5 });
    expect(s.seen).toEqual([0]);
    s = playbackReducer(s, { type: 'navigate', index: 0 });
    expect(s.playing).toBe(false);
    s = playbackReducer(s, { type: 'play' });
    for (let n = 0; n < 2; n++) s = playbackReducer(s, { type: 'advance', total: 5 });
    expect(s.seen).toEqual([0]);
    s = playbackReducer(s, { type: 'restart' });
    expect(s).toMatchObject({ index: 0, stage: 0, playing: false, seen: [] });
  });
  it('separates uncertain responses and unavailable answers from categorical counts', () => {
    const bundle = parseBundle(structuredClone(fixture));
    expect(playbackCounts(bundle, [])).toEqual({ flagged: 0, missed: 0, falseAlarms: 0, unsure: 0, unavailable: 0, revealed: 0 });
    expect(playbackCounts(bundle, [0, 1, 2, 3, 4, 0, 3])).toEqual({ flagged: 0, missed: 1, falseAlarms: 1, unsure: 1, unavailable: 2, revealed: 5 });
  });
  it('switches model on the same picture paused, clears counts, and counts the selected response', () => {
    const state = { ...initialPlayback, index: 3, stage: 2 as const, playing: true, seen: [0, 3], runId: 'previous' };
    const switched = playbackReducer(state, { type: 'model', runId: 'next' });
    expect(switched).toMatchObject({ index: 3, stage: 0, playing: false, seen: [], runId: 'next' });
    expect(playbackReducer(switched, { type: 'restart' })).toMatchObject({ index: 0, runId: 'next', seen: [] });
    const bundle = parseBundle(structuredClone(fixture));
    const second = structuredClone(bundle.runs[0]);
    second.evidence.run.run_id = 'unit-second-run';
    bundle.runs.push(second); // Isolated counter input; not a public evidence artifact.
    // Select the normal first challenge picture, originally needs_review.
    const normalId = bundle.challenge.image_ids[0];
    second.evidence.predictions.find(p => p.image_id === normalId)!.attempts.at(-1)!.response!.decision = 'looks_acceptable';
    expect(playbackCounts(bundle, [0], second.evidence.run.run_id).falseAlarms).toBe(0);
    expect(playbackCounts(bundle, [0], bundle.runs[0].evidence.run.run_id).falseAlarms).toBe(1);
  });
});
