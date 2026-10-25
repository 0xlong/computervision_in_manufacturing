import { useCallback, useEffect, useRef, useState } from 'react';
import { loadBundle } from './bundle';
import { answerImage, freshState, loadState, revealImage, storageKey } from './state';
import type { VisitorState } from './state';
import type { Answer, Bundle } from './types';
import { scenarioErrors } from './engine';
import { Picture } from './Picture';
import { Lab } from './Lab';
import { AnswerCard, Assessment, AssessmentDetails, answerLabel } from './Assessment';
import { Watch } from './Watch';

function Experience({ bundle }: { bundle: Bundle }) {
  const [loaded] = useState(() => {
    try { return loadState(window.localStorage, bundle); }
    catch { return { state: freshState(bundle), notice: 'Browser storage is unavailable. Progress stays in memory for this visit.', persistent: false }; }
  });
  const [watch, setWatch] = useState(false), [watchOpened, setWatchOpened] = useState(false);
  const openWatch = () => { setWatchOpened(true); setWatch(true); document.getElementById('main')?.focus(); window.scrollTo(0, 0); };
  const [state, setState] = useState(loaded.state), [notice, setNotice] = useState(loaded.notice);
  const [persistent, setPersistent] = useState(loaded.persistent), [confirmReset, setConfirmReset] = useState('');
  const [pictureReady, setPictureReady] = useState(false), [resetEpoch, setResetEpoch] = useState(0);
  const revealRef = useRef<HTMLDivElement>(null);
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
  useEffect(() => { if (revealed && state.screen === 'inspect') revealRef.current?.focus(); }, [revealed, image.image_id, state.screen]);
  const selected = bundle.runs.find(r => r.evidence.run.run_id === state.selectedRun)!;
  const prediction = selected.evidence.predictions.find(p => p.image_id === image.image_id)!;
  const aiAnswer = prediction.status === 'success' ? prediction.attempts.at(-1)!.response?.decision : null;
  const agreement = !aiAnswer ? 'AI assessment unavailable' : aiAnswer === 'uncertain' ? 'AI is unsure — human check needed'
    : aiAnswer !== answered ? 'You and AI disagree' : ((answered === 'needs_review') === (image.label === 'anomalous')) ? 'You and AI agree' : 'You and AI agree · reference differs';
  const count = Object.keys(state.answers).length;
  const correct = bundle.images.filter(i => state.answers[i.image_id] && ((state.answers[i.image_id] === 'needs_review') === (i.label === 'anomalous'))).length;
  const goImage = (id: string) => { if (id === state.selectedImage) return; setPictureReady(false); update({ selectedImage: id }); document.getElementById('inspection-title')?.focus(); window.scrollTo(0, 0); };
  const goScreen = (screen: VisitorState['screen']) => { setWatch(false); update({ screen }); document.getElementById('main')?.focus(); window.scrollTo(0, 0); };
  function reset() { setState(freshState(bundle)); setResetEpoch(n => n + 1); setConfirmReset(''); setNotice('Fastener progress has been reset.'); }
  return <>
    <a className="skip-link" href="#main">Skip to content</a>
    <header className="site-header"><a href="#main" className="brand" onClick={() => goScreen('start')}><span aria-hidden="true" className="brand-mark">◈</span><span>Manufacturing<span className="brand-light"> / AI Inspection</span></span></a>
      {(state.screen !== 'start' || watch) && <nav aria-label="Main navigation"><button aria-current={!watch && state.screen === 'inspect' ? 'page' : undefined} onClick={() => goScreen('inspect')}>Try it</button><button aria-current={watch ? 'page' : undefined} onClick={openWatch}>Watch AI Inspect</button><button aria-current={!watch && state.screen === 'lab' ? 'page' : undefined} onClick={() => goScreen('lab')}>Results</button></nav>}</header>
    <main id="main" tabIndex={-1}>
      <div className="context-bar"><span>Public-data demo</span></div>
      {bundle.execution === 'fixture' && <p className="development-notice">TEST EXAMPLES ONLY — invented model answers; not real AI evidence.</p>}
      {notice && <p className="notice" role="status">{notice}</p>}
      {!watch && state.screen === 'start' && <section className="hero"><h1>AI Visual Inspection<br /><em>for Manufacturing</em></h1><p className="hero-copy">Computer vision for quality control. Try five parts.</p>
        <div className="hero-actions"><button className="primary" onClick={() => goScreen('inspect')}>Try it →</button><button onClick={openWatch}>Watch AI Inspect</button><button className="text-button" onClick={() => goScreen('lab')}>See the results →</button></div>
        <p className="prototype-note">A public-image demo, not factory validation.</p></section>}
      {watchOpened && <Watch bundle={bundle} active={watch} />}
      {!watch && state.screen === 'inspect' && <>
        <section className="section-heading"><h1 id="inspection-title" tabIndex={-1}>Does this part need checking?</h1></section>
        <div className="challenge-progress"><strong>Image {index + 1} of 5</strong><span>{count} of 5 answered</span><progress max={5} value={count} aria-label="Challenge answers completed" /></div>
        <div className="inspection-layout"><Picture key={`${image.image_id}-${resetEpoch}`} image={image} revealed={revealed} onReady={readyCallback} />
          <div className="judgment-panel">
            {!revealed && <div className="answer-buttons">{(['looks_acceptable', 'needs_review'] as Answer[]).map(answer => <button key={answer} aria-pressed={answered === answer} disabled={!pictureReady} onClick={() => setState(s => answerImage(s, image.image_id, answer))}>{answerLabel(answer)}</button>)}</div>}
            {!revealed && <button className="primary reveal-button" disabled={!answered || !pictureReady} onClick={() => setState(s => revealImage(s, image.image_id))}>Reveal AI assessment</button>}
            {!revealed && <p className="small answer-hint">{answered ? 'Ready? Reveal the AI answer.' : 'Choose your answer first.'}</p>}
            {revealed && <div className="reveal" ref={revealRef} tabIndex={-1} aria-label="Revealed assessment"><p className="comparison-summary">{agreement}</p><div className="answer-comparison" role="group" aria-label="Answer comparison">
              <AnswerCard title="Your answer" value={answerLabel(answered)} detail={((answered === 'needs_review') === (image.label === 'anomalous')) ? 'Matches reference' : 'Differs from reference'} tone={((answered === 'needs_review') === (image.label === 'anomalous')) ? 'match' : 'mismatch'} />
              <Assessment saved={selected} imageId={image.image_id} reference={image.label} />
              <AnswerCard title="Dataset reference" value={image.label === 'normal' ? 'Looks fine' : 'Needs checking'} detail={image.label === 'normal' ? 'No defect labelled' : 'Defect labelled'} tone="reference" />
              </div>
              <AssessmentDetails saved={selected} imageId={image.image_id} fixture={bundle.execution === 'fixture'} />
              <details><summary>More about these answers</summary><p>Your answer {((answered === 'needs_review') === (image.label === 'anomalous')) ? 'matches' : 'differs from'} the dataset reference. It stays fixed until you reset your progress. Dataset labels are learning references, not factory approval.</p>
                {bundle.runs.length > 1 ? <><label>Saved model <select value={state.selectedRun} onChange={e => update({ selectedRun: e.target.value, comparisonRun: '' })}>{bundle.runs.map(r => <option key={r.evidence.run.run_id} value={r.evidence.run.run_id}>{r.evidence.run.model_id}</option>)}</select></label><label>Compare with <select value={state.comparisonRun} onChange={e => update({ comparisonRun: e.target.value })}><option value="">No comparison</option>{bundle.runs.filter(r => r.evidence.run.run_id !== state.selectedRun).map(r => <option key={r.evidence.run.run_id} value={r.evidence.run.run_id}>{r.evidence.run.model_id}</option>)}</select></label>{state.comparisonRun && <><Assessment saved={bundle.runs.find(r => r.evidence.run.run_id === state.comparisonRun)!} imageId={image.image_id} reference={image.label} /><AssessmentDetails saved={bundle.runs.find(r => r.evidence.run.run_id === state.comparisonRun)!} imageId={image.image_id} fixture={bundle.execution === 'fixture'} /></>}</> : <p>Model comparison is unavailable: one qualifying run.</p>}
                <p>AI heatmaps and adjustable sensitivity are unavailable. These are saved answers; your visit makes no AI requests.</p></details>
            </div>}
          </div></div>
        <nav className="image-navigation" aria-label="Challenge image navigation"><button disabled={index === 0} onClick={() => goImage(bundle.challenge.image_ids[index - 1])}>← Previous</button><div className="image-dots">{bundle.challenge.image_ids.map((id, n) => <button key={id} aria-label={`Go to image ${n + 1}${state.answers[id] ? ', answered' : ''}`} aria-current={id === state.selectedImage ? 'step' : undefined} onClick={() => goImage(id)}>{n + 1}{state.answers[id] && <span aria-hidden="true"> ✓</span>}</button>)}</div>{index < 4 ? <button onClick={() => goImage(bundle.challenge.image_ids[index + 1])}>Next →</button> : <button onClick={() => goScreen('lab')}>See all results →</button>}</nav>
        {count === 5 && <section className="challenge-summary" role="status"><h2>Your five-picture summary</h2><p>{correct} correct · {5 - correct} incorrect against the dataset labels.</p><p className="small">Five selected examples aren’t a performance test.</p><button className="primary" onClick={() => goScreen('lab')}>See the full AI results →</button></section>}
      </>}
      {!watch && state.screen === 'lab' && <Lab key={resetEpoch} bundle={bundle} state={state} update={update} />}
      <details className="about-demo"><summary>About this demo{state.screen !== 'start' ? ' & reset progress' : ''}</summary>
        <p>{bundle.execution === 'fixture' ? 'This test preview uses invented AI answers.' : `The AI answers are saved responses from all ${selected.report.expected} test images. Your visit makes no AI requests.`} Your answers stay in this browser.</p>
        <p>Five selected teaching pictures, not a representative factory sample. Dataset: {bundle.dataset.dataset_id} / {bundle.dataset.category}. The optional metal-surface track is unavailable.</p>
        <p>Local development preview, not factory validation. Dataset source records have limitations; this preview is not cleared for publication. No manufacturer affiliation is implied.</p>
        <p>{bundle.dataset.attribution} <a href={bundle.dataset.licence_url}>{bundle.dataset.licence}</a>. <a href={bundle.dataset.source_url}>Dataset source</a>.</p>
        {state.screen !== 'start' && <div className="reset-controls"><button onClick={() => setConfirmReset('current')}>Reset current track</button><button onClick={() => setConfirmReset('all')}>Reset all progress</button>{confirmReset && <div className="reset-confirmation" role="group" aria-label="Confirm progress reset"><p>Reset {confirmReset === 'all' ? 'all inspection progress' : 'fastener progress'}? Answers, assumptions and reasoning will be cleared from this app.</p><button onClick={reset}>Confirm reset</button><button onClick={() => setConfirmReset('')}>Keep progress</button></div>}</div>}
      </details>
    </main>
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
  return <main className="loading-page"><p className="eyebrow">Public-data demo</p><h1>AI Visual Inspection for Manufacturing</h1>{error ? <div role="alert"><p>{error}</p><button onClick={() => setRetry(n => n + 1)}>Retry evidence</button></div> : <p role="status">Loading…</p>}</main>;
}
