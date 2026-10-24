export interface Playback {
  index: number;
  stage: 0 | 1 | 2;
  playing: boolean;
  seen: number[];
  epoch: number;
  finished: boolean;
}
export type PlaybackAction = { type: 'play' | 'pause' | 'restart' } | { type: 'advance'; total: number } | { type: 'navigate'; index: number };
export const initialPlayback: Playback = { index: 0, stage: 0, playing: false, seen: [], epoch: 0, finished: false };

export function playbackReducer(state: Playback, action: PlaybackAction): Playback {
  switch (action.type) {
    case 'play': return state.finished ? state : { ...state, playing: true };
    case 'pause': return state.playing ? { ...state, playing: false } : state;
    case 'restart': return { ...initialPlayback, epoch: state.epoch + 1 };
    case 'navigate': return { ...state, index: action.index, stage: 0, playing: false, finished: false, epoch: state.epoch + 1 };
    case 'advance':
      if (!state.playing) return state;
      if (state.stage === 0) return { ...state, stage: 1 };
      if (state.stage === 1) return { ...state, stage: 2, seen: [...new Set([...state.seen, state.index])] };
      return state.index === action.total - 1 ? { ...state, playing: false, finished: true } : { ...state, index: state.index + 1, stage: 0 };
  }
}
