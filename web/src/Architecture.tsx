import { useState } from 'react';
import './architecture.css';

const steps = [
  {
    title: 'Public pictures', caption: 'Collect & check',
    icon: <><rect x="3" y="3" width="18" height="18" rx="3" /><circle cx="8" cy="8" r="1" /><path d="m3 17 6-6 5 5 3-3 4 4" /></>,
    heading: 'Start with traceable pictures.',
    description: 'Public manufacturing datasets provide the pictures and reference labels. Preparation checks files, records their source and fixes which pictures belong to each set.',
    output: 'Checked images, fixed image lists and attribution',
    boundary: 'The working fastener demo uses MVTec AD metal nuts as a proxy. The sheet-metal track is planned; these are not factory images.',
  },
  {
    title: 'AI assessments', caption: 'Run once & save',
    icon: <><path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5Z" /></>,
    heading: 'Ask the models before the visit.',
    description: 'A separate Python preparation process sends image pixels, neutral IDs and permitted normal examples to the selected models. Each real answer, observation and failed attempt is saved for later use.',
    output: 'Saved model answers and execution records',
    boundary: 'Reference labels and defect outlines are kept out of model requests. Only verified free access is allowed; there are no visitor-triggered AI calls.',
  },
  {
    title: 'Checked evidence', caption: 'Evaluate & package',
    icon: <><path d="M7 3h10l4 4v14H3V3h4m10 0v5h4M7 14l3 3 7-7" /></>,
    heading: 'Check answers against the references.',
    description: 'Evaluation uses the reference labels separately to count missed defects, false alarms, coverage and failures across the complete declared test set. A bundle builder checks and packages the results with their sources.',
    output: 'Versioned pictures, predictions, reports and source records',
    boundary: 'Failed assessments stay visible and route to human review. Five curated challenge pictures do not replace the full benchmark.',
  },
  {
    title: 'Static website', caption: 'Load saved evidence',
    icon: <><rect x="2" y="4" width="20" height="16" rx="2" /><path d="M2 9h20M6 6.5h.01M9 6.5h.01" /></>,
    heading: 'Serve the evidence as ordinary files.',
    description: 'The React and TypeScript website loads the checked evidence bundle and pictures as needed. Try it hides the model answers until you answer; Watch replays saved results; Results shows the measured benchmark.',
    output: 'The same saved evidence for every visitor',
    boundary: 'No live model, account, upload or database is needed. The existing VPS is the hosting target; deployment has not been verified.',
  },
  {
    title: 'Your exploration', caption: 'Judge & calculate',
    icon: <><path d="M5 3v18M12 3v18M19 3v18" /><rect x="2" y="6" width="6" height="4" rx="1" /><rect x="9" y="14" width="6" height="4" rx="1" /><rect x="16" y="8" width="6" height="4" rx="1" /></>,
    heading: 'Explore the trade-offs in your browser.',
    description: 'Your judgments stay separate from the AI answers and dataset references. Workday calculations combine measured review and miss rates with the volume, costs and review capacity you enter.',
    output: 'Local progress and illustrative workload projections',
    boundary: 'Your answers and reasoning stay in this browser. Workday assumptions are illustrative; fixed API answers have no adjustable sensitivity or calibrated defect probability.',
  },
  {
    title: 'Human decision', caption: 'Decide & export',
    icon: <><path d="M14 3H4v18h16V11M12 3v7h7M8 15h8M8 18h5m3-15 5 5" /></>,
    heading: 'Leave the next step to a person.',
    description: 'Choose a pilot direction and add your reasoning. The browser builds a Markdown brief from the saved evidence, your assumptions and your decision. The same inputs produce the same brief, with no AI request.',
    output: 'A downloadable pilot brief with evidence and limitations',
    boundary: 'A real pilot still needs representative site images, a quality owner, agreed acceptance criteria and enough human review capacity. This demo does not approve parts.',
  },
];

export function Architecture() {
  const [selected, setSelected] = useState(0);
  const step = steps[selected];
  function selectStep(index: number, pointer: boolean) {
    setSelected(index);
    // A tap should reveal its explanation even when the diagram stacks on a phone.
    // Keyboard selection keeps the focused step in view and never moves focus.
    if (pointer) requestAnimationFrame(() => document.getElementById('architecture-detail')?.scrollIntoView({ block: 'nearest' }));
  }
  return <section className="architecture" aria-labelledby="architecture-title">
    <div className="architecture-heading"><p className="eyebrow">From pictures to a pilot decision</p>
      <h1 id="architecture-title">How it all fits together.</h1>
      <p>AI runs beforehand. You explore the evidence here.</p>
    </div>
    <div className="architecture-flow" role="group" aria-label="Solution flow">
      {[{ title: 'Before your visit', subtitle: 'Prepare the evidence', start: 0 }, { title: 'In your browser', subtitle: 'Explore & decide', start: 3 }].map((group, g) => <section className="architecture-lane" key={group.title} aria-labelledby={`architecture-lane-${g}`}>
        <div className="architecture-lane-heading"><h2 id={`architecture-lane-${g}`}>{group.title}</h2><span>{group.subtitle}</span></div>
        <ol start={group.start + 1}>{steps.slice(group.start, group.start + 3).map((item, i) => {
          const n = group.start + i;
          return <li key={item.title}><button aria-pressed={n === selected} aria-controls="architecture-detail" onClick={e => selectStep(n, e.detail > 0)}>
            <span className="architecture-node-top"><span className="architecture-number">0{n + 1}</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{item.icon}</svg></span>
            <span className="architecture-node-title">{item.title}</span><span className="architecture-caption">{item.caption}</span>
          </button></li>;
        })}</ol>
      </section>)}
    </div>
    <p className="architecture-hint">Select a step to look inside.</p>
    <section id="architecture-detail" className="architecture-detail" aria-labelledby="architecture-detail-title" aria-live="polite" aria-atomic="true">
      <div><p className="eyebrow">0{selected + 1} / {step.title}</p><h2 id="architecture-detail-title">{step.heading}</h2></div>
      <div className="architecture-detail-copy"><p>{step.description}</p><p className="architecture-output"><strong>Passed on</strong>{step.output}</p><p className="small">{step.boundary}</p></div>
    </section>
  </section>;
}
