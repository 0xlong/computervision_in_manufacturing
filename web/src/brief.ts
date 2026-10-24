import { projections } from './engine';
import type { Bundle } from './types';
import type { VisitorState } from './state';
import { restoreState } from './state';

export const prerequisites = [
  'Representative site images', 'A named quality owner', 'Approved data access',
  'Agreed defect and disposition definitions', 'Agreed acceptance criteria',
  'Sufficient human review capacity', 'Human oversight and a stop procedure',
];
const safeText = (text: string) => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
  .replace(/[\\`*_{}\[\]()#+.!|~-]/g, '\\$&').split(/\r?\n/).map(line => `> ${line}`).join('\n');

export function buildBrief(bundle: Bundle, state: VisitorState): string {
  const checked = restoreState(JSON.stringify(state), bundle);
  if (checked.notice || !state.decision) throw Error('Choose a pilot decision and valid assumptions before export.');
  const selected = bundle.runs.find(r => r.evidence.run.run_id === state.selectedRun);
  if (!selected) throw Error('Selected evidence is unavailable.');
  const { report, evidence } = selected;
  const p = projections(state.scenario, report.full_set_routing);
  if (!p) throw Error('Valid assumptions and both evaluated classes are required for export.');
  const s = state.scenario, r = evidence.run;
  const number = (value: number | null) => value === null ? 'N/A' : String(value);
  const lines = [
    '# AI Inspection Pilot Lab — pilot brief', '',
    `Bundle: ${bundle.bundle_id}; evidence status: ${bundle.evidence_status}; execution: ${bundle.execution}.`,
    `Track: fasteners; dataset: ${bundle.dataset.dataset_id}; category: ${bundle.dataset.category}.`,
    `Run: ${r.run_id}; provider: ${r.provider}; model: ${r.model_id}; created: ${r.created_at}.`,
    `Reported model versions: ${[...new Set(evidence.predictions.flatMap(p => p.attempts.map(a => a.reported_model_version).filter(Boolean)))].sort().join(', ')}. Provider aliases can change.`,
    `Policy: ${r.policy}. Uncertain and technical failures route to human review.`,
    '', '## Measured evidence', '',
    `Expected: ${report.expected}; attempted: ${report.attempted}; successful: ${report.succeeded}; failed: ${report.failed}; coverage: ${number(report.coverage)}.`,
    `Successful assessments: misses ${report.successful_output.fn}/${report.successful_output.anomalous}; false alarms ${report.successful_output.fp}/${report.successful_output.normal}; reviews ${report.successful_output.review_count}.`,
    `Full-set routing: misses ${report.full_set_routing.fn}/${report.full_set_routing.anomalous}; normal reviews ${report.full_set_routing.fp}/${report.full_set_routing.normal}; all reviews ${report.full_set_routing.review_count}.`,
    `Technical reviews: ${report.technical_reviews.anomalous} anomalous, ${report.technical_reviews.normal} normal.`,
    `Routing recall: ${number(report.full_set_routing.recall)}; routing false-positive rate: ${number(report.full_set_routing.false_positive_rate)}.`,
    `95% Wilson intervals: recall ${JSON.stringify(report.full_set_routing.recall_wilson_95)}; false-positive rate ${JSON.stringify(report.full_set_routing.false_positive_rate_wilson_95)}.`,
    `Failure breakdown: ${JSON.stringify(Object.fromEntries(Object.entries(report.failure_breakdown).sort(([a], [b]) => a.localeCompare(b))))}.`,
    '', '## Illustrative assumptions and daily projections', '',
    `Components/day: ${s.volume}; assumed defective proportion: ${s.prevalence}; minutes/review: ${s.minutes}; available review minutes/day: ${s.capacity}.`,
    `EUR/review minute: ${s.reviewCost}; EUR/missed defect: ${s.missedCost}.`,
    `Expected caught: ${p.caught}; misses: ${p.missed}; unnecessary reviews: ${p.unnecessaryReviews}; all reviews: ${p.reviews}.`,
    `Review minutes: ${p.reviewMinutes}; excess capacity minutes: ${p.capacityExcess}; review cost EUR: ${p.reviewCost}; illustrative total cost EUR: ${p.totalCost}.`,
    'Assumes every flag is reviewed, human review resolves flags correctly, and each missed defect incurs the entered average cost. Capacity excess is a warning, not a queue simulation.',
    '', '## Visitor conclusion', '', state.decision, '', safeText(state.rationale || 'No rationale provided.'),
    '', 'This is a visitor choice, not an automatically validated recommendation.',
    `Challenge answers: ${Object.keys(state.answers).length}/5. Five curated examples do not establish human or model superiority.`,
    '', '## Provenance', '',
    `Manifest SHA-256: ${bundle.manifest_sha256}`, `Evaluation membership SHA-256: ${report.membership_sha256}`,
    `Evidence SHA-256: ${report.evidence_sha256}`,
    ...bundle.configuration_assets.filter(c => c.run_id === r.run_id).map(c => `Frozen configuration: ${c.path}; SHA-256: ${c.sha256}`),
    ...Object.keys(r.hashes).sort().map(key => `${key} SHA-256: ${r.hashes[key]}`),
    `Challenge version: ${bundle.challenge.version}`, safeText(bundle.challenge.rationale),
    '', '## Limitations', '',
    ...[...new Set([...bundle.limitations, ...report.limitations])].map(safeText),
    '', '## Pilot prerequisites', '', ...prerequisites.map(item => `- [ ] ${item}`),
    '', '## Dataset attribution', '', safeText(bundle.dataset.attribution),
    `${bundle.dataset.licence}: ${bundle.dataset.licence_url}`, `Source: ${bundle.dataset.source_url}`,
    safeText(bundle.dataset.modification_notice),
    '', 'Generated locally from saved evidence and visitor state. No provider request or transmission of visitor state.', '',
  ];
  return lines.join('\n');
}
