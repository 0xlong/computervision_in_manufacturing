import { useCallback, useEffect, useReducer, useRef, useState } from 'react';
import type { Bundle, PlaybackCatalog } from './types';
import { loadPlaybackCatalog } from './bundle';
import { Picture } from './Picture';
import { AnswerCard, Assessment, AssessmentDetails, answerLabel } from './Assessment';
import { initialPlayback, playbackCounts, playbackReducer } from './playback';
import { differentAnswerIndices, modelName, savedDecision } from './comparison';
import { ComparisonDashboard } from './ComparisonDashboard';

export function Watch({ bundle, active }: { bundle: Bundle; active: boolean }) {
  const [catalog, setCatalog] = useState<PlaybackCatalog | null>(null);
  const [error, setError] = useState(false), [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); setError(false);
    loadPlaybackCatalog(bundle, controller.signal).then(value => { if (!controller.signal.aborted) setCatalog(value); })
      .catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, [bundle, retry]);
  if (catalog) return <Player bundle={bundle} catalog={catalog} active={active} />;
  return <section hidden={!active} className="watch" aria-label="Watch AI Inspect">
    <h1>Watch AI Inspect</h1>{error ? <div role="alert"><p>Playback pictures could not be loaded.</p><button onClick={() => setRetry(n => n + 1)}>Retry playback</button></div> : <p role="status">Loading pictures…</p>}
  </section>;
}

