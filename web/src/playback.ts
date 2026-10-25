import type { Bundle } from './types';
import { categoricalCounts } from './comparison';

export interface Playback {
  index: number;
  stage: 0 | 1 | 2;
  playing: boolean;
  seen: number[];
  epoch: number;
  finished: boolean;
  runId: string;
  filter: 'all' | 'different';
}
export type PlaybackAction = { type: 'play' | 'pause' | 'restart' } | { type: 'advance'; total: number; referenceIndex?: number } | { type: 'navigate'; index: number } | { type: 'model'; runId: string } | { type: 'filter'; filter: Playback['filter'] };
export const initialPlayback: Playback = { index: 0, stage: 0, playing: false, seen: [], epoch: 0, finished: false, runId: '', filter: 'all' };

export function playbackReducer(state: Playback, action: PlaybackAction): Playback {
  switch (action.type) {
    case 'play': return state.finished ? state : { ...state, playing: true };
    case 'pause': return state.playing ? { ...state, playing: false } : state;
    case 'restart': return { ...initialPlayback, filter: state.filter, runId: state.runId, epoch: state.epoch + 1 };
    case 'model': return { ...initialPlayback, filter: state.filter, index: state.index, runId: action.runId, epoch: state.epoch + 1 };
    case 'filter': return { ...initialPlayback, filter: action.filter, runId: state.runId, epoch: state.epoch + 1 };
    case 'navigate': return { ...state, index: action.index, stage: 0, playing: false, finished: false, epoch: state.epoch + 1 };
    case 'advance':
      if (!state.playing || action.total === 0) return state;
      if (state.stage === 0) return { ...state, stage: 1 };
      if (state.stage === 1) return { ...state, stage: 2, seen: [...new Set([...state.seen, action.referenceIndex ?? state.index])] };
      return state.index === action.total - 1 ? { ...state, playing: false, finished: true } : { ...state, index: state.index + 1, stage: 0 };
  }
}
export function playbackCounts(bundle: Bundle, seen: number[], runId = bundle.runs[0].evidence.run.run_id) {
  const saved = bundle.runs.find(r => r.evidence.run.run_id === runId)!;
  const { flagged, missed, falseAlarms, unsure, unavailable, revealed } = categoricalCounts(saved, seen.map(index => bundle.challenge.image_ids[index]));
  return { flagged, missed, falseAlarms, unsure, unavailable, revealed };
}
