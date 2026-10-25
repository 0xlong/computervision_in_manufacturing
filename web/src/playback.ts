import type { Bundle } from './types';

export interface Playback {
  index: number;
  stage: 0 | 1 | 2;
  playing: boolean;
  seen: number[];
  epoch: number;
  finished: boolean;
  runId: string;
}
export type PlaybackAction = { type: 'play' | 'pause' | 'restart' } | { type: 'advance'; total: number } | { type: 'navigate'; index: number } | { type: 'model'; runId: string };
export const initialPlayback: Playback = { index: 0, stage: 0, playing: false, seen: [], epoch: 0, finished: false, runId: '' };

export function playbackReducer(state: Playback, action: PlaybackAction): Playback {
  switch (action.type) {
    case 'play': return state.finished ? state : { ...state, playing: true };
    case 'pause': return state.playing ? { ...state, playing: false } : state;
    case 'restart': return { ...initialPlayback, runId: state.runId, epoch: state.epoch + 1 };
    case 'model': return { ...initialPlayback, index: state.index, runId: action.runId, epoch: state.epoch + 1 };
    case 'navigate': return { ...state, index: action.index, stage: 0, playing: false, finished: false, epoch: state.epoch + 1 };
    case 'advance':
      if (!state.playing) return state;
      if (state.stage === 0) return { ...state, stage: 1 };
      if (state.stage === 1) return { ...state, stage: 2, seen: [...new Set([...state.seen, state.index])] };
      return state.index === action.total - 1 ? { ...state, playing: false, finished: true } : { ...state, index: state.index + 1, stage: 0 };
  }
}
export function playbackCounts(bundle: Bundle, seen: number[], runId = bundle.runs[0].evidence.run.run_id) {
  const saved = bundle.runs.find(r => r.evidence.run.run_id === runId)!;
  const counts = { flagged: 0, missed: 0, falseAlarms: 0, unsure: 0, unavailable: 0, revealed: 0 };
  for (const index of new Set(seen)) {
    const id = bundle.challenge.image_ids[index];
    const image = bundle.images.find(i => i.image_id === id)!;
    const prediction = saved.evidence.predictions.find(p => p.image_id === id)!;
    const response = prediction.status === 'success' ? prediction.attempts.at(-1)!.response : null;
    counts.revealed++;
    if (!response) counts.unavailable++;
    else if (response.decision === 'uncertain') counts.unsure++;
    else if (image.label === 'anomalous') {
      if (response.decision === 'needs_review') counts.flagged++;
      else counts.missed++;
    } else if (response.decision === 'needs_review') counts.falseAlarms++;
  }
  return counts;
}
