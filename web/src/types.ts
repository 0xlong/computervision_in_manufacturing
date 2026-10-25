import type { Counts } from './engine';

export type Answer = 'looks_acceptable' | 'needs_review';
export type Decision = Answer | 'uncertain';
export type PilotDecision = 'Pilot with human review' | 'Collect more evidence' | 'Revise the approach';
export const pilotDecisions: PilotDecision[] = ['Pilot with human review', 'Collect more evidence', 'Revise the approach'];
export interface Asset { path: string; sha256: string; dimensions: { width_px: number; height_px: number } }
export interface ChallengeImage { image_id: string; label: 'normal' | 'anomalous'; display: Asset; mask: Asset | null }
export interface PlaybackCatalog { schema_version: 1; bundle_id: string; manifest_sha256: string; images: ChallengeImage[] }
export interface Attempt {
  number: number; status: string; reason: string; latency_ms: number | null;
  reported_model_version: string | null;
  response: { decision: Decision; observation: string } | null;
}
export interface Prediction { run_id: string; image_id: string; status: string; attempts: Attempt[] }
export interface Metrics extends Counts {
  anomalous: number; normal: number; recall: number | null; false_positive_rate: number | null;
  precision: number | null; review_count: number;
  recall_wilson_95: [number, number] | null; false_positive_rate_wilson_95: [number, number] | null;
}
export interface Evaluation {
  schema_version: 1; evidence_status: 'fixture' | 'development_only'; track_id: 'fasteners';
  run_id: string; model_id: string; manifest_sha256: string; inputs_sha256: string; evidence_sha256: string;
  expected: number; attempted: number; succeeded: number; failed: number; coverage: number | null;
  failure_breakdown: Record<string, number>; technical_reviews: { normal: number; anomalous: number };
  successful_output: Metrics; full_set_routing: Metrics; membership_sha256: string;
  images: { image_id: string; label: 'normal' | 'anomalous'; status: string; decision: Decision | null; review: boolean; technical_review: boolean }[];
  limitations: string[];
}
export interface SavedRun {
  evidence: {
    schema_version: 1; evidence_status: 'fixture' | 'development_only';
    run: {
      run_id: string; track_id: 'fasteners'; model_id: string; provider: 'gemini'; created_at: string;
      state: 'complete'; hashes: Record<string, string>; policy: string;
      inputs: { image_id: string; sha256: string }[];
    }; predictions: Prediction[];
  };
  report: Evaluation;
}
export interface Bundle {
  schema_version: 2; bundle_id: string; track_id: 'fasteners'; evidence_status: 'fixture' | 'development_only' | 'authentic';
  execution: 'fixture' | 'recorded_live';
  dataset: { dataset_id: 'mvtec_ad'; category: 'metal_nut'; attribution: string; licence: string; licence_url: string; source_url: string; modification_notice: string };
  manifest_sha256: string; challenge: { version: string; image_ids: string[]; rationale: string };
  images: ChallengeImage[]; runs: SavedRun[]; limitations: string[];
  notices: { path: string; sha256: string }[];
  configuration_assets: { run_id: string; path: string; sha256: string }[];
}
