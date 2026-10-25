import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json' with { type: 'json' };
import type { Bundle } from '../src/types';

const artifacts = resolve('../artifacts/model-comparison');

test('genuine complete-set comparison row shows real counts and measured request time', async ({ page, browser }) => {
  const external: string[] = [], errors: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (!r.url().startsWith('http://127.0.0.1:4175') && !r.url().startsWith('blob:')) external.push(r.url()); });
  await page.goto('/');
  await page.getByRole('button', { name: 'See the results' }).click();
  const section = page.getByRole('region', { name: 'Compare models', exact: true });
  const table = section.getByRole('table');
  const row = table.getByRole('row').nth(1);
  await expect(section).toContainText('One completed model so far.');
  await expect(table).toHaveAccessibleName('Complete 115-picture test set · Saved AI results');
  await expect(table.getByRole('row')).toHaveCount(2);
  await expect(row.getByRole('button', { name: 'gemini-3.5-flash-lite', exact: true })).toHaveAttribute('aria-pressed', 'true');
  const cells = row.getByRole('cell');
  await expect(cells.nth(0)).toHaveText('12 / 93');
  await expect(cells.nth(1)).toHaveText('5 / 22');
  await expect(cells.nth(2)).toHaveText('115 / 115');
  await expect(cells.nth(3)).toHaveText('0 / 115');
  await expect(cells.nth(4)).toHaveText('0 / 115');
  const bundle = await page.request.get('/evidence/bundle.json').then(r => r.json()) as Bundle;
  const times = bundle.runs[0].evidence.predictions.flatMap(p => p.attempts).map(a => a.latency_ms!).sort((a, b) => a - b);
  const median = (times[57] + times[58]) / 2;
  await expect(cells.nth(5)).toContainText(`${(median / 1000).toFixed(2)} s`);
  await expect(cells.nth(5)).toContainText('116 / 116 attempts timed');
  await expect(cells.nth(6)).toHaveText('86 / 115');
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
    genuine_models: 1, images: 115, median_attempt_ms: median, attempts: times.length, scans,
    external_requests: external, page_errors: errors, visual_subject: 'Table only; no source photographs',
    note: 'One authentic evaluated model; multi-model selection is verified separately with labelled fixtures.' }, null, 2));
});

test('two labelled fixture models can be selected without changing visitor judgments; failures stay visible', async ({ page }) => {
  const data = structuredClone(fixture);
  const second = structuredClone(data.runs[0]);
  second.evidence.run.run_id = 'fixture-comparison-second';
  second.evidence.run.model_id = 'fixture-comparison-model';
  second.report.run_id = second.evidence.run.run_id;
  second.report.model_id = second.evidence.run.model_id;
  second.evidence.predictions.forEach(p => {
    p.run_id = second.evidence.run.run_id;
    p.attempts.forEach(a => { a.latency_ms = null; });
  });
  data.runs.push(second);
  await page.route('**/evidence/**', async route => {
    const path = new URL(route.request().url()).pathname;
    if (path === '/evidence/bundle.json') return route.fulfill({ json: data });
    if (/^\/evidence\/(images|masks)\/img-\d{6}\.png$/.test(path)) return route.fulfill({ contentType: 'image/png', body: await readFile(resolve('../tests/fixtures/fastener-assets', path.slice('/evidence/'.length))) });
    return route.fulfill({ status: 404 });
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Try it', exact: false }).click();
  await page.getByRole('button', { name: 'Looks fine', exact: true }).click();
  await page.getByRole('button', { name: 'Reveal AI assessment' }).click();
  const before = await page.evaluate(() => JSON.parse(localStorage.getItem('ai-inspection-pilot-lab:visitor:v1')!));
  await page.getByRole('button', { name: 'Results', exact: true }).click();
  const section = page.getByRole('region', { name: 'Compare models', exact: true });
  await expect(section.getByRole('row')).toHaveCount(3);
  await expect(section.getByText('One completed model so far.', { exact: false })).toHaveCount(0);
  const model = section.getByRole('button', { name: 'fixture-comparison-model', exact: true });
  await model.focus(); await page.keyboard.press('Enter');
  await expect(model).toHaveAttribute('aria-pressed', 'true');
  const cells = section.getByRole('row').nth(2).getByRole('cell');
  await expect(cells.nth(0)).toHaveText('1 / 2');
  await expect(cells.nth(1)).toHaveText('1 / 1');
  await expect(cells.nth(2)).toHaveText('3 / 6');
  await expect(cells.nth(3)).toHaveText('3 / 6');
  await expect(cells.nth(4)).toHaveText('1 / 3');
  await expect(cells.nth(5)).toContainText('Unavailable');
  await expect(cells.nth(5)).toContainText('0 / 6 attempts timed');
  await expect(cells.nth(6)).toHaveText('5 / 6');
  await expect(page.getByText('TEST EXAMPLES ONLY', { exact: false })).toBeVisible();
  const after = await page.evaluate(() => JSON.parse(localStorage.getItem('ai-inspection-pilot-lab:visitor:v1')!));
  expect(after.answers).toEqual(before.answers); expect(after.revealed).toEqual(before.revealed);
  expect(after.selectedImage).toBe(before.selectedImage);
  // The player follows the selected model, keeps image identity, and never mixes counters.
  await page.getByRole('button', { name: 'Try it', exact: true }).click();
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  const watch = page.getByRole('region', { name: 'Watch AI Inspect', exact: true });
  const status = watch.getByRole('status').filter({ hasText: 'Picture' });
  await expect(watch.getByLabel('Saved model', { exact: true })).toHaveValue(second.evidence.run.run_id);
  await watch.getByRole('button', { name: 'Next', exact: true }).click();
  await expect(status).toContainText('Picture 2 of 5 · Paused · Look at the picture');
  await page.clock.install({ time: new Date('2026-10-25T12:00:00Z') });
  await page.clock.pauseAt(new Date('2026-10-25T13:00:00Z'));
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(1000);
  await expect(status).toContainText('AI assessment');
  await page.clock.runFor(1000);
  await expect(status).toContainText('Dataset reference');
  const playbackResults = watch.getByRole('region', { name: 'Results for this five-picture playback', exact: true });
  await expect(playbackResults).toContainText('1 of 5 references shown');
  await expect(playbackResults.getByRole('region', { name: 'Defects missed', exact: true }).locator('strong')).toHaveText('1');
  await watch.getByLabel('Saved model', { exact: true }).selectOption(data.runs[0].evidence.run.run_id);
  await expect(status).toContainText('Picture 2 of 5 · Paused · Look at the picture');
  await expect(playbackResults).toContainText('0 of 5 references shown');
  await expect(playbackResults.getByRole('region', { name: 'Defects missed', exact: true }).locator('strong')).toHaveText('0');
  await page.clock.runFor(5000);
  await expect(status).toContainText('Paused · Look at the picture');
  const final = await page.evaluate(() => JSON.parse(localStorage.getItem('ai-inspection-pilot-lab:visitor:v1')!));
  expect(final.answers).toEqual(before.answers); expect(final.revealed).toEqual(before.revealed);
  expect(final.selectedImage).toBe(before.selectedImage);
  await page.setViewportSize({ width: 360, height: 1000 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.clock.resume(); // Playback is paused; allow axe's own scheduling.
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
  const playerArtifacts = resolve('../artifacts/model-comparison-oct25');
  await mkdir(playerArtifacts, { recursive: true });
  await watch.getByRole('group', { name: 'Playback controls', exact: true }).screenshot({ path: resolve(playerArtifacts, 'player-controls-fixture-360.png') });
});