function Player({ bundle, catalog, active }: { bundle: Bundle; catalog: PlaybackCatalog; active: boolean }) {
  const [state, dispatch] = useReducer(playbackReducer, initialPlayback);
  const [ready, setReady] = useState(false), [failed, setFailed] = useState(false), [seconds, setSeconds] = useState(4);
  const onReady = useCallback((value: boolean) => setReady(value), []);
  const onFailure = useCallback((value: boolean) => { setFailed(value); if (value) dispatch({ type: 'pause' }); }, []);
  const clock = useRef({ key: '', remaining: 1 });
  const playbackArea = useRef<HTMLElement>(null);
  const allIds = catalog.images.map(i => i.image_id);
  const different = differentAnswerIndices(bundle, allIds);
  const indices = state.filter === 'different' ? different : catalog.images.map((_, index) => index);
  const image = catalog.images[indices[state.index]];
  const referenceStage = bundle.runs.length + 1;
  const referenceShown = state.stage === referenceStage;
  const stageLabel = state.stage === 0 ? 'Picture' : referenceShown ? 'Dataset reference' : modelName(bundle.runs[state.stage - 1].report.model_id);
  const counts = bundle.runs.map(run => playbackCounts(bundle, state.seen, run.report.run_id, allIds));
  useEffect(() => { if (!active) dispatch({ type: 'pause' }); }, [active]);
  useEffect(() => {
    const pause = () => { if (document.hidden) dispatch({ type: 'pause' }); };
    document.addEventListener('visibilitychange', pause);
    return () => document.removeEventListener('visibilitychange', pause);
  }, []);
  useEffect(() => {
    const key = `${state.index}-${state.stage}-${state.epoch}`;
    if (clock.current.key !== key) clock.current = { key, remaining: 1 };
    if (!state.playing || !active || !ready || !indices.length || document.hidden) return;
    const duration = seconds * 1000 / (referenceStage + 1);
    const started = performance.now();
    const timer = window.setTimeout(() => {
      if (document.hidden) { dispatch({ type: 'pause' }); return; }
      if (referenceShown && state.index < indices.length - 1) setReady(false);
      dispatch({ type: 'advance', total: indices.length, referenceStage, referenceIndex: indices[state.index] });
    }, duration * clock.current.remaining);
    return () => {
      window.clearTimeout(timer);
      clock.current.remaining = Math.max(0, clock.current.remaining - (performance.now() - started) / duration);
    };
  }, [state.index, state.stage, state.epoch, state.playing, state.filter, active, ready, indices.length, seconds, referenceStage, referenceShown]);
  const navigate = (index: number) => { setReady(false); dispatch({ type: 'navigate', index }); };
  const restart = () => { setReady(false); dispatch({ type: 'restart' }); };
  const changeFilter = (filter: 'all' | 'different') => { setReady(false); setFailed(false); dispatch({ type: 'filter', filter }); };
  const returnToPlayback = (action: () => void) => { action(); playbackArea.current?.focus({ preventScroll: true }); };
  return <section ref={playbackArea} hidden={!active} className="watch" aria-labelledby="watch-title" aria-describedby="playback-keys" tabIndex={0} onKeyDown={e => {
    if (e.key === 'Escape') { dispatch({ type: 'pause' }); return; }
    if ((e.target as HTMLElement).closest('button, select, input, textarea, a, summary, .image-window') || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key === ' ' && !state.finished && !failed && indices.length) { e.preventDefault(); dispatch({ type: state.playing ? 'pause' : 'play' }); }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      e.preventDefault(); const index = state.index + (e.key === 'ArrowLeft' ? -1 : 1);
      if (index >= 0 && index < indices.length) navigate(index); else dispatch({ type: 'pause' });
    }
    if (e.key === 'Home') { e.preventDefault(); restart(); }
    if (e.key === 'End' && indices.length) { e.preventDefault(); navigate(indices.length - 1); }
  }}>
    <div className="section-heading watch-heading"><h1 id="watch-title">Watch AI Inspect</h1><p>{allIds.length} pictures · {bundle.runs.length} models · Saved results</p></div>
    <div className="watch-controls">
      <div className="playback-controls" role="group" aria-label="Playback controls">
        <button className="primary" disabled={state.finished || failed || !indices.length} onClick={() => dispatch({ type: state.playing ? 'pause' : 'play' })}>{state.playing ? 'Pause' : 'Play'}</button>
        <button disabled={state.index === 0} onClick={() => navigate(state.index - 1)}>Previous</button>
        <button disabled={state.index >= indices.length - 1} onClick={() => navigate(state.index + 1)}>Next</button>
        <button onClick={restart}>Restart</button>
        <div className="viewing-time"><label htmlFor="viewing-time">Viewing time</label><select id="viewing-time" value={seconds} onChange={e => setSeconds(Number(e.target.value))}>
          <option value={2}>Fast · 2 s</option><option value={4}>Normal · 4 s</option><option value={8}>Slow · 8 s</option>
        </select></div>
      </div>
      <div className="playback-filter" role="group" aria-label="Picture filter">
        {state.filter === 'all' ? <button disabled={bundle.runs.length < 2} onClick={() => changeFilter('different')}>Different answers only ({different.length})</button> : <button onClick={() => changeFilter('all')}>Show all pictures</button>}
      </div>
    </div>
    <p className="playback-status" role="status">{indices.length ? `Picture ${state.index + 1} of ${indices.length}` : 'No matching pictures'} · {state.finished ? 'Finished' : state.playing ? 'Playing' : 'Paused'}{indices.length > 0 && !state.finished && ` · ${!ready && !failed ? 'Loading picture' : stageLabel}`}{state.filter === 'different' && ' · Different answers'}</p>
    {state.finished ? <ComparisonDashboard bundle={bundle} watched={counts[0].revealed} matching={different.length} filtered={state.filter === 'different'} active={active}
      onReview={() => returnToPlayback(() => changeFilter('all'))} onDifferent={() => returnToPlayback(() => changeFilter('different'))} onAgain={() => returnToPlayback(restart)} /> : <>
      {!image && <p className="notice">No different answers. Choose “Show all pictures” to continue.</p>}
      {image && <div className="playback-evidence">
        <Picture key={`${image.image_id}-${state.epoch}`} image={image} revealed={referenceShown} onReady={onReady} onFailure={onFailure} />
        <div className="answer-comparison playback-comparison" role="group" aria-label="Saved answer comparison">
          {bundle.runs.map((saved, index) => {
            const title = modelName(saved.report.model_id), decision = savedDecision(saved, image.image_id);
            return <div key={saved.report.run_id} className={state.stage <= index ? 'pending-assessment' : ''} aria-hidden={state.stage <= index}>
              {referenceShown ? <Assessment saved={saved} imageId={image.image_id} reference={image.label} title={title} /> : <AnswerCard title={title} value={decision === 'unavailable' ? 'No answer' : decision === 'uncertain' ? 'Unsure' : answerLabel(decision)} detail="Saved assessment" tone="neutral" />}
              {state.stage > index && <AssessmentDetails key={image.image_id} saved={saved} imageId={image.image_id} fixture={bundle.execution === 'fixture'} />}
            </div>;
          })}
          <div className={referenceShown ? '' : 'pending-assessment'} aria-hidden={!referenceShown}><AnswerCard title="Dataset reference" value={image.label === 'normal' ? 'Looks fine' : 'Needs checking'} detail={image.label === 'normal' ? 'No defect labelled' : 'Defect labelled'} tone="reference" /></div>
        </div>
      </div>}
      <section className="playback-results" aria-labelledby="playback-results-title">
        <h2 id="playback-results-title">This playback <span className="small">{counts[0].revealed} / {indices.length} references viewed</span></h2>
        <div className="running-models">{bundle.runs.map((saved, index) => <section className="running-model" key={saved.report.run_id} aria-label={`${saved.report.model_id} playback totals`}>
          <h3>{modelName(saved.report.model_id)} <span className="running-correct">{counts[index].correct} correct</span></h3>
          <dl className="running-counts">
            <div><dt>Defects flagged</dt><dd>{counts[index].flagged}</dd></div><div><dt>Defects missed</dt><dd>{counts[index].missed}</dd></div><div><dt>Good parts flagged</dt><dd>{counts[index].falseAlarms}</dd></div>
          </dl><p className="small">{counts[index].unsure} unsure · {counts[index].unavailable} unavailable</p>
        </section>)}</div>
      </section>
    </>}
    <details className="playback-help"><summary>About this playback</summary>
      <p>Picture → each model → dataset reference. Totals update once when the reference appears. Unsure and unavailable answers stay separate. Viewing time is per picture, not AI request time.</p>
      <p>Changing the filter pauses playback and clears its counters. Full benchmark scores never change.</p>
      <p id="playback-keys">Focus the playback area: Space to play or pause, arrows for pictures, Home to restart, End for the last picture, Esc to pause. Buttons work with Tab and Enter.</p>
    </details>
  </section>;
}
