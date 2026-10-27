import { useState } from 'react';
import { defaultScenario, formatNumber, projections, scenarioErrors, scenarioLabels } from './engine';
import type { Scenario } from './engine';
import { buildBrief, prerequisites } from './brief';
import { pilotDecisions } from './types';
import type { Bundle, Metrics, PilotDecision } from './types';
import type { VisitorState } from './state';
import { ModelComparison } from './ModelComparison';

function MetricsView({ name, metrics }: { name: string; metrics: Metrics }) {
  return <section className="metric-card"><h3>{name}</h3><dl>
    <div><dt>Missed defects</dt><dd>{metrics.fn} / {metrics.anomalous} anomalous</dd></div>
    <div><dt>Normal items sent to review</dt><dd>{metrics.fp} / {metrics.normal} normal</dd></div>
    <div><dt>All reviews</dt><dd>{metrics.review_count} / {metrics.anomalous + metrics.normal}</dd></div>
    <div><dt>Recall</dt><dd>{metrics.recall === null ? 'N/A' : `${formatNumber(metrics.recall * 100)}%`}</dd></div>
    <div><dt>Precision</dt><dd>{metrics.precision === null ? 'N/A' : `${formatNumber(metrics.precision * 100)}%`}</dd></div>
    <div><dt>False-positive rate</dt><dd>{metrics.false_positive_rate === null ? 'N/A' : `${formatNumber(metrics.false_positive_rate * 100)}%`}</dd></div>
  </dl><p className="small">95% Wilson intervals: recall {metrics.recall_wilson_95?.map(n => `${formatNumber(n * 100)}%`).join(' to ') ?? 'N/A'};
    {' '}false-positive rate {metrics.false_positive_rate_wilson_95?.map(n => `${formatNumber(n * 100)}%`).join(' to ') ?? 'N/A'}.
    These intervals do not cover dataset shift or benchmark contamination.</p></section>;
}

