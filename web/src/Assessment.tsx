import type { SavedRun } from './types';

export const answerLabel = (answer: string) => answer === 'looks_acceptable' ? 'Looks fine' : answer === 'needs_review' ? 'Needs checking' : 'Unsure — needs checking';

export function AnswerCard({ title, value, detail, tone }: { title: string; value: string; detail: string; tone: 'match' | 'mismatch' | 'neutral' | 'reference' }) {
  return <section className={`comparison-card ${tone}`} aria-label={title}><h2>{title}</h2><strong className="comparison-value">{value}</strong>
    <p className="comparison-status"><span aria-hidden="true">{tone === 'match' ? '✓' : tone === 'mismatch' ? '!' : tone === 'reference' ? '◆' : '?'}</span>{detail}</p></section>;
}

export function Assessment({ saved, imageId, reference, title = 'AI assessment' }: { saved: SavedRun; imageId: string; reference: 'normal' | 'anomalous'; title?: string }) {
  const prediction = saved.evidence.predictions.find(p => p.image_id === imageId)!;
  const attempt = prediction.attempts.at(-1)!;
  const response = prediction.status === 'success' ? attempt.response : null;
  const matches = response && ((response.decision === 'needs_review') === (reference === 'anomalous'));
  const tone = !response || response.decision === 'uncertain' ? 'neutral' : matches ? 'match' : 'mismatch';
  const detail = !response ? 'Human check needed' : response.decision === 'uncertain' ? 'Sent for checking' : matches ? 'Matches reference' : reference === 'anomalous' ? 'Missed defect' : 'False alarm';
  return <AnswerCard title={title} value={!response ? 'No answer' : response.decision === 'uncertain' ? 'Unsure' : answerLabel(response.decision)} detail={detail} tone={tone} />;
}

export function AssessmentDetails({ saved, imageId, fixture }: { saved: SavedRun; imageId: string; fixture: boolean }) {
  const prediction = saved.evidence.predictions.find(p => p.image_id === imageId)!;
  const attempt = prediction.attempts.at(-1)!;
  return <details className="assessment"><summary>{prediction.status === 'success' ? 'Why AI said this' : 'Why no AI answer?'}</summary>
    <p className="observation">{prediction.status === 'success' && attempt.response ? attempt.response.observation : `Recorded outcome: ${prediction.status}; reason: ${attempt.reason}.`}</p>
    <p className="small">{saved.evidence.run.model_id}. {fixture ? 'Invented test response.' : 'Authentic saved response.'} {attempt.latency_ms === null ? '' : `Recorded request time: ${(attempt.latency_ms / 1000).toFixed(2)} s.`}</p>
  </details>;
}
