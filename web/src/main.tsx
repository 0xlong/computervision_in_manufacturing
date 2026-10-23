import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  return (
    <main>
      <p className="status">Development setup · Public-data prototype</p>
      <h1>AI Inspection Pilot Lab</h1>
      <p>The React and TypeScript development page is running.</p>
      <p>
        Inspection challenges and model evidence will be added after data and
        model feasibility checks. No inspection results are available yet.
      </p>
    </main>
  );
}

const root = document.getElementById('root');
if (!root) throw new Error('The application root element is missing.');
createRoot(root).render(<StrictMode><App /></StrictMode>);