export function Lab({ bundle, state, update }: { bundle: Bundle; state: VisitorState; update: (patch: Partial<VisitorState>) => void }) {
  const saved = bundle.runs.find(r => r.evidence.run.run_id === state.selectedRun)!;
  const { report, evidence } = saved;
  const [drafts, setDrafts] = useState(() => Object.fromEntries(Object.entries(state.scenario).map(([k, v]) => [k, String(v)])));
  const [exportError, setExportError] = useState('');
  const errors = scenarioErrors(state.scenario), projected = projections(state.scenario, report.full_set_routing);
  function exportBrief() {
    try {
      const text = buildBrief(bundle, state);
      const url = URL.createObjectURL(new Blob([text], { type: 'text/markdown;charset=utf-8' }));
      const link = document.createElement('a'); link.href = url; link.download = `inspection-pilot-${bundle.bundle_id}.md`;
      link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); setExportError('');
    } catch { setExportError('The brief needs valid evidence, assumptions and a selected decision.'); }
  }
  return <>
    <section className="section-heading"><h1>Results</h1></section>
    <ModelComparison bundle={bundle} selectedRun={state.selectedRun} onSelect={id => update({ selectedRun: id, comparisonRun: '' })} />
    <details className="detailed-results"><summary>Detailed results</summary>
    <label className="model-select">Saved model <select value={state.selectedRun} onChange={e => update({ selectedRun: e.target.value, comparisonRun: '' })}>
      {bundle.runs.map(r => <option value={r.evidence.run.run_id} key={r.evidence.run.run_id}>{r.evidence.run.model_id}</option>)}
    </select></label>
    <p><strong>{report.succeeded} successful assessments / {report.expected} expected images</strong> ({formatNumber((report.coverage ?? 0) * 100)}% coverage).
      {' '}{report.attempted} attempted; {report.failed} technical failures.</p>
    <div className="metric-grid"><MetricsView name="Successful AI assessments" metrics={report.successful_output} />
      <MetricsView name="Complete-set review routing" metrics={report.full_set_routing} /></div>
    <p className="small">Technical failures add {report.technical_reviews.anomalous} anomalous and {report.technical_reviews.normal} normal items to review.
      {' '}Failure reasons: {Object.entries(report.failure_breakdown).map(([k, n]) => `${k}: ${n}`).join('; ') || 'none'}.
      Routing sends needs_review, uncertain and technical failures to a person. It is not successful model prediction on failed requests.</p>
    <p className="notice">Fixed API policy. Adjustable sensitivity, calibrated defect probabilities and AI heatmaps are unavailable. Controls make no model requests.</p>
    </details>
    <details className="workday-tools"><summary>Explore a workday &amp; download a brief{Object.keys(errors).length > 0 ? ' — check your inputs' : ''}</summary>
    <section className="scenario"><div><h2>What would a workday look like?</h2>
      <p>Defaults are illustrative, in EUR. These are not site measurements or measured savings.</p></div>
      <div className="scenario-layout"><fieldset><legend>Daily workload assumptions</legend>
        {(Object.keys(defaultScenario) as (keyof Scenario)[]).map(key => <label key={key} htmlFor={`scenario-${key}`}>
          {scenarioLabels[key]}<input id={`scenario-${key}`} type="text" inputMode={key === 'volume' ? 'numeric' : 'decimal'}
            value={drafts[key]} aria-label={scenarioLabels[key]} aria-invalid={Boolean(errors[key])} aria-describedby={errors[key] ? `error-${key}` : undefined}
            onChange={e => { setDrafts(s => ({ ...s, [key]: e.target.value })); update({ scenario: { ...state.scenario, [key]: e.target.value.trim() === '' ? NaN : Number(e.target.value) } }); }} />
          {errors[key] && <span className="field-error" id={`error-${key}`}>{errors[key]}</span>}
        </label>)}
      </fieldset><div className="projection" aria-live="polite" aria-atomic="true">
        <h3>Expected per day</h3>{projected ? <dl>
          <div><dt>Missed defects</dt><dd>{formatNumber(projected.missed)}</dd></div>
          <div><dt>All reviews</dt><dd>{formatNumber(projected.reviews)}</dd></div>
          <div><dt>Review time</dt><dd>{formatNumber(projected.reviewMinutes)} min</dd></div>
          <div><dt>Beyond review capacity</dt><dd>{formatNumber(projected.capacityExcess)} min</dd></div>
          <div><dt>Review cost</dt><dd>EUR {formatNumber(projected.reviewCost)}</dd></div>
          <div><dt>Illustrative total cost</dt><dd>EUR {formatNumber(projected.totalCost)}</dd></div>
        </dl> : <p role="status">Projections and export are paused. {Object.keys(errors).length ? 'Correct the marked inputs. Invalid assumptions are not saved; other progress is saved when storage is available.' : 'These values exceed the supported calculation range, or an evaluated class is absent. Try smaller values or inspect the evidence.'}</p>}
        {projected && projected.capacityExcess > 0 && <p className="capacity-warning">Review demand exceeds the entered capacity. This is a warning, not a queue simulation or an estimate of extra missed defects.</p>}
      </div></div>
      <p className="small">Uses complete-set routing rates, including technical failures. Assumes every flag is reviewed, people resolve flags correctly, and each missed defect incurs the average cost entered. Display values are rounded; calculations retain precision.</p>
    </section>
    <section className="decision"><h2>What would you do next?</h2>
      <fieldset><legend>Your pilot decision</legend>{pilotDecisions.map(decision => <label className="radio-option" key={decision}>
        <input type="radio" name="pilot-decision" value={decision} checked={state.decision === decision} onChange={() => update({ decision: decision as PilotDecision })} />{decision}
      </label>)}</fieldset>
      <label htmlFor="rationale">Your reasoning (optional, up to 2,000 characters)<textarea id="rationale" maxLength={2000} rows={3} value={state.rationale} onChange={e => update({ rationale: e.target.value })} /></label>
      <p className="small">This is your conclusion, not an automatically validated recommendation. Your answers and reasoning stay in this browser.</p>
      <button className="primary" onClick={exportBrief} disabled={!projected || !state.decision}>Download pilot brief (.md)</button>
      {exportError && <p role="alert">{exportError}</p>}
      <details><summary>What a real pilot still needs</summary><ul>{prerequisites.map(p => <li key={p}>{p}</li>)}</ul></details>
    </section>
    </details>
    <details className="provenance"><summary>Where the results come from</summary>
      <p>{bundle.dataset.attribution} <a href={bundle.dataset.licence_url}>{bundle.dataset.licence}</a>. <a href={bundle.dataset.source_url}>Dataset source</a>.</p>
      <p>Dataset: {bundle.dataset.dataset_id} / {bundle.dataset.category}. {bundle.dataset.modification_notice}</p>
      <p>Run: <code>{evidence.run.run_id}</code>; provider: {evidence.run.provider}; model: {evidence.run.model_id}; created {evidence.run.created_at}.</p>
      <p>Reported versions: {[...new Set(evidence.predictions.flatMap(p => p.attempts.map(a => a.reported_model_version).filter(Boolean)))].join(', ')}. Provider aliases can change.</p>
      <p>Manifest SHA-256: <code>{bundle.manifest_sha256}</code><br />Evaluation membership SHA-256: <code>{report.membership_sha256}</code></p>
      <p>Challenge: {bundle.challenge.version}. {bundle.challenge.rationale}</p>
      <ul>{[...new Set([...bundle.limitations, ...report.limitations])].map(text => <li key={text}>{text}</li>)}</ul>
      <a href="/evidence/bundle.json" download>Download the complete saved evidence (JSON)</a>
      {bundle.configuration_assets.map(c => <p key={c.run_id}><a href={`/evidence/${c.path}`} download>Download frozen instructions, normal reference and image settings ({c.run_id})</a></p>)}
      <p>{bundle.notices.map(n => <a key={n.path} href={`/evidence/${n.path}`} download>{n.path.endsWith('license.txt') ? 'Original dataset licence' : 'Original dataset readme'}{' '}</a>)}</p>
    </details>
  </>;
}
