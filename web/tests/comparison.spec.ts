import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import type { Bundle } from '../src/types';

const artifacts = resolve('../artifacts/model-comparison');

test('genuine complete-set comparison row shows real counts and measured request time', async ({ page, browser }) => {
  test.setTimeout(90000); // Multiple genuine rows and three responsive accessibility scans.
  const external: string[] = [], errors: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (!r.url().startsWith('http://127.0.0.1:4175') && !r.url().startsWith('blob:')) external.push(r.url()); });
  await page.goto('/');
  await page.getByRole('button', { name: 'See the results' }).click();
  const section = page.getByRole('region', { name: 'Compare models', exact: true });
  const table = section.getByRole('table');
  const row = table.getByRole('row').nth(1);
  const bundle = await page.request.get('/evidence/bundle.json').then(r => r.json()) as Bundle;
  if (bundle.runs.length === 1) await expect(section).toContainText('One completed model so far.');
  else await expect(section.getByText('One completed model so far.', { exact: false })).toHaveCount(0);
  await expect(table).toHaveAccessibleName('Complete 115-picture test set · Saved AI results');
  await expect(table.getByRole('row')).toHaveCount(bundle.runs.length + 1);
  await expect(row.getByRole('button', { name: 'gemini-3.5-flash-lite', exact: true })).toHaveAttribute('aria-pressed', 'true');
  const cells = row.getByRole('cell');
  await expect(cells.nth(0)).toHaveText('12 / 93');
  await expect(cells.nth(1)).toHaveText('5 / 22');
  await expect(cells.nth(2)).toHaveText('115 / 115');
  await expect(cells.nth(3)).toHaveText('0 / 115');
  await expect(cells.nth(4)).toHaveText('0 / 115');
  const times = bundle.runs[0].evidence.predictions.flatMap(p => p.attempts).map(a => a.latency_ms!).sort((a, b) => a - b);
  const median = (times[57] + times[58]) / 2;
  await expect(cells.nth(5)).toContainText(`${(median / 1000).toFixed(2)} s`);
  await expect(cells.nth(5)).toContainText('116 / 116 attempts timed');
  await expect(cells.nth(6)).toHaveText('86 / 115');
  // Check every genuine row, including coverage, uncertainty and retry timing.
  for (const [index, saved] of bundle.runs.entries()) {
    const values = table.getByRole('row').nth(index + 1).getByRole('cell');
    const m = saved.report.successful_output;
    await expect(values.nth(0)).toHaveText(`${m.fn} / ${m.anomalous}`);
    await expect(values.nth(1)).toHaveText(`${m.fp} / ${m.normal}`);
    await expect(values.nth(2)).toHaveText(`${saved.report.succeeded} / 115`);
    await expect(values.nth(3)).toHaveText(`${saved.report.failed} / 115`);
    const unsure = saved.evidence.predictions.filter(p => p.status === 'success' && p.attempts.at(-1)!.response?.decision === 'uncertain').length;
    await expect(values.nth(4)).toHaveText(`${unsure} / ${saved.report.succeeded}`);
    const attempts = saved.evidence.predictions.flatMap(p => p.attempts);
    const measured = attempts.flatMap(a => a.latency_ms === null ? [] : [a.latency_ms]).sort((a, b) => a - b);
    const mid = Math.floor(measured.length / 2);
    const requestMedian = measured.length % 2 ? measured[mid] : (measured[mid - 1] + measured[mid]) / 2;
    await expect(values.nth(5)).toContainText(`${(requestMedian / 1000).toFixed(2)} s`);
    await expect(values.nth(5)).toContainText(`${measured.length} / ${attempts.length} attempts timed`);
    await expect(values.nth(6)).toHaveText(`${saved.report.full_set_routing.review_count} / 115`);
  }
  await expect(section.getByText('gemini-3.8-flash', { exact: true })).toHaveCount(0);
  await section.getByText('How to read the table', { exact: true }).click();
  await expect(section.getByText('No answer is a technical failure', { exact: false })).toBeVisible();
  await mkdir(artifacts, { recursive: true });
  const scans = [];
  for (const width of [360, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const violations = (await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations;
    expect(violations).toEqual([]);
    const scroll = section.getByRole('region', { name: 'Model comparison table', exact: false });
    await scroll.focus();
    await expect(scroll).toBeFocused();
    if (width === 360) {
      await page.keyboard.press('ArrowRight');
      await expect.poll(() => scroll.evaluate(el => el.scrollLeft)).toBeGreaterThan(0);
      await scroll.evaluate(el => { el.scrollLeft = 0; });
    }
    if (width === 1440) expect(await scroll.evaluate(el => el.scrollWidth <= el.clientWidth)).toBe(true);
    await section.screenshot({ path: resolve(artifacts, `comparison-${width}.png`) });
    scans.push({ width, violations: violations.length, page_overflow: false });
  }
  expect(errors).toEqual([]); expect(external).toEqual([]);
  await writeFile(resolve(artifacts, 'verification.json'), JSON.stringify({ bundle_id: bundle.bundle_id, browser: browser.version(),
    genuine_models: bundle.runs.length, models: bundle.runs.map(r => ({ model: r.report.model_id, report: r.report })), images: 115, median_attempt_ms: median, attempts: times.length, scans,
    external_requests: external, page_errors: errors, visual_subject: 'Table only; no source photographs',
    note: 'All genuine complete rows checked against saved reports; baseline values also independently fixed above. Labelled fixtures retain failure edge cases.' }, null, 2));
});
