/** Pure workload calculations. Inputs are assumptions; rates describe saved routing. */
export interface Counts { tp: number; fn: number; fp: number; tn: number }
export interface Scenario {
  volume: number; prevalence: number; minutes: number; capacity: number;
  reviewCost: number; missedCost: number;
}
export const defaultScenario: Scenario = {
  volume: 1000, prevalence: 0.01, minutes: 2, capacity: 240, reviewCost: 1, missedCost: 100,
};
export const scenarioLabels: Record<keyof Scenario, string> = {
  volume: 'Components per day', prevalence: 'Assumed defective proportion (0–1)',
  minutes: 'Minutes per review', capacity: 'Available review minutes per day',
  reviewCost: 'Review cost (EUR per minute)', missedCost: 'Cost per missed defect (EUR)',
};
export type ScenarioErrors = Partial<Record<keyof Scenario, string>>;
export function scenarioErrors(input: Scenario): ScenarioErrors {
  const errors: ScenarioErrors = {};
  for (const key of Object.keys(defaultScenario) as (keyof Scenario)[]) {
    if (!Number.isFinite(input[key]) || input[key] < 0) errors[key] = 'Enter a finite number of zero or more.';
  }
  if (Number.isFinite(input.volume) && !Number.isSafeInteger(input.volume)) errors.volume = 'Enter a whole number of components within the supported range.';
  if (Number.isFinite(input.prevalence) && input.prevalence > 1) errors.prevalence = 'Enter a proportion between 0 and 1.';
  return errors;
}
export function projections(input: Scenario, counts: Counts) {
  if (Object.keys(scenarioErrors(input)).length) return null;
  if ([counts.tp, counts.fn, counts.fp, counts.tn].some(n => !Number.isSafeInteger(n) || n < 0)) return null;
  const positives = counts.tp + counts.fn, negatives = counts.fp + counts.tn;
  if (!positives || !negatives) return null;
  const recall = counts.tp / positives, fpr = counts.fp / negatives;
  const caught = input.volume * input.prevalence * recall;
  const missed = input.volume * input.prevalence * (1 - recall);
  const unnecessaryReviews = input.volume * (1 - input.prevalence) * fpr;
  const reviews = caught + unnecessaryReviews;
  const reviewMinutes = reviews * input.minutes;
  const reviewCost = reviewMinutes * input.reviewCost;
  const totalCost = reviewCost + missed * input.missedCost;
  const capacityExcess = Math.max(0, reviewMinutes - input.capacity);
  const result = { caught, missed, unnecessaryReviews, reviews, reviewMinutes, reviewCost, totalCost, capacityExcess };
  return Object.values(result).every(Number.isFinite) ? result : null;
}
export const formatNumber = (value: number | null, digits = 2) => value === null ? 'N/A' :
  value.toLocaleString('en-GB', { maximumFractionDigits: digits });
