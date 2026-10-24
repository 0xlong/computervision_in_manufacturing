import { defaultScenario, scenarioErrors } from './engine';
import type { Scenario } from './engine';
import { pilotDecisions } from './types';
import type { Answer, Bundle, PilotDecision } from './types';
import Ajv2020 from 'ajv/dist/2020';
import stateSchema from '../../schemas/visitor-state.v1.schema.json';

const validateState = new Ajv2020({ strict: false, strictNumbers: true }).compile(stateSchema);

export const storageKey = 'ai-inspection-pilot-lab:visitor:v1';
export interface VisitorState {
  schema_version: 1; bundle_id: string; track_id: 'fasteners';
  screen: 'start' | 'inspect' | 'lab'; selectedImage: string; selectedRun: string;
  comparisonRun: string; answers: Record<string, Answer>; revealed: string[];
  scenario: Scenario; decision: PilotDecision | ''; rationale: string;
}
export function freshState(bundle: Bundle): VisitorState {
  return { schema_version: 1, bundle_id: bundle.bundle_id, track_id: 'fasteners', screen: 'start',
    selectedImage: bundle.challenge.image_ids[0], selectedRun: bundle.runs[0].evidence.run.run_id,
    comparisonRun: '', answers: {}, revealed: [], scenario: { ...defaultScenario }, decision: '', rationale: '' };
}
export function answerImage(state: VisitorState, id: string, answer: Answer): VisitorState {
  if (state.revealed.includes(id)) return state;
  return { ...state, answers: { ...state.answers, [id]: answer } };
}
export function revealImage(state: VisitorState, id: string): VisitorState {
  if (!Object.hasOwn(state.answers, id) || state.revealed.includes(id)) return state;
  return { ...state, revealed: [...state.revealed, id] };
}
export interface StoragePort { getItem(key: string): string | null; setItem(key: string, value: string): void }
export function restoreState(raw: string | null, bundle: Bundle): { state: VisitorState; notice: string } {
  const fresh = freshState(bundle);
  if (raw === null) return { state: fresh, notice: '' };
  try {
    const s = JSON.parse(raw) as VisitorState;
    if (!validateState(s)) throw Error();
    if (s.bundle_id !== bundle.bundle_id) return { state: fresh, notice: 'The evidence bundle changed. Your challenge has restarted so answers and results stay together.' };
    const ids = bundle.challenge.image_ids, runs = bundle.runs.map(r => r.evidence.run.run_id);
    if (!['start', 'inspect', 'lab'].includes(s.screen) || !ids.includes(s.selectedImage) || !runs.includes(s.selectedRun) ||
      (s.comparisonRun !== '' && (!runs.includes(s.comparisonRun) || s.comparisonRun === s.selectedRun)) ||
      !s.answers || Array.isArray(s.answers) || typeof s.answers !== 'object' ||
      Object.entries(s.answers).some(([id, a]) => !ids.includes(id) || !['looks_acceptable', 'needs_review'].includes(a)) ||
      !Array.isArray(s.revealed) || new Set(s.revealed).size !== s.revealed.length || s.revealed.some(id => !ids.includes(id) || !Object.hasOwn(s.answers, id)) ||
      !s.scenario || Object.keys(defaultScenario).some(k => typeof s.scenario[k as keyof Scenario] !== 'number') || Object.keys(scenarioErrors(s.scenario)).length ||
      (s.decision !== '' && !pilotDecisions.includes(s.decision)) || typeof s.rationale !== 'string' || s.rationale.length > 2000) throw Error();
    // Copy only understood fields; do not retain untrusted properties from storage.
    return { state: { ...fresh, screen: s.screen, selectedImage: s.selectedImage, selectedRun: s.selectedRun,
      comparisonRun: s.comparisonRun, answers: { ...s.answers }, revealed: [...s.revealed],
      scenario: Object.fromEntries(Object.keys(defaultScenario).map(k => [k, s.scenario[k as keyof Scenario]])) as unknown as Scenario,
      decision: s.decision, rationale: s.rationale }, notice: '' };
  } catch {
    return { state: fresh, notice: 'Saved progress could not be read. A fresh challenge is ready; reset can replace the saved progress.' };
  }
}
export function loadState(storage: StoragePort, bundle: Bundle) {
  try { return { ...restoreState(storage.getItem(storageKey), bundle), persistent: true }; }
  catch { return { state: freshState(bundle), notice: 'Browser storage is unavailable. You can continue here, but progress will not survive closing this page.', persistent: false }; }
}
