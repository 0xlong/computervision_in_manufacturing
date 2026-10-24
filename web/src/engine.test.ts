import { describe, expect, it } from 'vitest';
import { defaultScenario, projections, scenarioErrors } from './engine';

describe('workload uses complete-set routing rates and unrounded values', () => {
  const counts = { tp: 8, fn: 2, fp: 9, tn: 81 };
  it('charges for caught defects and unnecessary reviews, then missed defects', () => {
    const p = projections(defaultScenario, counts)!;
    expect(p.caught).toBe(8);
    expect(p.missed).toBeCloseTo(2);
    expect(p.unnecessaryReviews).toBe(99);
    expect(p.reviews).toBe(107);
    expect(p.reviewMinutes).toBe(214);
    expect(p.reviewCost).toBe(214);
    expect(p.totalCost).toBeCloseTo(414);
    expect(p.capacityExcess).toBe(0);
  });
  it('supports zero and full prevalence, zero capacity/cost and fractional review time', () => {
    expect(projections({ ...defaultScenario, prevalence: 0 }, counts)?.missed).toBe(0);
    expect(projections({ ...defaultScenario, prevalence: 1 }, counts)?.unnecessaryReviews).toBe(0);
    expect(projections({ ...defaultScenario, volume: 0 }, counts)?.reviews).toBe(0);
    const p = projections({ ...defaultScenario, minutes: .125, capacity: 0, reviewCost: 0, missedCost: 0 }, counts)!;
    expect(p.capacityExcess).toBe(13.375);
    expect(p.totalCost).toBe(0);
  });
  it.each([NaN, Infinity, -1])('rejects invalid assumption %s', value => {
    for (const key of Object.keys(defaultScenario)) {
      const s = { ...defaultScenario, [key]: value };
      expect(Object.keys(scenarioErrors(s))).toContain(key);
      expect(projections(s, counts)).toBeNull();
    }
  });
  it('rejects fractional volume, invalid prevalence and overflowing projections', () => {
    expect(projections({ ...defaultScenario, volume: .5 }, counts)).toBeNull();
    expect(projections({ ...defaultScenario, prevalence: 1.1 }, counts)).toBeNull();
    expect(projections({ ...defaultScenario, missedCost: Number.MAX_VALUE }, counts)).toBeNull();
  });
  it('does not invent a rate when an evaluated class is absent', () => {
    expect(projections(defaultScenario, { tp: 0, fn: 0, fp: 1, tn: 2 })).toBeNull();
    expect(projections(defaultScenario, { tp: 1, fn: 2, fp: 0, tn: 0 })).toBeNull();
    expect(projections(defaultScenario, { ...counts, fn: -1 })).toBeNull();
  });
});
