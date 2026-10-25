import { useEffect, useRef, useState } from 'react';
import type { CSSProperties } from 'react';
import './architecture.css';

const components = [
  { title: 'Picture checks', tech: 'Python · Pillow', source: 'pipeline/prepare_inputs.py', icon: 0, x: 12, y: 15,
    hint: 'Checks the public pictures before preparation. The models receive pictures without the dataset’s answers or defect outlines.' },
  { title: 'Model runner', tech: 'Python · retry / resume', source: 'pipeline/run_gemini_evaluation.py', icon: 1, x: 37, y: 15,
    hint: 'During preparation, sends pictures to each model and saves the returned assessments, attempts and failures. This does not run when you visit or click the diagram.' },
  { title: 'Gemini 3.5 Flash-Lite', modelId: 'gemini-3.5-flash-lite', tech: 'AI model · Google API', source: 'web/public/evidence/configurations/eval-flash-lite-46e242a298f20b6f.json', icon: 8, x: 62, y: 15, external: true,
    hint: 'Receives pictures from the runner and returns its own assessment. One of two models in the current saved fastener results; calls happened during preparation.' },
  { title: 'Gemma 4 26B', modelId: 'gemma-4-26b-a4b-it', tech: 'AI model · Google API', source: 'web/public/evidence/configurations/eval-gemma-7292d2441bcfd2c1.json', icon: 8, x: 87, y: 15, external: true,
    hint: 'Receives pictures from the runner and returns a separate assessment. The current saved bundle has these two models; it has no third model’s results.' },
  { title: 'Check & package', tech: 'Python · evaluation', source: 'pipeline/evaluate_api.py · pipeline/public_bundle.py', icon: 2, x: 37, y: 43,
    hint: 'Compares saved assessments with dataset answers and checks the files. Counts errors and failures honestly before packaging the evidence.' },
  { title: 'Saved evidence', tech: 'JSON · pictures · outlines', source: 'web/public/evidence/', icon: 2, x: 62, y: 43,
    hint: 'Keeps both models’ real assessments, pictures, dataset answers and error counts in checked files. Visitors explore these saved results; no new assessment is requested.' },
  { title: 'Website host', tech: 'Vite · static files', source: 'web/dist/ · scripts/web.ps1', icon: 3, x: 87, y: 43,
    hint: 'Serves the website and saved evidence as files. The local website works; the planned VPS is not a verified deployment.' },
  { title: 'Evidence loader', tech: 'TypeScript · Ajv', source: 'web/src/bundle.ts', icon: 6, x: 87, y: 68,
    hint: 'Checks the saved files before the website uses them. Pictures load when needed; missing or incorrect evidence produces an error message.' },
  { title: 'Website app', tech: 'React · TypeScript', source: 'web/src/App.tsx', icon: 7, x: 62, y: 68,
    hint: 'Shows the inspection game and saved assessments. Your answers stay in your browser and are never sent to a model.' },
  { title: 'Workload calculator', tech: 'TypeScript functions', source: 'web/src/engine.ts', icon: 9, x: 37, y: 68,
    hint: 'Combines measured error rates with your assumptions to estimate review work and cost. These are calculations, not new AI results or measured factory savings.' },
  { title: 'Your saved progress', tech: 'Browser · localStorage', source: 'web/src/state.ts', icon: 10, x: 62, y: 89,
    hint: 'Keeps your judgments and settings in this browser. There is no server-side visitor database; if saving is blocked, the page still works until you leave.' },
  { title: 'Brief download', tech: 'Markdown · local file', source: 'web/src/brief.ts', icon: 5, x: 37, y: 89,
    hint: 'Builds a brief from the saved evidence, calculations and your decisions. The same inputs give the same file; no model call or upload is needed.' },
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
    <><path d="m8 5-6 7 6 7m8-14 6 7-6 7m-3-16-2 18" /></>,
    <><path d="M6 18a5 5 0 0 1-1-10 7 7 0 0 1 13-1 5.5 5.5 0 0 1 0 11Z" /><path d="m9 12 3-3 3 3m-3-3v7" /></>,
    <><path d="M4 5h16M4 12h16M4 19h16" /><circle cx="8" cy="5" r="2" fill="white" /><circle cx="16" cy="12" r="2" fill="white" /><circle cx="10" cy="19" r="2" fill="white" /></>,
    <><ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0" /></>,
  ];
  return <svg className="architecture-task-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{icons[kind]}</svg>;
}

