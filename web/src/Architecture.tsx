import { useEffect, useRef, useState } from 'react';
import type { CSSProperties } from 'react';
import './architecture.css';

const stops = [
  { title: 'Pick the pictures', hint: 'We start with public pictures and their reference answers. These stand in for factory parts.', x: 20, y: 15, icon: 0 },
  { title: 'Ask the AI', hint: 'Before your visit, AI inspects the pictures without seeing the reference answers.', x: 47, y: 15, icon: 1 },
  { title: 'Check & save', hint: 'We compare all AI answers with the references. Mistakes and failures stay in the saved evidence.', x: 78, y: 15, icon: 2 },
  { title: 'Open the website', hint: 'The website opens those saved results. Your visit never calls an AI model.', x: 20, y: 48, icon: 3 },
  { title: 'Try it yourself', hint: 'First, judge a picture yourself. Your answers and workday assumptions stay in your browser.', x: 47, y: 82, icon: 4 },
  { title: 'Answered?', hint: 'Your answer unlocks the reveal. Try either path here—these example choices do not change your inspection answers.', x: 47, y: 48, icon: -1 },
  { title: 'Reveal saved answers', hint: 'After you answer, reveal the saved AI answer and the dataset reference. They stay separate from your judgment.', x: 78, y: 48, icon: 6 },
  { title: 'You decide', hint: 'Explore a workday, choose a next step and download your brief. A person decides; this demo cannot approve parts.', x: 78, y: 82, icon: 5 },
];

// Process symbols describe the architecture; they are not inspection evidence.
function TaskIcon({ kind }: { kind: number }) {
  const icons = [
    <><rect x="4" y="4" width="16" height="16" rx="2" /><circle cx="9" cy="9" r="1.5" /><path d="m4 17 5-5 4 4 3-3 4 4" /></>,
    <><rect x="6" y="6" width="12" height="12" rx="2" /><path d="M9 2v4m6-4v4m-6 12v4m6-4v4M2 9h4m-4 6h4m12-6h4m-4 6h4" /><path d="M10 10h4v4h-4Z" /></>,
    <><path d="M4 8h16v12H4ZM3 4h18v4H3Z" /><path d="m9 13 2 2 4-4" /></>,
    <><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M3 9h18M7 6.5h.01m3 0h.01M7 13h5m-5 3h10" /></>,
    <><circle cx="12" cy="7" r="4" /><path d="M4 21v-2a8 8 0 0 1 16 0v2M8 21h8" /></>,
    <><path d="M14 3H5v18h14V8ZM14 3v5h5m-10 5h6m-6 4h6" /></>,
    <><rect x="3" y="6" width="8" height="14" rx="1" /><rect x="14" y="3" width="8" height="14" rx="1" /><path d="M6 10h2m-2 4h2m9-7h2m-2 4h2" /></>,
  ];
  return <svg className="architecture-task-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{icons[kind]}</svg>;
}

const edges = [
  { target: 0, d: 'M106 99H118' },
  { target: 1, d: 'M282 99H388' },
  { target: 2, d: 'M552 99H698' },
  { target: 3, d: 'M780 164V213H200V252', transfer: true },
  { target: 4, d: 'M200 382V541H388' },
  { target: 5, d: 'M470 476V374' },
  { target: 4, d: 'M410 317H338V541H388' },
  { target: 6, d: 'M530 317H698' },
  { target: 7, d: 'M780 382V476' },
  { target: 7, d: 'M862 541H914' },
];

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
    <h1 id="architecture-title">How the solution works</h1>
    <div className="architecture-board" role="group" aria-label="Solution flow">
      <div className="architecture-guide">
        <div className="architecture-speech" id="architecture-hint" role="status" aria-live="polite" aria-atomic="true">
          <span className="architecture-step-count">{selected + 1} / {stops.length}</span>
          <p>{stops[selected].hint}</p>
        </div>
        <div className="architecture-actions">
          {selected === 5 && <button key="back" className="architecture-back" onClick={() => setSelected(4)}>Not yet ↩</button>}
          <button key="forward" className="architecture-next" onClick={() => setSelected(n => (n + 1) % stops.length)}>{selected === stops.length - 1 ? 'Restart ↺' : selected === 5 ? 'Yes →' : 'Next step →'}</button>
        </div>
      </div>
      <div className="architecture-canvas">
        <div className="architecture-lanes" aria-hidden="true"><span>Before your visit</span><span>The website</span><span>You</span></div>
        <div className="architecture-viewport" ref={viewport} tabIndex={0} role="region" aria-label="Architecture diagram. Scroll horizontally to explore.">
        <div className="architecture-map">
        <svg className="architecture-road" viewBox="0 0 1000 660" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <marker id="architecture-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="m0 0 7 3.5L0 7Z" /></marker>
            <marker id="architecture-arrow-active" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="m0 0 7 3.5L0 7Z" /></marker>
          </defs>
          {edges.map(edge => <path key={edge.d} className={`architecture-edge${edge.transfer ? ' architecture-transfer' : ''}${edge.target === selected ? ' architecture-edge-active' : ''}`} d={edge.d} />)}
          <text x="88" y="66">Start</text><text x="933" y="581">Your brief</text><text className="architecture-branch-label" x="601" y="303">Yes</text><text className="architecture-branch-label" x="374" y="302">Not yet</text>
        </svg>
        <span className="architecture-event architecture-start" aria-hidden="true" /><span className="architecture-event architecture-end" aria-hidden="true" />
        <ol className="architecture-stops">{stops.map((stop, n) => <li key={stop.title} style={position(stop)}>
          <button className={`architecture-stop${stop.icon === -1 ? ' architecture-gateway' : ''}`} aria-label={stop.title} aria-pressed={n === selected} aria-controls="architecture-hint" aria-describedby={`architecture-role-${n}`} onClick={() => setSelected(n)}>
            {stop.icon === -1 ? <span className="architecture-question" aria-hidden="true">×</span> : <TaskIcon kind={stop.icon} />}<span className="architecture-stop-title">{stop.title}</span>
            <span id={`architecture-role-${n}`} className="sr-only">{n < 3 ? 'Before your visit' : n === 4 || n === 7 ? 'You' : 'The website'}</span>
          </button>
        </li>)}</ol>
        <span className={`architecture-token${selected === 5 ? ' architecture-token-gateway' : ''}`} style={position(stops[selected])} aria-hidden="true" />
        </div></div>
      </div>
      <p className="architecture-legend"><span className="architecture-pan-hint">Swipe across or use Next step.</span><span>Process guide · saved AI results.</span></p>
    </div>
  </section>;
}
