import { useEffect, useRef, useState } from 'react';
import type { CSSProperties } from 'react';
import './architecture.css';

const stops = [
  { title: 'Pick the pictures', hint: 'We start with public pictures and their reference answers. These stand in for factory parts.', x: 20, y: 15, toy: 0 },
  { title: 'Ask the AI', hint: 'Before your visit, AI inspects the pictures without seeing the reference answers.', x: 47, y: 15, toy: 1 },
  { title: 'Check & save', hint: 'We compare all AI answers with the references. Mistakes and failures stay in the saved evidence.', x: 78, y: 15, toy: 2 },
  { title: 'Open the website', hint: 'The website opens those saved results. Your visit never calls an AI model.', x: 20, y: 48, toy: 3 },
  { title: 'Try it yourself', hint: 'First, judge a picture yourself. Your answers and workday assumptions stay in your browser.', x: 47, y: 82, toy: 4 },
  { title: 'Answered?', hint: 'Your answer unlocks the reveal. Try either path here—these example choices do not change your inspection answers.', x: 47, y: 48, toy: -1 },
  { title: 'Reveal saved answers', hint: 'After you answer, reveal the saved AI answer and the dataset reference. They stay separate from your judgment.', x: 78, y: 48, toy: 6 },
  { title: 'You decide', hint: 'Explore a workday, choose a next step and download your brief. A person decides; this demo cannot approve parts.', x: 78, y: 82, toy: 5 },
];

// Drawn teaching symbols, never dataset pictures or fabricated model evidence.
function Toy({ stop }: { stop: number }) {
  return <svg className="architecture-toy" viewBox="0 0 180 140" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <ellipse cx="90" cy="124" rx="69" ry="12" fill="#e0e9d7" stroke="none" />
    {stop === 0 && <>
      <rect x="39" y="22" width="91" height="88" rx="10" fill="#e6eddc" transform="rotate(-12 85 66)" />
      <rect x="52" y="24" width="91" height="88" rx="10" fill="white" transform="rotate(6 97 68)" />
      <path d="m94 41 25 14v28L94 97 69 83V55Z" fill="#e3ece8" /><circle cx="94" cy="69" r="12" fill="white" />
      <path d="m136 22 3-10m7 18 10-4M29 84l-9 3" />
    </>}
    {stop === 1 && <>
      <path d="M90 27V16m-25 91-8 12m58-12 8 12M42 75l-13 13m109-13 13 13" />
      <circle cx="90" cy="12" r="5" fill="#e5f2af" />
      <rect x="43" y="29" width="94" height="76" rx="23" fill="#124f43" />
      <rect x="54" y="42" width="72" height="43" rx="14" fill="#f6f7f2" />
      <circle cx="73" cy="61" r="5" fill="#124f43" /><circle cx="107" cy="61" r="5" fill="#124f43" />
      <path d="M81 73q9 7 18 0" /><path d="M78 96h24" stroke="#e5f2af" />
      <circle cx="27" cy="91" r="5" fill="#e6eddc" /><circle cx="153" cy="91" r="5" fill="#e6eddc" />
    </>}
    {stop === 2 && <>
      <path d="m40 63 50-17 50 17v45l-50 16-50-16Z" fill="#e6eddc" /><path d="m40 63 50 17 50-17M90 80v44" />
      <rect x="67" y="15" width="52" height="56" rx="6" fill="white" transform="rotate(8 93 43)" />
      <path d="m80 40 9 9 17-18M48 88l12 4m-12 7 12 4" />
      <path d="m40 63-13-15 48-16 15 14m50 17 13-15-22-7" fill="#e3ece8" />
    </>}
    {stop === 3 && <>
      <rect x="35" y="24" width="110" height="76" rx="9" fill="white" /><path d="M35 43h110" />
      <circle cx="45" cy="34" r="1" /><circle cx="53" cy="34" r="1" /><circle cx="61" cy="34" r="1" />
      <rect x="48" y="54" width="38" height="31" rx="4" fill="#e6eddc" /><path d="m59 65 8-5 8 5v10l-8 5-8-5Zm39-6h31m-31 10h23m-23 10h28" />
      <path d="m35 100-13 15q0 6 10 6h116q10 0 10-6l-13-15Z" fill="#e3ece8" /><path d="M73 111h34" />
    </>}
    {stop === 4 && <>
      <circle cx="72" cy="40" r="19" fill="#e6eddc" /><path d="M49 99V83q0-19 23-19t23 19v16" fill="#e6eddc" />
      <rect x="84" y="60" width="65" height="48" rx="8" fill="white" /><path d="M99 71v25m16-25v25m17-25v25" />
      <rect x="94" y="76" width="10" height="7" rx="2" fill="#124f43" /><rect x="110" y="85" width="10" height="7" rx="2" fill="#124f43" /><rect x="127" y="74" width="10" height="7" rx="2" fill="#124f43" />
      <path d="M57 100h-9l-8 18m-3-72-9-5m10-7-4-10" /><circle cx="65" cy="39" r="1" /><path d="M73 48q5 2 8-2" />
    </>}
    {stop === 5 && <>
      <path d="M52 120V22m0 1q22-17 43 0t37 0v45q-19 17-37 0T52 68" fill="#e6eddc" />
      <path d="m82 42 11 11 20-22" /><path d="M38 122h34" />
      <rect x="106" y="83" width="38" height="40" rx="5" fill="white" /><path d="M115 94h19m-19 9h19m-19 9h12" />
      <path d="m146 44 6-8m-7 22 11-1M29 30l-7-6" stroke="#a6531b" />
    </>}
    {stop === 6 && <>
      <rect x="25" y="35" width="57" height="77" rx="9" fill="#e6eddc" /><rect x="98" y="35" width="57" height="77" rx="9" fill="white" />
      <path d="M38 55h31m-31 12h24m-24 12h28m44-24h31m-31 12h24m-24 12h28" />
      <path d="M57 22q33-21 66 0m-6-9 7 10-12 2" /><circle cx="53" cy="95" r="4" fill="#124f43" /><circle cx="126" cy="95" r="4" fill="#124f43" />
    </>}
  </svg>;
}

