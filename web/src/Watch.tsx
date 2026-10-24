import { useCallback, useEffect, useReducer, useRef, useState } from 'react';
import type { Bundle } from './types';
import { Picture } from './Picture';
import { AnswerCard, Assessment, AssessmentDetails, answerLabel } from './Assessment';
import { initialPlayback, playbackReducer } from './playback';

export function Watch({ bundle, active }: { bundle: Bundle; active: boolean }) {
  const [state, dispatch] = useReducer(playbackReducer, initialPlayback);
  const [ready, setReady] = useState(false);
  const onReady = useCallback((value: boolean) => setReady(value), []);
  const clock = useRef({ key: '', remaining: 1 });
  const ids = bundle.challenge.image_ids;
  const image = bundle.images.find(i => i.image_id === ids[state.index])!;
  const saved = bundle.runs[0];
  const prediction = saved.evidence.predictions.find(p => p.image_id === image.image_id)!;
  const response = prediction.status === 'success' ? prediction.attempts.at(-1)!.response : null;
  const complete = state.finished;
  useEffect(() => { if (!active) dispatch({ type: 'pause' }); }, [active]);
  useEffect(() => {
    const pause = () => { if (document.hidden) dispatch({ type: 'pause' }); };
    document.addEventListener('visibilitychange', pause);
    return () => document.removeEventListener('visibilitychange', pause);
  }, []);
  useEffect(() => {
    const key = `${state.index}-${state.stage}-${state.epoch}`;
    if (clock.current.key !== key) clock.current = { key, remaining: 1 };
    if (!state.playing || !active || !ready || document.hidden) return;
    const duration = 1000;
    const started = performance.now();
    const timer = window.setTimeout(() => {
      if (state.stage === 2 && state.index < ids.length - 1) setReady(false);
      dispatch({ type: 'advance', total: ids.length });
    }, duration * clock.current.remaining);
    return () => {
      window.clearTimeout(timer);
      clock.current.remaining = Math.max(0, clock.current.remaining - (performance.now() - started) / duration);
    };
  }, [state.index, state.stage, state.epoch, state.playing, active, ready, ids.length]);
  return <section hidden={!active} className="watch" aria-labelledby="watch-title">
    <div className="section-heading"><h1 id="watch-title">Watch AI Inspect</h1><p>Saved AI results · Five pictures</p></div>
    <p className="small">3 seconds per picture is viewing time, not AI processing speed. No new AI requests.</p>
    <div className="playback-controls"><button className="primary" disabled={complete} onClick={() => dispatch({ type: state.playing ? 'pause' : 'play' })}>{state.playing ? 'Pause' : 'Play'}</button></div>
    <p role="status">Picture {state.index + 1} of {ids.length} · {complete ? 'Finished' : state.playing ? 'Playing' : 'Paused'} · {['Look at the picture', 'AI assessment', 'Dataset reference'][state.stage]}</p>
    <Picture key={`${image.image_id}-${state.epoch}`} image={image} revealed={state.stage === 2} onReady={onReady} />
    <div className="answer-comparison playback-comparison" role="group" aria-label="Saved answer comparison">
      {state.stage === 0 ? <AnswerCard title="AI assessment" value="Waiting" detail="Picture first" tone="neutral" /> : state.stage === 1 ? <AnswerCard title="AI assessment" value={response ? response.decision === 'uncertain' ? 'Unsure' : answerLabel(response.decision) : 'No answer'} detail="Reference next" tone="neutral" /> : <Assessment saved={saved} imageId={image.image_id} reference={image.label} />}
      {state.stage < 2 ? <AnswerCard title="Dataset reference" value="Waiting" detail="Shown after AI" tone="neutral" /> : <AnswerCard title="Dataset reference" value={image.label === 'normal' ? 'Looks fine' : 'Needs checking'} detail={image.label === 'normal' ? 'No defect labelled' : 'Defect labelled'} tone="reference" />}
    </div>
    {state.stage > 0 && <AssessmentDetails key={image.image_id} saved={saved} imageId={image.image_id} fixture={bundle.execution === 'fixture'} />}
  </section>;
}
