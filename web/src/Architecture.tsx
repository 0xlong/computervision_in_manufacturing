import { useState } from 'react';
import type { CSSProperties } from 'react';
import './architecture.css';

const stops = [
  { title: 'Pick the pictures', hint: 'We start with public pictures and their reference answers. These stand in for factory parts.', x: 17, y: 25, mx: 25, my: 16 },
  { title: 'Ask the AI', hint: 'Before your visit, AI inspects the pictures without seeing the reference answers.', x: 50, y: 25, mx: 75, my: 16 },
  { title: 'Check & save', hint: 'We compare all AI answers with the references. Mistakes and failures stay in the saved evidence.', x: 83, y: 25, mx: 75, my: 50 },
  { title: 'Open the website', hint: 'The website opens those saved results. Your visit never calls an AI model.', x: 83, y: 77, mx: 25, my: 50 },
  { title: 'Try it yourself', hint: 'Judge the pictures and explore a workday. Your answers and assumptions stay in your browser.', x: 50, y: 77, mx: 25, my: 84 },
  { title: 'You decide', hint: 'Choose a next step and download your brief. A person decides; this demo cannot approve parts.', x: 17, y: 77, mx: 75, my: 84 },
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
  </svg>;
}

function position(stop: typeof stops[number]): CSSProperties {
  return { '--stop-x': `${stop.x}%`, '--stop-y': `${stop.y}%`, '--mobile-x': `${stop.mx}%`, '--mobile-y': `${stop.my}%` } as CSSProperties;
}

export function Architecture() {
  const [selected, setSelected] = useState(0);
  return <section className="architecture" aria-labelledby="architecture-title">
    <h1 id="architecture-title">How does it work?</h1>
    <div className="architecture-board" role="group" aria-label="Solution flow">
      <div className="architecture-guide">
        <div className="architecture-speech" id="architecture-hint" role="status" aria-live="polite" aria-atomic="true">
          <span className="architecture-step-count">{selected + 1} / {stops.length}</span>
          <p>{stops[selected].hint}</p>
        </div>
        <button className="architecture-next" onClick={() => setSelected(n => (n + 1) % stops.length)}>{selected === stops.length - 1 ? 'Again ↺' : 'Next stop →'}</button>
      </div>
      <div className="architecture-map">
        <span className="architecture-phase architecture-phase-before">Before you arrive</span>
        <span className="architecture-phase architecture-phase-you">Now it’s your turn</span>
        <svg className="architecture-road architecture-road-wide" viewBox="0 0 1000 600" preserveAspectRatio="none" aria-hidden="true"><path d="M170 150H830Q950 150 950 270V342Q950 462 830 462H170" /></svg>
        <svg className="architecture-road architecture-road-small" viewBox="0 0 400 600" preserveAspectRatio="none" aria-hidden="true"><path d="M100 96H300V300H100V504H300" /></svg>
        <span className="architecture-scenery architecture-scenery-one" aria-hidden="true">✳</span>
        <span className="architecture-scenery architecture-scenery-two" aria-hidden="true">✳</span>
        <ol className="architecture-stops">{stops.map((stop, n) => <li key={stop.title} style={position(stop)}>
          <button className="architecture-stop" aria-pressed={n === selected} aria-controls="architecture-hint" onClick={() => setSelected(n)}>
            <span className="architecture-stop-number" aria-hidden="true">{n + 1}</span>
            <Toy stop={n} /><span className="architecture-stop-title">{stop.title}</span>
          </button>
        </li>)}</ol>
        <span className="architecture-token" style={position(stops[selected])} aria-hidden="true"><svg viewBox="0 0 36 42" fill="none"><path d="M18 40 6 28h24Z" fill="#a6531b" /><rect x="2" y="2" width="32" height="31" rx="7" fill="white" stroke="#a6531b" strokeWidth="2.5" /><path d="m18 8 9 5v10l-9 5-9-5V13Z" fill="#e6eddc" stroke="#124f43" strokeWidth="2" /><circle cx="18" cy="18" r="4" fill="white" stroke="#124f43" strokeWidth="2" /></svg></span>
      </div>
      <p className="architecture-legend">Tap a stop or follow the picture. <span>Illustrated guide · saved AI results.</span></p>
    </div>
  </section>;
}
