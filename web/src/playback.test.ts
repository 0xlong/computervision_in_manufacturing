import { describe, expect, it } from 'vitest';
import { initialPlayback, playbackReducer } from './playback';

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
});
