import type { Bundle, SavedRun } from './types';

export function requestTimes(saved: SavedRun) {
  const attempts = saved.evidence.predictions.flatMap(p => p.attempts);
  const times = attempts.flatMap(a => a.latency_ms === null ? [] : [a.latency_ms]).sort((a, b) => a - b);
  const middle = Math.floor(times.length / 2);
  return {
    median: times.length ? times.length % 2 ? times[middle] : (times[middle - 1] + times[middle]) / 2 : null,
    measured: times.length,
    total: attempts.length,
  };
}

export function ModelComparison({ bundle, selectedRun, onSelect }: { bundle: Bundle; selectedRun: string; onSelect: (id: string) => void }) {
  return <section className="model-comparison" aria-labelledby="model-comparison-title">
    <h2 id="model-comparison-title">Compare models</h2>
    {bundle.runs.length === 1 && <p className="notice">One completed model so far. A comparison needs another model evaluated on the same pictures.</p>}
    <p className="small">Select a model to explore its results. Scroll sideways if some columns are out of view.</p>
    <div className="comparison-table-window" role="region" aria-label="Model comparison table; scroll sideways for more columns" tabIndex={0}>
      <table>
        <caption>Complete {bundle.runs[0].report.expected}-picture test set · Saved AI results</caption>
        <thead><tr><th scope="col">Model</th><th scope="col">Defects missed</th><th scope="col">Good parts flagged</th><th scope="col">AI answers</th><th scope="col">No answer</th><th scope="col">Unsure</th><th scope="col">Request time</th><th scope="col">Sent for checking</th></tr></thead>
        <tbody>{bundle.runs.map(saved => {
          const { report, evidence } = saved, m = report.successful_output, timing = requestTimes(saved);
          const unsure = evidence.predictions.filter(p => p.status === 'success' && p.attempts.at(-1)!.response?.decision === 'uncertain').length;
          return <tr key={report.run_id}>
            <th scope="row"><button aria-pressed={selectedRun === report.run_id} onClick={() => onSelect(report.run_id)}>{report.model_id}</button><span className="small">{selectedRun === report.run_id ? 'Selected' : 'View these results'}</span></th>
            <td>{m.fn} / {m.anomalous}</td><td>{m.fp} / {m.normal}</td><td>{report.succeeded} / {report.expected}</td><td>{report.failed} / {report.expected}</td><td>{unsure} / {report.succeeded}</td>
            <td>{timing.median === null ? 'Unavailable' : `${(timing.median / 1000).toFixed(2)} s`}<span className="small">{timing.measured} / {timing.total} attempts timed</span></td>
            <td>{report.full_set_routing.review_count} / {report.expected}</td>
          </tr>;
        })}</tbody>
      </table>
    </div>
    <details className="comparison-guide"><summary>How to read the table</summary>
      <p>Fewer missed defects and fewer good parts flagged are better. Check AI answers and No answer alongside these counts: a model that fails to answer has not successfully inspected those pictures.</p>
      <p>Defect and good-part counts cover pictures with an AI answer; each cell shows its class total. Unsure is a valid answer sent for checking, included in flags and also listed separately. No answer is a technical failure, not a correct prediction. Sent for checking includes unsure answers and technical failures.</p>
      <p>Request time is the median of all available recorded attempt times, including retries and failed requests. Pauses between requests are excluded; missing times stay missing. This is separate from the playback's viewing time.</p>
      <p>Models use the same test pictures and reference labels. Each run's frozen settings and detailed results remain available below. A result here shows performance on this public dataset, not which model is best in every factory.</p>
    </details>
  </section>;
}
