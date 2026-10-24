import Ajv2020 from 'ajv/dist/2020';
import addFormats from 'ajv-formats';
import apiSchema from '../../schemas/api-evidence.v1.schema.json';
import reportSchema from '../../schemas/evaluation-report.v1.schema.json';
import bundleSchema from '../../schemas/fastener-bundle.v2.schema.json';
import type { Bundle, Metrics } from './types';

// Canonical Draft 2020-12 contracts are shared with Python; no permissive fallback.
const ajv = new Ajv2020({ strict: false, strictNumbers: true, allErrors: false });
addFormats(ajv);
ajv.addSchema(apiSchema).addSchema(reportSchema);
const validate = ajv.compile<Bundle>(bundleSchema);
const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);
const ratio = (a: number, b: number) => b ? a / b : null;
function checkCounts(m: Metrics, counts: { tp: number; fn: number; fp: number; tn: number }) {
  function interval(actual: [number, number] | null, positive: number, total: number) {
    if (!total) return actual === null;
    if (!actual) return false;
    const z = 1.959963984540054, p = positive / total, scale = 1 + z * z / total;
    const center = (p + z * z / (2 * total)) / scale;
    const margin = z * Math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / scale;
    return Math.abs(actual[0] - Math.max(0, center - margin)) < 1e-12 && Math.abs(actual[1] - Math.min(1, center + margin)) < 1e-12;
  }
  return Object.entries(counts).every(([k, v]) => m[k as keyof typeof counts] === v) &&
    m.anomalous === counts.tp + counts.fn && m.normal === counts.fp + counts.tn &&
    m.review_count === counts.tp + counts.fp && m.recall === ratio(counts.tp, counts.tp + counts.fn) &&
    m.false_positive_rate === ratio(counts.fp, counts.fp + counts.tn) && m.precision === ratio(counts.tp, counts.tp + counts.fp) &&
    interval(m.recall_wilson_95, counts.tp, counts.tp + counts.fn) && interval(m.false_positive_rate_wilson_95, counts.fp, counts.fp + counts.tn);
}
export function parseBundle(value: unknown): Bundle {
  if (!validate(value)) throw Error('The evidence bundle is corrupt or uses an unsupported version.');
  const bundle = value;
  if (new Set(bundle.notices.map(n => n.path)).size !== 2) throw Error('Dataset notices are incomplete.');
  const images = new Map(bundle.images.map(i => [i.image_id, i]));
  if (images.size !== 5 || bundle.challenge.image_ids.some(id => !images.has(id)) ||
    bundle.images.filter(i => i.label === 'normal').length !== 2) throw Error('The five-picture challenge is inconsistent.');
  for (const i of images.values()) {
    if (i.display.path !== `images/${i.image_id}.png` || (i.mask === null) !== (i.label === 'normal') ||
      (i.mask && (i.mask.path !== `masks/${i.image_id}.png` || !same(i.mask.dimensions, i.display.dimensions)))) throw Error('An image or reference outline is inconsistent.');
  }
  const runIds = new Set<string>();
  let membership = '';
  for (const saved of bundle.runs) {
    const { run, predictions, evidence_status } = saved.evidence, report = saved.report;
    if (run.state !== 'complete' || run.track_id !== 'fasteners' || runIds.has(run.run_id) ||
      report.run_id !== run.run_id || report.model_id !== run.model_id || report.manifest_sha256 !== bundle.manifest_sha256 ||
      run.hashes.manifest !== bundle.manifest_sha256 || report.inputs_sha256 !== run.hashes.inputs) throw Error('Model and evaluation identities disagree.');
    runIds.add(run.run_id);
    if (bundle.execution === 'recorded_live' && !bundle.configuration_assets.some(c => c.run_id === run.run_id && c.path === `configurations/${run.run_id}.json`)) throw Error('The frozen run configuration is missing.');
    if ((evidence_status === 'fixture' || report.evidence_status === 'fixture') && (bundle.execution !== 'fixture' || bundle.evidence_status !== 'fixture')) throw Error('Test examples must be labelled as test examples.');
    const inputs = new Set(run.inputs.map(i => i.image_id));
    const rows = new Map(report.images.map(i => [i.image_id, i]));
    if (inputs.size !== run.inputs.length || rows.size !== report.images.length || rows.size !== inputs.size ||
      predictions.length !== rows.size || new Set(predictions.map(p => p.image_id)).size !== rows.size ||
      [...rows.keys()].some(id => !inputs.has(id))) throw Error('The complete evaluation membership is inconsistent.');
    const current = JSON.stringify([...rows.values()].map(r => [r.image_id, r.label]).sort());
    if (membership && current !== membership) throw Error('The models use different evaluation sets.');
    membership = current;
    const success = { tp: 0, fn: 0, fp: 0, tn: 0 }, routing = { ...success };
    const technical = { normal: 0, anomalous: 0 }, failures: Record<string, number> = {};
    for (const p of predictions) {
      const row = rows.get(p.image_id), a = p.attempts.at(-1);
      if (!row || !a || p.run_id !== run.run_id || p.status !== a.status || p.status === 'unknown_outcome') throw Error('A model response is incomplete.');
      const succeeded = p.status === 'success';
      const decision = succeeded ? a.response?.decision : null;
      const review = !succeeded || decision !== 'looks_acceptable';
      if (!same([row.status, row.decision, row.review, row.technical_review], [p.status, decision, review, !succeeded]) ||
        (succeeded && !a.response) || (!succeeded && a.response)) throw Error('A displayed assessment disagrees with saved evidence.');
      const key = row.label === 'anomalous' ? (review ? 'tp' : 'fn') : (review ? 'fp' : 'tn');
      routing[key]++;
      if (succeeded) success[key]++;
      else { technical[row.label]++; failures[a.reason] = (failures[a.reason] ?? 0) + 1; }
    }
    const failed = technical.normal + technical.anomalous, n = rows.size;
    if (!checkCounts(report.successful_output, success) || !checkCounts(report.full_set_routing, routing) ||
      report.expected !== n || report.attempted !== n || report.failed !== failed || report.succeeded !== n - failed ||
      report.coverage !== (n - failed) / n || !same(Object.entries(report.failure_breakdown).sort(), Object.entries(failures).sort()) ||
      !same([report.technical_reviews.normal, report.technical_reviews.anomalous], [technical.normal, technical.anomalous]) ||
      bundle.images.some(i => rows.get(i.image_id)?.label !== i.label)) throw Error('Evaluation totals disagree with the saved responses.');
  }
  if (new Set(bundle.configuration_assets.map(c => c.run_id)).size !== bundle.configuration_assets.length ||
    (bundle.execution === 'recorded_live' && bundle.configuration_assets.some(c => !runIds.has(c.run_id)))) throw Error('Frozen configuration identities disagree with the runs.');
  return bundle;
}

export async function loadBundle(signal?: AbortSignal): Promise<Bundle> {
  const response = await fetch('/evidence/bundle.json', { signal, cache: 'no-cache' });
  if (!response.ok) throw Error('Saved inspection evidence is unavailable. Prepare the local evidence bundle and retry.');
  if (Number(response.headers.get('content-length')) > 4_000_000) throw Error('The evidence bundle exceeds its supported size.');
  const text = await response.text();
  if (text.length > 4_000_000) throw Error('The evidence bundle exceeds its supported size.');
  return parseBundle(JSON.parse(text));
}
