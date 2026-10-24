import { useCallback, useEffect, useReducer, useRef, useState } from 'react';
import type { Bundle } from './types';
import { Picture } from './Picture';
import { AnswerCard, Assessment, AssessmentDetails, answerLabel } from './Assessment';
import { initialPlayback, playbackCounts, playbackReducer } from './playback';

export function Watch({ bundle, active }: { bundle: Bundle; active: boolean }) {
  const [state, dispatch] = useReducer(playbackReducer, initialPlayback);
  const [ready, setReady] = useState(false), [failed, setFailed] = useState(false), [seconds, setSeconds] = useState(3);
  const onReady = useCallback((value: boolean) => setReady(value), []);
  const onFailure = useCallback((value: boolean) => { setFailed(value); if (value) dispatch({ type: 'pause' }); }, []);
  // Retain the unfinished fraction of a stage across pauses and speed changes.
  const clock = useRef({ key: '', remaining: 1 });
  const ids = bundle.challenge.image_ids;
  const image = bundle.images.find(i => i.image_id === ids[state.index])!;
  const saved = bundle.runs[0];
  const prediction = saved.evidence.predictions.find(p => p.image_id === image.image_id)!;
  const response = prediction.status === 'success' ? prediction.attempts.at(-1)!.response : null;
  const complete = state.finished;
  const counts = playbackCounts(bundle, state.seen);
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
    const duration = seconds * 1000 / 3;
    const started = performance.now();
    const timer = window.setTimeout(() => {
      if (document.hidden) { dispatch({ type: 'pause' }); return; }
      if (state.stage === 2 && state.index < ids.length - 1) setReady(false);
      dispatch({ type: 'advance', total: ids.length });
    }, duration * clock.current.remaining);
    return () => {
      window.clearTimeout(timer);
      clock.current.remaining = Math.max(0, clock.current.remaining - (performance.now() - started) / duration);
    };
  }, [state.index, state.stage, state.epoch, state.playing, active, ready, ids.length, seconds]);
  const navigate = (index: number) => { setReady(false); dispatch({ type: 'navigate', index }); };
  const restart = () => { setReady(false); dispatch({ type: 'restart' }); };
  return <section hidden={!active} className="watch" aria-labelledby="watch-title" aria-describedby="playback-keys" tabIndex={0} onKeyDown={e => {
    if (e.key === 'Escape') { dispatch({ type: 'pause' }); return; }
    if ((e.target as HTMLElement).closest('button, select, input, textarea, a, summary, .image-window') || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key === ' ' && !complete && !failed) { e.preventDefault(); dispatch({ type: state.playing ? 'pause' : 'play' }); }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      e.preventDefault();
      const index = state.index + (e.key === 'ArrowLeft' ? -1 : 1);
      if (index >= 0 && index < ids.length) navigate(index);
      else dispatch({ type: 'pause' });
    }
    if (e.key === 'Home') { e.preventDefault(); restart(); }
  }}>
    <div className="section-heading"><h1 id="watch-title">Watch AI Inspect</h1><p>Saved AI results · Five pictures</p></div>
    <p className="small">Viewing time, not AI processing speed. No new AI requests.</p>
    <div className="playback-controls" role="group" aria-label="Playback controls">
      <button className="primary" disabled={complete || failed} onClick={() => dispatch({ type: state.playing ? 'pause' : 'play' })}>{state.playing ? 'Pause' : 'Play'}</button>
      <button disabled={state.index === 0} onClick={() => navigate(state.index - 1)}>Previous</button>
      <button disabled={state.index === ids.length - 1} onClick={() => navigate(state.index + 1)}>Next</button>
      <button onClick={restart}>Restart</button>
      <div><label htmlFor="viewing-time">Viewing time per picture</label><select id="viewing-time" value={seconds} onChange={e => setSeconds(Number(e.target.value))}>
        <option value={1.5}>Fast · 1.5 s</option><option value={3}>Normal · 3 s</option><option value={6}>Slow · 6 s</option>
      </select></div>
    </div>
    <p role="status">Picture {state.index + 1} of {ids.length} · {complete ? 'Finished' : state.playing ? 'Playing' : 'Paused'} · {!ready && !failed ? 'Waiting for picture' : ['Look at the picture', 'AI assessment', 'Dataset reference'][state.stage]}</p>
    <div className="playback-evidence">
    <Picture key={`${image.image_id}-${state.epoch}`} image={image} revealed={state.stage === 2} onReady={onReady} onFailure={onFailure} />
    <div className="answer-comparison playback-comparison" role="group" aria-label="Saved answer comparison">
      {state.stage === 0 ? <AnswerCard title="AI assessment" value="Waiting" detail="Picture first" tone="neutral" /> : state.stage === 1 ? <AnswerCard title="AI assessment" value={response ? response.decision === 'uncertain' ? 'Unsure' : answerLabel(response.decision) : 'No answer'} detail="Reference next" tone="neutral" /> : <Assessment saved={saved} imageId={image.image_id} reference={image.label} />}
      {state.stage < 2 ? <AnswerCard title="Dataset reference" value="Waiting" detail="Shown after AI" tone="neutral" /> : <AnswerCard title="Dataset reference" value={image.label === 'normal' ? 'Looks fine' : 'Needs checking'} detail={image.label === 'normal' ? 'No defect labelled' : 'Defect labelled'} tone="reference" />}
    </div>
    </div>
    {state.stage > 0 && <AssessmentDetails key={image.image_id} saved={saved} imageId={image.image_id} fixture={bundle.execution === 'fixture'} />}
    <section className="playback-results" aria-labelledby="playback-results-title">
      <h2 id="playback-results-title">Results for this five-picture playback</h2>
      <div className="result-highlights">
        <section aria-label="Defects flagged"><strong>{counts.flagged}</strong><h3>Defects flagged</h3></section>
        <section aria-label="Defects missed"><strong>{counts.missed}</strong><h3>Defects missed</h3></section>
        <section aria-label="Good parts flagged"><strong>{counts.falseAlarms}</strong><h3>Good parts flagged</h3></section>
      </div>
      <p className="small">{counts.revealed} of {ids.length} references shown · {counts.unsure} unsure · {counts.unavailable} unavailable</p>
      <p className="small">Unsure and unavailable answers are separate from the three counts and need human checking. Five selected pictures are separate from the complete {saved.report.expected}-image benchmark in Results.</p>
    </section>
    <details><summary>Keyboard controls</summary><p id="playback-keys">Focus this playback area: Space to play or pause, arrow keys for pictures, Home to restart, Esc to pause. Buttons also work with Tab and Enter.</p></details>
  </section>;
}
