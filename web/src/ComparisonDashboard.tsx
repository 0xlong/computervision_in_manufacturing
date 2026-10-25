import { useEffect, useRef } from 'react';
import type { Bundle } from './types';
import { benchmarkCounts, modelName, percentage } from './comparison';
import { requestTimes } from './ModelComparison';

function ComparisonBar({ label, count, total, caution = false }: { label: string; count: number; total: number; caution?: boolean }) {
  return <div className={`benchmark-bar${caution ? ' caution' : ''}`}>
    <div><span>{label}</span><strong>{count} / {total} <span className="small">({percentage(count, total)})</span></strong></div>
    <div className="bar-track" aria-hidden="true"><div style={{ width: `${total ? 100 * count / total : 0}%` }} /></div>
  </div>;
}

export function ComparisonDashboard({ bundle, watched, matching, filtered, active, onReview, onDifferent, onAgain }: {
  bundle: Bundle; watched: number; matching: number; filtered: boolean; active: boolean;
  onReview: () => void; onDifferent: () => void; onAgain: () => void;
}) {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { if (active) heading.current?.focus({ preventScroll: true }); }, [active]);
  const summaries = bundle.runs.map(saved => ({ saved, counts: benchmarkCounts(saved), timing: requestTimes(saved) }));
  const first = summaries[0], second = summaries[1];
  return <section className="comparison-dashboard" aria-labelledby="dashboard-title">
    <h2 id="dashboard-title" tabIndex={-1} ref={heading}>The complete comparison</h2>
    <p className="notice">{watched} of {filtered ? matching : first.saved.report.expected} pictures viewed{filtered ? ' · Filtered playback' : ''}. Scores below cover all {first.saved.report.expected} pictures.</p>
    {bundle.execution === 'fixture' && <p className="notice">Test examples only: these invented results are for checking the website.</p>}
    <div className="benchmark-cards">
      {summaries.map(({ saved, counts, timing }) => <article className="benchmark-card" key={saved.report.run_id} aria-label={`${saved.report.model_id} full benchmark`}>
        <h3>{modelName(saved.report.model_id)}</h3>
        <p className="benchmark-score"><strong>{percentage(counts.correct, saved.report.expected)}</strong><span>✓ Correct decisions</span></p>
        <ComparisonBar label="Matching the reference" count={counts.correct} total={saved.report.expected} />
        <ComparisonBar label="! Defects missed" count={counts.missed} total={counts.defective} caution />
        <ComparisonBar label="! Good parts flagged" count={counts.falseAlarms} total={counts.good} caution />
        <dl>
          <div><dt>? Unsure answers</dt><dd>{counts.unsure} / {saved.report.expected}</dd></div>
          <div><dt>— Unavailable answers</dt><dd>{counts.unavailable} / {saved.report.expected}</dd></div>
          <div><dt>Median recorded request time</dt><dd>{timing.median === null ? 'Unavailable' : `${(timing.median / 1000).toFixed(2)} s`}</dd></div>
        </dl>
        <p className="small">{timing.measured} / {timing.total} requests timed · Separate from viewing time</p>
      </article>)}
    </div>
    {second ? <p className="benchmark-explanation">{modelName(first.saved.report.model_id)} missed {first.counts.missed} defects; {modelName(second.saved.report.model_id)} missed {second.counts.missed}. {first.counts.falseAlarms === second.counts.falseAlarms ? `Both flagged ${first.counts.falseAlarms} good parts.` : `They flagged ${first.counts.falseAlarms} and ${second.counts.falseAlarms} good parts, respectively.`} This public dataset does not establish which model is best everywhere.</p> : <p>A comparison needs another completed model on the same pictures.</p>}
    <div className="dashboard-actions" role="group" aria-label="Review and replay">
      <button onClick={onReview}>Review pictures</button>
      <button disabled={bundle.runs.length < 2 || matching === 0} onClick={onDifferent}>Review different answers</button>
      <button className="primary" onClick={onAgain}>Watch again</button>
    </div>
    <details><summary>How scores are counted</summary>
      <p>Correct decisions are “Looks fine” or “Needs checking” answers matching the dataset reference. Unsure and unavailable answers are never correct. All {first.saved.report.expected} pictures stay in the denominator.</p>
      <p>Misses and good parts flagged count categorical errors against all defective and good pictures. Sending an unsure answer for checking is not a correct defect prediction. Filtering never changes benchmark scores.</p>
      <p>Median request time includes recorded attempts, retries and failures, excluding pauses between requests. It is separate from playback viewing time.</p>
      <p>Watch again keeps the filter, starts paused and clears playback counters. Your own judgments stay saved.</p>
    </details>
  </section>;
}