function position(stop: typeof stops[number]): CSSProperties {
  return { '--stop-x': `${stop.x}%`, '--stop-y': `${stop.y}%` } as CSSProperties;
}

export function Architecture() {
  const [selected, setSelected] = useState(0);
  const viewport = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const area = viewport.current!;
    const center = () => { area.scrollLeft = stops[selected].x / 100 * area.scrollWidth - area.clientWidth / 2; };
    center();
    const observer = new ResizeObserver(center);
    observer.observe(area);
    return () => observer.disconnect();
  }, [selected]);
  return <section className="architecture" aria-labelledby="architecture-title">
    <h1 id="architecture-title">How does it work?</h1>
    <div className="architecture-board" role="group" aria-label="Solution flow">
      <div className="architecture-guide">
        <div className="architecture-speech" id="architecture-hint" role="status" aria-live="polite" aria-atomic="true">
          <span className="architecture-step-count">{selected + 1} / {stops.length}</span>
          <p>{stops[selected].hint}</p>
        </div>
        <div className="architecture-actions">
          {selected === 5 && <button key="back" className="architecture-back" onClick={() => setSelected(4)}>Not yet ↩</button>}
          <button key="forward" className="architecture-next" onClick={() => setSelected(n => (n + 1) % stops.length)}>{selected === stops.length - 1 ? 'Again ↺' : selected === 5 ? 'Yes →' : 'Next stop →'}</button>
        </div>
      </div>
      <div className="architecture-canvas">
        <div className="architecture-lanes" aria-hidden="true"><span>Before your visit</span><span>The website</span><span>You</span></div>
        <div className="architecture-viewport" ref={viewport} tabIndex={0} role="region" aria-label="Architecture diagram. Scroll horizontally to explore.">
        <div className="architecture-map">
        <svg className="architecture-road" viewBox="0 0 1000 660" preserveAspectRatio="none" aria-hidden="true">
          <defs><marker id="architecture-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="m0 0 7 3.5L0 7Z" /></marker></defs>
          <path className="architecture-edge" d="M106 99H118" /><path className="architecture-edge" d="M282 99H388" /><path className="architecture-edge" d="M552 99H698" />
          <path className="architecture-transfer architecture-edge" d="M780 174V213H200V242" />
          <path className="architecture-edge" d="M200 392V541H388" /><path className="architecture-edge" d="M470 466V374" />
          <path className="architecture-edge architecture-return" d="M410 317H338V541H388" />
          <path className="architecture-edge" d="M530 317H698" /><path className="architecture-edge" d="M780 392V466" />
          <path className="architecture-edge" d="M862 541H914" />
          <text x="88" y="66">Start</text><text x="933" y="581">Your brief</text><text className="architecture-branch-label" x="601" y="303">Yes</text><text className="architecture-branch-label" x="374" y="302">Not yet</text>
        </svg>
        <span className="architecture-event architecture-start" aria-hidden="true" /><span className="architecture-event architecture-end" aria-hidden="true" />
        <ol className="architecture-stops">{stops.map((stop, n) => <li key={stop.title} style={position(stop)}>
          <button className={`architecture-stop${stop.toy === -1 ? ' architecture-gateway' : ''}`} aria-label={stop.title} aria-pressed={n === selected} aria-controls="architecture-hint" aria-describedby={`architecture-role-${n}`} onClick={() => setSelected(n)}>
            <span className="architecture-stop-number" aria-hidden="true">{n + 1}</span>
            {stop.toy === -1 ? <span className="architecture-question" aria-hidden="true">?</span> : <Toy stop={stop.toy} />}<span className="architecture-stop-title">{stop.title}</span>
            <span id={`architecture-role-${n}`} className="sr-only">{n < 3 ? 'Before your visit' : n === 4 || n === 7 ? 'You' : 'The website'}</span>
          </button>
        </li>)}</ol>
        <span className={`architecture-token${selected === 5 ? ' architecture-token-gateway' : ''}`} style={position(stops[selected])} aria-hidden="true"><svg viewBox="0 0 36 42" fill="none"><path d="M18 40 6 28h24Z" fill="#a6531b" /><rect x="2" y="2" width="32" height="31" rx="7" fill="white" stroke="#a6531b" strokeWidth="2.5" /><path d="m18 8 9 5v10l-9 5-9-5V13Z" fill="#e6eddc" stroke="#124f43" strokeWidth="2" /><circle cx="18" cy="18" r="4" fill="white" stroke="#124f43" strokeWidth="2" /></svg></span>
        </div></div>
      </div>
      <p className="architecture-legend"><span className="architecture-pan-hint">Swipe across or use Next stop.</span><span>Illustrated guide · saved AI results.</span></p>
    </div>
  </section>;
}
