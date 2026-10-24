import { useCallback, useEffect, useRef, useState } from 'react';
import { loadBundle } from './bundle';
import { answerImage, freshState, loadState, revealImage, storageKey } from './state';
import type { VisitorState } from './state';
import type { Answer, Bundle, SavedRun } from './types';
import { scenarioErrors } from './engine';
import { Picture } from './Picture';
import { Lab } from './Lab';

const answerLabel = (answer: string) => answer === 'looks_acceptable' ? 'Looks acceptable' : answer === 'needs_review' ? 'Needs further inspection' : 'Uncertain — route to review';

function Assessment({ saved, imageId, fixture }: { saved: SavedRun; imageId: string; fixture: boolean }) {
  const prediction = saved.evidence.predictions.find(p => p.image_id === imageId)!;
  const attempt = prediction.attempts.at(-1)!;
  return <section className="assessment"><p className="eyebrow">Saved model assessment</p><h3>{saved.evidence.run.model_id}</h3>
    {prediction.status === 'success' && attempt.response ? <><strong>{answerLabel(attempt.response.decision)}</strong><p>{attempt.response.observation}</p></> :
      <><strong>Assessment unavailable — human review required</strong><p>Recorded outcome: {prediction.status}; reason: {attempt.reason}.</p></>}
    <p className="small">{fixture ? 'Invented test response.' : 'Authentic saved response.'} No request was made by your visit. {attempt.latency_ms === null ? '' : `Recorded request time: ${(attempt.latency_ms / 1000).toFixed(2)} s.`}</p>
  </section>;
}

