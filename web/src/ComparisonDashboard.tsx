import { useEffect, useRef } from 'react';
import type { Bundle } from './types';
import { benchmarkCounts, percentage } from './comparison';
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
    <p className="eyebrow">Playback finished · Saved evidence</p>
    <h2 id="dashboard-title" tabIndex={-1} ref={heading}>The complete comparison</h2>
    <p className="notice">You viewed {watched} of {filtered ? matching : bundle.challenge.image_ids.length} {filtered ? 'matching pictures in filtered playback' : 'selected playback pictures'}. The benchmark below covers all {first.saved.report.expected} pictures. Filtering never changes these scores.</p>
    <p>Correct decisions are “Looks fine” or “Needs checking” answers matching the dataset reference. Unsure and unavailable answers do not count as correct. Every benchmark picture stays in the denominator.</p>
    {bundle.execution === 'fixture' && <p className="notice">Test examples only: these invented results are for checking the website.</p>}
    <div className="benchmark-cards">
      {summaries.map(({ saved, counts, timing }) => <article className="benchmark-card" key={saved.report.run_id} aria-label={`${saved.report.model_id} full benchmark`}>
        <h3>{saved.report.model_id}</h3>
        <p className="benchmark-score"><strong>{percentage(counts.correct, saved.report.expected)}</strong><span>✓ Correct decisions</span></p>
        <ComparisonBar label="Matching the reference" count={counts.correct} total={saved.report.expected} />
        <ComparisonBar label="! Defects missed" count={counts.missed} total={counts.defective} caution />
        <ComparisonBar label="! Good parts flagged" count={counts.falseAlarms} total={counts.good} caution />
        <dl>
          <div><dt>? Unsure answers</dt><dd>{counts.unsure} / {saved.report.expected}</dd></div>
          <div><dt>— Unavailable answers</dt><dd>{counts.unavailable} / {saved.report.expected}</dd></div>
          <div><dt>Median recorded request time</dt><dd>{timing.median === null ? 'Unavailable' : `${(timing.median / 1000).toFixed(2)} s`}</dd></div>
        </dl>
        <p className="small">{timing.measured} / {timing.total} attempts timed, including retries and failures. Request time is separate from playback viewing time; pauses between requests are excluded.</p>
      </article>)}
    </div>
    {second ? <p className="benchmark-explanation">On these pictures, {first.saved.report.model_id} missed {first.counts.missed} defects and flagged {first.counts.falseAlarms} good parts; {second.saved.report.model_id} missed {second.counts.missed} and flagged {second.counts.falseAlarms}. {summaries.map(({ saved, counts }) => `${saved.report.model_id} gave ${counts.unsure} unsure and ${counts.unavailable} unavailable answers`).join('; ')}. These results describe this public dataset and these saved model settings. They do not establish which model is best everywhere.</p> : <p>A comparison needs another completed model on the same pictures.</p>}
    <p className="small">Misses and good parts flagged count categorical errors only, against all defective and good pictures respectively. Sending an unsure answer for human checking is a review action, not a correct defect prediction.</p>
    <div className="dashboard-actions" role="group" aria-label="Review and replay">
      <button onClick={onReview}>Review pictures</button>
      <button disabled={bundle.runs.length < 2 || matching === 0} onClick={onDifferent}>Review different answers</button>
      <button className="primary" onClick={onAgain}>Watch again</button>
    </div>
    <p className="small">Watch again starts the current selection paused and clears playback counters. Your own inspection judgments stay saved.</p>
  </section>;
}
