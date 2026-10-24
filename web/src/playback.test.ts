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
});