const edges = [
  { source: 0, target: 1, d: 'M202 135H288', label: 'Pictures', x: 245, y: 118 },
  { source: 1, target: 2, d: 'M370 65V25H620V65', label: 'Pictures', x: 590, y: 22 },
  { source: 1, target: 3, d: 'M370 65V25H870V65', label: '', x: 0, y: 0 },
  { source: 2, target: 1, d: 'M620 205V242H420V205', label: 'Gemini assessment', x: 562, y: 239 },
  { source: 3, target: 1, d: 'M870 205V279H390V205', label: 'Gemma assessment', x: 746, y: 276 },
  { source: 0, target: 4, d: 'M120 205V410H288', label: 'Dataset answers', x: 202, y: 436, transfer: true },
  { source: 1, target: 4, d: 'M288 160H250V360H288', label: 'Saved assessments', x: 238, y: 312 },
  { source: 4, target: 5, d: 'M452 387H538', label: 'Evidence', x: 495, y: 370 },
  { source: 5, target: 6, d: 'M702 387H788', label: 'Files', x: 745, y: 370 },
  { source: 6, target: 7, d: 'M870 457V542', label: 'Files', x: 909, y: 507 },
  { source: 7, target: 8, d: 'M788 612H702', label: 'Checked data', x: 745, y: 595 },
  { source: 8, target: 9, d: 'M538 612H452', label: 'Rates + inputs', x: 495, y: 595 },
  { source: 8, target: 10, d: 'M620 682V731', label: 'Save / restore', x: 687, y: 716, both: true },
  { source: 9, target: 11, d: 'M370 682V731', label: 'Estimates', x: 419, y: 716 },
  { source: 8, target: 11, d: 'M538 636H495V779H452', label: 'Evidence', x: 495, y: 749 },
  { source: 10, target: 11, d: 'M538 824H452', label: 'Your decisions', x: 495, y: 852 },
];

function position(component: typeof components[number]): CSSProperties {
  return { '--stop-x': `${component.x}%`, '--stop-y': `${component.y}%` } as CSSProperties;
}

export function Architecture() {
  const [selected, setSelected] = useState(0);
  const viewport = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const area = viewport.current!;
    const center = () => { area.scrollLeft = components[selected].x / 100 * area.scrollWidth - area.clientWidth / 2; };
    center();
    const observer = new ResizeObserver(center);
    observer.observe(area);
    return () => observer.disconnect();
  }, [selected]);
  return <section className="architecture" aria-labelledby="architecture-title">
    <h1 id="architecture-title">Software architecture</h1>
    <div className="architecture-board" role="group" aria-label="Software components and data flow">
      <div className="architecture-guide">
        <div className="architecture-speech" id="architecture-hint" role="status" aria-live="polite" aria-atomic="true">
          <span className="architecture-step-count">{selected + 1} / {components.length}</span>
          <div><p>{components[selected].hint}</p><code className="architecture-source">{components[selected].source}</code></div>
        </div>
        <button className="architecture-next" onClick={() => setSelected(n => (n + 1) % components.length)}>{selected === components.length - 1 ? 'Restart ↺' : 'Next component →'}</button>
      </div>
      <div className="architecture-canvas">
        <div className="architecture-viewport" ref={viewport} tabIndex={0} role="region" aria-label="Software architecture diagram. Scroll horizontally to explore.">
          <div className="architecture-map">
            <svg className="architecture-road" viewBox="0 0 1000 900" preserveAspectRatio="none" aria-hidden="true">
              <defs>
                <marker id="architecture-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse"><path d="m0 0 7 3.5L0 7Z" /></marker>
                <marker id="architecture-arrow-active" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse"><path d="m0 0 7 3.5L0 7Z" /></marker>
              </defs>
              {edges.map(edge => <g key={edge.d}>
                <path className={`architecture-edge${edge.transfer ? ' architecture-transfer' : ''}${edge.both ? ' architecture-edge-both' : ''}${edge.target === selected || edge.source === selected ? ' architecture-edge-active' : ''}`} d={edge.d} />
              </g>)}
            </svg>
            {edges.filter(edge => edge.label).map(edge => <span key={edge.d} className="architecture-connection-label" style={{ left: `${edge.x / 10}%`, top: `${edge.y / 9}%` }} aria-hidden="true">{edge.label}</span>)}
            <ol className="architecture-stops">{components.map((component, n) => <li key={component.title} style={position(component)}>
              <button className={`architecture-stop${component.external ? ' architecture-external' : ''}`} data-model-id={component.modelId} aria-label={component.title} aria-pressed={n === selected} aria-controls="architecture-hint" aria-describedby={`architecture-tech-${n}`} onClick={() => setSelected(n)}>
                <TaskIcon kind={component.icon} />
                <span className="architecture-stop-title">{component.title}</span>
                <span id={`architecture-tech-${n}`} className="architecture-tech">{component.tech}</span>
              </button>
            </li>)}</ol>
            <span className="architecture-token" style={position(components[selected])} aria-hidden="true" />
          </div>
        </div>
      </div>
      <p className="architecture-legend"><span className="architecture-pan-hint">Swipe across or use Next component.</span><span>AI calls happen during preparation. You explore saved results; diagram clicks never call a model.</span></p>
    </div>
  </section>;
}
