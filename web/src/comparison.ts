import type { Bundle, Decision, SavedRun } from './types';

export function savedDecision(saved: SavedRun, imageId: string): Decision | 'unavailable' {
  const prediction = saved.evidence.predictions.find(p => p.image_id === imageId)!;
  return prediction.status === 'success' ? prediction.attempts.at(-1)!.response!.decision : 'unavailable';
}

/** Categorical predictions only. Review routing deliberately has no role here. */
export function categoricalCounts(saved: SavedRun, ids: string[]) {
  const references = new Map(saved.report.images.map(i => [i.image_id, i.label]));
  const counts = { correct: 0, flagged: 0, missed: 0, falseAlarms: 0, unsure: 0, unavailable: 0, revealed: 0, defective: 0, good: 0 };
  for (const id of new Set(ids)) {
    const label = references.get(id)!;
    const decision = savedDecision(saved, id);
    counts.revealed++;
    if (label === 'anomalous') counts.defective++; else counts.good++;
    if (decision === 'unavailable') counts.unavailable++;
    else if (decision === 'uncertain') counts.unsure++;
    else if (label === 'anomalous') {
      if (decision === 'needs_review') { counts.flagged++; counts.correct++; }
      else counts.missed++;
    } else if (decision === 'needs_review') counts.falseAlarms++;
    else counts.correct++;
  }
  return counts;
}

export function benchmarkCounts(saved: SavedRun) {
  return categoricalCounts(saved, saved.report.images.map(i => i.image_id));
}

export function differentAnswerIndices(bundle: Bundle) {
  return bundle.challenge.image_ids.flatMap((id, index) =>
    new Set(bundle.runs.map(saved => savedDecision(saved, id))).size > 1 ? [index] : []);
}

export const percentage = (count: number, total: number) => total ? `${(100 * count / total).toFixed(1)}%` : 'N/A';
