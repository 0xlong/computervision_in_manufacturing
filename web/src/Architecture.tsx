import { useEffect, useRef, useState } from 'react';
import type { CSSProperties } from 'react';
import './architecture.css';

const zones = ['Preparation', 'Static delivery', 'Browser runtime'];
const components = [
  { title: 'Data preparation', tech: 'Python · Pillow', source: 'pipeline/prepare_inputs.py', icon: 0, zone: 0, x: 14, y: 16.667,
    hint: 'Checks public MVTec images, hashes and fixed manifests. Model inputs exclude reference labels and masks; evaluation reads those references separately.' },
  { title: 'API runner', tech: 'Python · retry / resume', source: 'pipeline/run_gemini_evaluation.py', icon: 1, zone: 0, x: 38, y: 16.667,
    hint: 'Sends label-free images and permitted normal references through the provider adapter. Saves attempts, real responses and failures; credentials stay in preparation.' },
  { title: 'Gemini API', tech: 'External · Gemini / Gemma', source: 'pipeline/gemini_transport.py', icon: 8, zone: 0, x: 62, y: 16.667, external: true,
    hint: 'External Google service used for the saved Gemini and Gemma runs. HTTPS requests happen only during verified free preparation, never during a visitor session. OpenAI is not enabled.' },
  { title: 'Evaluation & packaging', tech: 'Python · metrics / validation', source: 'pipeline/evaluate_api.py · pipeline/public_bundle.py', icon: 2, zone: 0, x: 86, y: 16.667,
    hint: 'Compares saved outputs with references separately, computes full-set coverage and errors, and validates public artifacts. Failures and provenance remain part of the evidence.' },
  { title: 'Evidence bundle', tech: 'JSON · images · masks', source: 'web/public/evidence/', icon: 2, zone: 1, x: 24, y: 45,
    hint: 'Versioned static evidence contains authentic predictions, evaluation reports, pictures, reference masks and attribution. Shared JSON Schema contracts define the saved data; this is not a database.' },
  { title: 'Static web host', tech: 'Vite output · HTTP files', source: 'web/dist/ · scripts/web.ps1', icon: 3, zone: 1, x: 70, y: 45,
    hint: 'Vite builds HTML, JavaScript and CSS; the host serves them with the evidence files. The local preview works. The Infomaniak VPS is a target, not a verified deployment; no inference backend runs here.' },
  { title: 'Evidence loader', tech: 'TypeScript · Ajv', source: 'web/src/bundle.ts', icon: 6, zone: 2, x: 14, y: 68.889,
    hint: 'Fetches the bundle over HTTP and validates its JSON Schema, identities, counts and references before the app uses it. Pictures and playback data load as needed.' },
  { title: 'React application', tech: 'React · TypeScript', source: 'web/src/App.tsx', icon: 7, zone: 2, x: 42, y: 68.889,
    hint: 'Renders the inspection screens from validated evidence and local visitor state. It coordinates the calculation and export modules; it never sends visitor answers to a model.' },
  { title: 'Policy & scenario engine', tech: 'Pure TypeScript functions', source: 'web/src/engine.ts', icon: 9, zone: 2, x: 73, y: 68.889,
    hint: 'Uses fixed review routing and measured rates with visitor assumptions to calculate workload and cost. These are local calculations, not live AI inference or measured factory savings.' },
  { title: 'Visitor state', tech: 'Versioned localStorage', source: 'web/src/state.ts', icon: 10, zone: 2, x: 42, y: 90.556,
    hint: 'Stores judgments, settings and reasoning in this browser, with schema checks and reset support. There is no server-side visitor database; blocked storage falls back to memory.' },
  { title: 'Brief builder', tech: 'Markdown · local download', source: 'web/src/brief.ts', icon: 5, zone: 2, x: 73, y: 90.556,
    hint: 'Combines validated evidence, calculations and visitor state into a deterministic Markdown file. Identical inputs produce identical content; no LLM or upload is involved.' },
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
  { target: 1, d: 'M220 150H300', label: 'image inputs', x: 260, y: 133 },
  { target: 2, d: 'M460 137H540', label: 'HTTPS', x: 500, y: 120 },
  { target: 1, d: 'M540 174H460', label: 'JSON', x: 500, y: 198 },
  { target: 3, d: 'M140 80V30H860V80', label: 'reference labels · evaluation only', x: 500, y: 20, transfer: true },
  { target: 3, d: 'M380 220V260H750V150H780', label: 'saved attempts & responses', x: 560, y: 283 },
  { target: 4, d: 'M860 220V312H240V335', label: 'validated artifacts', x: 540, y: 304 },
  { target: 5, d: 'M320 405H620', label: 'release files + Vite build', x: 470, y: 388 },
  { target: 6, d: 'M700 475V523H140V550', label: 'HTTP GET · static files', x: 430, y: 515 },
  { target: 7, d: 'M220 620H340', label: 'validated data', x: 280, y: 603 },
  { target: 8, d: 'M500 620H650', label: 'rates + assumptions', x: 575, y: 603 },
  { target: 9, d: 'M420 690V745', label: 'read / write', x: 480, y: 725, both: true },
  { target: 10, d: 'M730 690V745', label: 'projections', x: 790, y: 725 },
  { target: 10, d: 'M500 642H600V815H650', label: 'bundle', x: 622, y: 744 },
  { target: 10, d: 'M500 815H650', label: 'visitor state', x: 555, y: 798 },
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
        <div className="architecture-lanes" aria-hidden="true">{zones.map(zone => <span key={zone}>{zone}</span>)}</div>
        <div className="architecture-viewport" ref={viewport} tabIndex={0} role="region" aria-label="Software architecture diagram. Scroll horizontally to explore.">
          <div className="architecture-map">
            <svg className="architecture-road" viewBox="0 0 1000 900" preserveAspectRatio="none" aria-hidden="true">
              <defs>
                <marker id="architecture-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse"><path d="m0 0 7 3.5L0 7Z" /></marker>
                <marker id="architecture-arrow-active" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse"><path d="m0 0 7 3.5L0 7Z" /></marker>
              </defs>
              {edges.map(edge => <g key={edge.d}>
                <path className={`architecture-edge${edge.transfer ? ' architecture-transfer' : ''}${edge.both ? ' architecture-edge-both' : ''}${edge.target === selected ? ' architecture-edge-active' : ''}`} d={edge.d} />
              </g>)}
            </svg>
            {edges.map(edge => <span key={edge.d} className="architecture-connection-label" style={{ left: `${edge.x / 10}%`, top: `${edge.y / 9}%` }} aria-hidden="true">{edge.label}</span>)}
            <ol className="architecture-stops">{components.map((component, n) => <li key={component.title} style={position(component)}>
              <button className={`architecture-stop${component.external ? ' architecture-external' : ''}`} aria-label={component.title} aria-pressed={n === selected} aria-controls="architecture-hint" aria-describedby={`architecture-role-${n}`} onClick={() => setSelected(n)}>
                <TaskIcon kind={component.icon} />
                <span className="architecture-stop-title">{component.title}</span>
                <span className="architecture-tech">{component.tech}</span>
                <span id={`architecture-role-${n}`} className="sr-only">{zones[component.zone]}{component.external ? ', external service' : ''}</span>
              </button>
            </li>)}</ol>
            <span className="architecture-token" style={position(components[selected])} aria-hidden="true" />
          </div>
        </div>
      </div>
      <p className="architecture-legend"><span className="architecture-pan-hint">Swipe across or use Next component.</span><span>AI runs in preparation · visitor state stays in the browser.</span></p>
    </div>
  </section>;
}
