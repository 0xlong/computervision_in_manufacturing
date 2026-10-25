import type { Bundle } from './types';
import { categoricalCounts } from './comparison';

export interface Playback {
  index: number;
  stage: number;
  playing: boolean;
  seen: number[];
  epoch: number;
  finished: boolean;
  filter: 'all' | 'different';
}
export type PlaybackAction = { type: 'play' | 'pause' | 'restart' } | { type: 'advance'; total: number; referenceStage: number; referenceIndex?: number } | { type: 'navigate'; index: number } | { type: 'filter'; filter: Playback['filter'] };
export const initialPlayback: Playback = { index: 0, stage: 0, playing: false, seen: [], epoch: 0, finished: false, filter: 'all' };

export function playbackReducer(state: Playback, action: PlaybackAction): Playback {
  switch (action.type) {
    case 'play': return state.finished ? state : { ...state, playing: true };
    case 'pause': return state.playing ? { ...state, playing: false } : state;
    case 'restart': return { ...initialPlayback, filter: state.filter, epoch: state.epoch + 1 };
    case 'filter': return { ...initialPlayback, filter: action.filter, epoch: state.epoch + 1 };
    case 'navigate': return { ...state, index: action.index, stage: 0, playing: false, finished: false, epoch: state.epoch + 1 };
    case 'advance':
      if (!state.playing || action.total === 0) return state;
      if (state.stage < action.referenceStage) return { ...state, stage: state.stage + 1,
        seen: state.stage + 1 === action.referenceStage ? [...new Set([...state.seen, action.referenceIndex ?? state.index])] : state.seen };
      return state.index === action.total - 1 ? { ...state, playing: false, finished: true } : { ...state, index: state.index + 1, stage: 0 };
  }
}
export function playbackCounts(bundle: Bundle, seen: number[], runId = bundle.runs[0].evidence.run.run_id, ids = bundle.challenge.image_ids) {
  const saved = bundle.runs.find(r => r.evidence.run.run_id === runId)!;
  const { correct, flagged, missed, falseAlarms, unsure, unavailable, revealed } = categoricalCounts(saved, seen.map(index => ids[index]));
  return { correct, flagged, missed, falseAlarms, unsure, unavailable, revealed };
}