function Experience({ bundle }: { bundle: Bundle }) {
  const [loaded] = useState(() => {
    try { return loadState(window.localStorage, bundle); }
    catch { return { state: freshState(bundle), notice: 'Browser storage is unavailable. Progress stays in memory for this visit.', persistent: false }; }
  });
  const [state, setState] = useState(loaded.state), [notice, setNotice] = useState(loaded.notice);
  const [persistent, setPersistent] = useState(loaded.persistent), [confirmReset, setConfirmReset] = useState('');
  const [pictureReady, setPictureReady] = useState(false), [resetEpoch, setResetEpoch] = useState(0);
  const lastValidScenario = useRef({ ...loaded.state.scenario });
  const readyCallback = useCallback((ready: boolean) => setPictureReady(ready), []);
  const update = (patch: Partial<VisitorState>) => setState(s => ({ ...s, ...patch }));
  useEffect(() => {
    if (!persistent) return;
    if (!Object.keys(scenarioErrors(state.scenario)).length) lastValidScenario.current = { ...state.scenario };
    try { window.localStorage.setItem(storageKey, JSON.stringify({ ...state, scenario: lastValidScenario.current })); }
    catch { setPersistent(false); setNotice('Browser storage is unavailable. You can continue, but this visit’s changes will not be saved.'); }
  }, [state, persistent]);
  const index = bundle.challenge.image_ids.indexOf(state.selectedImage);
  const image = bundle.images.find(i => i.image_id === state.selectedImage)!;
  const answered = state.answers[image.image_id], revealed = state.revealed.includes(image.image_id);
  const selected = bundle.runs.find(r => r.evidence.run.run_id === state.selectedRun)!;
  const count = Object.keys(state.answers).length;
  const correct = bundle.images.filter(i => state.answers[i.image_id] && ((state.answers[i.image_id] === 'needs_review') === (i.label === 'anomalous'))).length;
  const goImage = (id: string) => { if (id === state.selectedImage) return; setPictureReady(false); update({ selectedImage: id }); };
  const goScreen = (screen: VisitorState['screen']) => { update({ screen }); document.getElementById('main')?.focus(); window.scrollTo(0, 0); };
  function reset() { setState(freshState(bundle)); setResetEpoch(n => n + 1); setConfirmReset(''); setNotice('Fastener progress has been reset.'); }
  return <>
    <a className="skip-link" href="#main">Skip to content</a>
    <header className="site-header"><a href="#main" className="brand" onClick={() => goScreen('start')}><span aria-hidden="true" className="brand-mark">◈</span><span>Inspection<span className="brand-light"> / Pilot Lab</span></span></a>
      {state.screen !== 'start' && <nav aria-label="Main navigation"><button aria-current={state.screen === 'inspect' ? 'page' : undefined} onClick={() => goScreen('inspect')}>Challenge</button><button aria-current={state.screen === 'lab' ? 'page' : undefined} onClick={() => goScreen('lab')}>Evidence &amp; pilot</button></nav>}</header>
    <main id="main" tabIndex={-1}>
      <div className="context-bar"><span><span className="live-dot" aria-hidden="true" />Public-data prototype · Fasteners</span>{state.screen !== 'start' && <span>Saved evidence · Local progress</span>}</div>
      {(state.screen !== 'start' || bundle.execution === 'fixture') && <p className="development-notice">{bundle.execution === 'fixture' ? 'TEST EXAMPLES ONLY — invented model answers; not real AI evidence.' : 'Local development preview · Authentic Gemini responses; dataset provenance limitations remain. Not cleared for publication.'}</p>}
      {notice && <p className="notice" role="status">{notice}</p>}
      {state.screen === 'start' && <section className="hero"><p className="eyebrow">Try AI quality inspection</p><h1>Can AI help spot<br /><em>faulty parts?</em></h1><p className="hero-copy">Check five pictures of metal nuts, then compare your answers with AI. See where it helps and where a person still needs to check.</p>
        <div className="hero-actions"><button className="primary" onClick={() => goScreen('inspect')}>Start the inspection ↗</button><button className="text-button" onClick={() => goScreen('lab')}>See the results →</button></div><p className="small">No setup needed. Your answers stay in this browser.</p>
        <p className="prototype-note">A learning demo using public images, not proof of factory performance.</p>
        <details className="about-demo"><summary>About this demo</summary>
          <p>Try five selected examples, compare your answers, then explore review workload and download a pilot brief.</p>
          <p>{bundle.execution === 'fixture' ? 'This test preview uses invented AI answers.' : `The AI answers are saved Gemini responses from all ${selected.report.expected} test images. Your visit makes no AI requests.`} The five challenge pictures are teaching examples, not a representative factory sample.</p>
          <p>Local development preview. Dataset source records have limitations; this preview is not cleared for publication. Public fastener images stand in for manufacturing tasks. No manufacturer affiliation or factory approval is implied.</p>
          <p>Dataset: {bundle.dataset.dataset_id} / {bundle.dataset.category}. The optional metal-surface track is not available in this preview.</p>
        </details></section>}
      {state.screen === 'inspect' && <>
        <section className="section-heading"><p className="eyebrow">01 / Make your own call</p><h1>Look first. Reveal second.</h1><p>Is the part visually acceptable, or would you ask a person to look more closely?</p></section>
        <div className="challenge-progress"><strong>Image {index + 1} of 5</strong><span>{count} of 5 answered</span><progress max={5} value={count} aria-label="Challenge answers completed" /></div>
        <div className="inspection-layout"><Picture key={`${image.image_id}-${resetEpoch}`} image={image} revealed={revealed} onReady={readyCallback} />
          <div className="judgment-panel"><p className="eyebrow">Your judgment</p><h2>What do you see?</h2><p>Use the zoom controls to inspect the surface and shape. There is no time limit.</p>
            <div className="answer-buttons">{(['looks_acceptable', 'needs_review'] as Answer[]).map(answer => <button key={answer} aria-pressed={answered === answer} disabled={revealed || !pictureReady} onClick={() => setState(s => answerImage(s, image.image_id, answer))}>{answerLabel(answer)}</button>)}</div>
            {answered && <p className="answer-status">Your answer: <strong>{answerLabel(answered)}</strong></p>}
            {!revealed && <button className="primary reveal-button" disabled={!answered || !pictureReady} onClick={() => setState(s => revealImage(s, image.image_id))}>Reveal evidence</button>}
            <p className="small">{revealed ? 'Your revealed answer is fixed until you reset this track.' : 'You can change your answer before reveal. AI answers and reference labels stay hidden until then.'}</p>
            {revealed && <div className="reveal" aria-live="polite"><section className="reference"><p className="eyebrow">Dataset reference</p><strong>{image.label === 'normal' ? 'Normal example' : 'Anomalous example'}</strong><p>{((answered === 'needs_review') === (image.label === 'anomalous')) ? 'Your answer matches the reference.' : 'Your answer differs from the reference.'} The public annotation is a learning reference, not a factory disposition.</p></section>
              <label>Saved model <select value={state.selectedRun} onChange={e => update({ selectedRun: e.target.value, comparisonRun: '' })}>{bundle.runs.map(r => <option key={r.evidence.run.run_id} value={r.evidence.run.run_id}>{r.evidence.run.model_id}</option>)}</select></label>
              <Assessment saved={selected} imageId={image.image_id} fixture={bundle.execution === 'fixture'} />
              {bundle.runs.length > 1 ? <><label>Compare with <select value={state.comparisonRun} onChange={e => update({ comparisonRun: e.target.value })}><option value="">No comparison</option>{bundle.runs.filter(r => r.evidence.run.run_id !== state.selectedRun).map(r => <option key={r.evidence.run.run_id} value={r.evidence.run.run_id}>{r.evidence.run.model_id}</option>)}</select></label>{state.comparisonRun && <Assessment saved={bundle.runs.find(r => r.evidence.run.run_id === state.comparisonRun)!} imageId={image.image_id} fixture={bundle.execution === 'fixture'} />}</> : <p className="small">Model comparison is unavailable: one qualifying run. API heatmaps and adjustable sensitivity are unavailable.</p>}
            </div>}
          </div></div>
        <nav className="image-navigation" aria-label="Challenge image navigation"><button disabled={index === 0} onClick={() => goImage(bundle.challenge.image_ids[index - 1])}>← Previous</button><div className="image-dots">{bundle.challenge.image_ids.map((id, n) => <button key={id} aria-label={`Go to image ${n + 1}${state.answers[id] ? ', answered' : ''}`} aria-current={id === state.selectedImage ? 'step' : undefined} onClick={() => goImage(id)}>{n + 1}{state.answers[id] && <span aria-hidden="true"> ✓</span>}</button>)}</div>{index < 4 ? <button onClick={() => goImage(bundle.challenge.image_ids[index + 1])}>Next →</button> : <button onClick={() => goScreen('lab')}>Explore the lab →</button>}</nav>
        {count === 5 && <section className="challenge-summary" role="status"><h2>Your five-picture summary</h2><p>{correct} correct and {5 - correct} incorrect against the dataset reference.</p><p>Five curated examples do not establish human or model superiority.</p><button className="primary" onClick={() => goScreen('lab')}>Explore full-set evidence &amp; build a pilot brief →</button></section>}
      </>}
      {state.screen === 'lab' && <Lab key={resetEpoch} bundle={bundle} state={state} update={update} />}
      {state.screen !== 'start' && <><section className="track-note"><strong>Fasteners / metal_nut</strong><span>The optional metal-surface track is not part of this local fastener milestone.</span></section>
      <div className="reset-controls"><button onClick={() => setConfirmReset('current')}>Reset current track</button><button onClick={() => setConfirmReset('all')}>Reset all progress</button>{confirmReset && <div className="reset-confirmation" role="group" aria-label="Confirm progress reset"><p>Reset {confirmReset === 'all' ? 'all inspection progress' : 'fastener progress'}? Answers, assumptions and reasoning will be cleared from this app.</p><button onClick={reset}>Confirm reset</button><button onClick={() => setConfirmReset('')}>Keep progress</button></div>}</div></>}
    </main>
    <footer><p>{bundle.dataset.attribution} <a href={bundle.dataset.licence_url}>{bundle.dataset.licence}</a>. <a href={bundle.dataset.source_url}>Dataset source</a>.</p><p>Prototype, not production approval. No visitor-triggered AI calls. {persistent ? 'Progress is saved in this browser.' : 'Progress is in memory for this visit.'}</p></footer>
  </>;
}

export function App() {
  const [bundle, setBundle] = useState<Bundle | null>(null), [error, setError] = useState(''), [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); setError('');
    loadBundle(controller.signal).then(value => { if (!controller.signal.aborted) setBundle(value); }).catch(() => { if (!controller.signal.aborted) setError('Saved inspection evidence could not be loaded. Retry below. If this continues, the preview’s saved data needs to be restored.'); });
    return () => controller.abort();
  }, [retry]);
  if (bundle) return <Experience key={bundle.bundle_id} bundle={bundle} />;
  return <main className="loading-page"><p className="eyebrow">Public-data prototype</p><h1>AI Inspection Pilot Lab</h1>{error ? <div role="alert"><p>{error}</p><button onClick={() => setRetry(n => n + 1)}>Retry evidence</button></div> : <p role="status">Checking saved inspection evidence…</p>}</main>;
}
