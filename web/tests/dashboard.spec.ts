import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import type { Bundle } from '../src/types';
import { bundle, catalog, finish, fixturePlayback, metric, modelNames, openWatch, status, storage, tick, totals } from './playback-helpers';

const artifacts = resolve('../artifacts/sequential-playback');
const allIds = catalog.images.map(i => i.image_id);
// Independent categorization; no imports from the application's comparison helpers.
const differingIds = allIds.filter(id => new Set(bundle.runs.map(r => {
  const p = r.evidence.predictions.find(p => p.image_id === id)!;
  return p.status === 'success' ? p.attempts.at(-1)!.response!.decision : 'unavailable';
})).size > 1);

test('all 115 pictures reveal both genuine models, count every reference, stop and preserve visitor judgments', async ({ page, browser }) => {
  test.setTimeout(180000);
  const errors: string[] = [], external: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (!r.url().startsWith('http://127.0.0.1:4175') && !r.url().startsWith('blob:')) external.push(r.url()); });
  const watch = await openWatch(page, true);
  const before = await page.evaluate(key => localStorage.getItem(key), storage);
  const dashboard = await finish(page, watch, allIds);
  await expect(status(watch)).toHaveText('Picture 115 of 115 · Finished');
  await expect(dashboard).toContainText('115 of 115 pictures viewed. Scores below cover all 115 pictures.');
  const expected = [
    { correct: 98, missed: 12, unsure: 0, median: '4.96 s' },
    { correct: 89, missed: 20, unsure: 1, median: '6.06 s' },
  ];
  for (const [index, saved] of bundle.runs.entries()) {
    const card = dashboard.getByRole('article', { name: `${saved.report.model_id} full benchmark`, exact: true }), values = expected[index];
    await expect(card.locator('.benchmark-score strong')).toHaveText(`${(values.correct / 115 * 100).toFixed(1)}%`);
    await expect(card.locator('.benchmark-bar').nth(0)).toContainText(`${values.correct} / 115`);
    await expect(card.locator('.benchmark-bar').nth(1)).toContainText(`${values.missed} / 93`);
    await expect(card.locator('.benchmark-bar').nth(2)).toContainText('5 / 22');
    await expect(card.locator('dd').nth(0)).toHaveText(`${values.unsure} / 115`);
    await expect(card.locator('dd').nth(1)).toHaveText('0 / 115');
    await expect(card.locator('dd').nth(2)).toHaveText(values.median);
  }
  await page.clock.runFor(20000); await expect(dashboard).toBeVisible();
  // Keyboard reaches the three end actions without passing through explanatory text.
  await page.keyboard.press('Tab'); await expect(dashboard.getByRole('button', { name: 'Review pictures', exact: true })).toBeFocused();
  await page.keyboard.press('Tab'); await expect(dashboard.getByRole('button', { name: 'Review different answers', exact: true })).toBeFocused();
  await page.keyboard.press('Tab'); await expect(dashboard.getByRole('button', { name: 'Watch again', exact: true })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(watch).toBeFocused();
  await expect(status(watch)).toContainText('Picture 1 of 115 · Paused · Picture');
  for (let n = 0; n < 2; n++) {
    await expect(totals(watch, n)).toContainText('0 correct');
    for (const key of ['Defects flagged', 'Defects missed', 'Good parts flagged']) await expect(metric(totals(watch, n), key)).toHaveText('0');
  }
  expect(await page.evaluate(key => localStorage.getItem(key), storage)).toBe(before);
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('button', { name: 'Try it', exact: true }).click();
  await expect(page.getByRole('region', { name: 'Your answer', exact: true })).toContainText('Looks fine');
  await page.reload(); await expect(page.getByRole('region', { name: 'Your answer', exact: true })).toContainText('Looks fine');
  expect(errors).toEqual([]); expect(external).toEqual([]);
  await mkdir(artifacts, { recursive: true });
  await writeFile(resolve(artifacts, 'full-run.json'), JSON.stringify({ bundle_id: bundle.bundle_id, browser: browser.version(), pictures: 115,
    staged_saved_decisions_checked: 230, references_counted: 115, expected, unique_counts: true, stopped: true,
    replay_paused_cleared: true, judgments_preserved: true, errors, external }, null, 2));
});

test('26 different answers play in full with unchanged scores, paused filter changes and review actions', async ({ page }) => {
  test.setTimeout(120000);
  const watch = await openWatch(page, true), before = await page.evaluate(key => localStorage.getItem(key), storage);
  expect(differingIds).toHaveLength(26);
  await watch.getByRole('button', { name: 'Play', exact: true }).click(); await page.clock.runFor(300);
  await watch.getByRole('button', { name: 'Different answers only (26)', exact: true }).click();
  await expect(status(watch)).toContainText('Picture 1 of 26 · Paused · Picture');
  await page.clock.runFor(10000); await expect(status(watch)).toContainText('Paused · Picture');
  const dashboard = await finish(page, watch, differingIds);
  await expect(dashboard).toContainText('26 of 26 pictures viewed · Filtered playback. Scores below cover all 115 pictures.');
  for (const [index, value] of ['98 / 115', '89 / 115'].entries()) await expect(dashboard.locator('.benchmark-card').nth(index).locator('.benchmark-bar').first()).toContainText(value);
  const scores = await dashboard.locator('.benchmark-cards').innerText();
  await dashboard.getByRole('button', { name: 'Review different answers', exact: true }).click();
  await expect(watch).toBeFocused(); await expect(status(watch)).toContainText('Picture 1 of 26 · Paused');
  await expect(watch.getByRole('region', { name: 'This playback', exact: false })).toContainText('0 / 26 references viewed');
  // Skipping ahead remains honest about the number of references actually viewed.
  await watch.focus(); await page.keyboard.press('End');
  await expect(status(watch)).toContainText('Picture 26 of 26 · Paused · Picture');
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  for (const stage of [...modelNames, 'Dataset reference']) await tick(page, watch, stage);
  await page.clock.runFor(1000);
  await expect(dashboard).toContainText('1 of 26 pictures viewed · Filtered playback');
  expect(await dashboard.locator('.benchmark-cards').innerText()).toBe(scores);
  await dashboard.getByRole('button', { name: 'Watch again', exact: true }).click();
  await expect(status(watch)).toContainText('Picture 1 of 26 · Paused · Picture');
  await watch.focus(); await page.keyboard.press('End');
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  for (const stage of [...modelNames, 'Dataset reference']) await tick(page, watch, stage);
  await page.clock.runFor(1000);
  await dashboard.getByRole('button', { name: 'Review pictures', exact: true }).click();
  await expect(watch).toBeFocused(); await expect(status(watch)).toContainText('Picture 1 of 115 · Paused · Picture');
  await watch.getByRole('button', { name: 'Different answers only (26)', exact: true }).click();
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await watch.getByRole('button', { name: 'Show all pictures', exact: true }).click();
  await expect(status(watch)).toContainText('Picture 1 of 115 · Paused · Picture');
  expect(await page.evaluate(key => localStorage.getItem(key), storage)).toBe(before);
  await mkdir(artifacts, { recursive: true });
  await writeFile(resolve(artifacts, 'filtered-run.json'), JSON.stringify({ pictures: 26, benchmark: 115, ids: differingIds,
    full_scores_unchanged: true, paused_filters: true, review_and_replay: true, skipped_references_honest: true, judgments_preserved: true }, null, 2));
});

for (const width of [360, 768, 1440]) test(`dashboard layout and keyboard at ${width}px`, async ({ page }) => {
  test.setTimeout(60000);
  await page.setViewportSize({ width, height: 1000 });
  const watch = await openWatch(page);
  await watch.focus(); await page.keyboard.press('End');
  await expect(status(watch)).toContainText('Picture 115 of 115 · Paused · Picture');
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  for (const stage of [...modelNames, 'Dataset reference']) await tick(page, watch, stage);
  await page.clock.runFor(1000);
  const dashboard = watch.getByRole('region', { name: 'The complete comparison', exact: true });
  await expect(dashboard).toContainText('1 of 115 pictures viewed');
  const boxes = await dashboard.locator('.benchmark-card').evaluateAll(cards => cards.map(card => { const b = card.getBoundingClientRect(); return { x: b.x, y: b.y, width: b.width, height: b.height }; }));
  expect(Math.abs(boxes[0].width - boxes[1].width)).toBeLessThan(1);
  expect(Math.abs(boxes[0].height - boxes[1].height)).toBeLessThan(1);
  if (width === 360) expect(boxes[1].y).toBeGreaterThanOrEqual(boxes[0].y + boxes[0].height);
  else expect(Math.abs(boxes[0].y - boxes[1].y)).toBeLessThan(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await expect(dashboard.getByRole('heading', { name: 'The complete comparison', exact: true })).toBeFocused();
  for (const name of ['Review pictures', 'Review different answers', 'Watch again']) {
    await page.keyboard.press('Tab'); await expect(dashboard.getByRole('button', { name, exact: true })).toBeFocused();
  }
  expect(await dashboard.getByRole('button', { name: 'Watch again', exact: true }).evaluate(el => getComputedStyle(el).outlineStyle)).toBe('solid');
  await page.clock.resume();
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
  await mkdir(artifacts, { recursive: true });
  await dashboard.screenshot({ path: resolve(artifacts, `dashboard-${width}.png`) });
  await writeFile(resolve(artifacts, `dashboard-layout-${width}.json`), JSON.stringify({ width, boxes, violations: [], overflow: false, keyboard: true }, null, 2));
  await page.keyboard.press('Enter'); await expect(status(watch)).toContainText('Picture 1 of 115 · Paused');
});

test('single-model fixture plays all six records and keeps unsure, unavailable and missing time separate', async ({ page }) => {
  const data = await fixturePlayback(page), watch = await openWatch(page);
  const ids = data.runs[0].report.images.map(i => i.image_id).sort();
  const dashboard = await finish(page, watch, ids, 1, data as unknown as Bundle);
  const card = dashboard.getByRole('article');
  await expect(card.locator('.benchmark-score strong')).toHaveText('0.0%');
  await expect(card.locator('.benchmark-bar').nth(0)).toContainText('0 / 6');
  await expect(card.locator('.benchmark-bar').nth(1)).toContainText('1 / 3');
  await expect(card.locator('.benchmark-bar').nth(2)).toContainText('1 / 3');
  await expect(card.locator('dd').nth(0)).toHaveText('1 / 6');
  await expect(card.locator('dd').nth(1)).toHaveText('3 / 6');
  await expect(card.locator('dd').nth(2)).toHaveText('Unavailable');
  await expect(dashboard.getByRole('button', { name: 'Review different answers', exact: true })).toBeDisabled();
  await expect(watch.getByRole('button', { name: 'Different answers only (0)', exact: true })).toBeDisabled();
  await expect(dashboard).toContainText('Test examples only');
});
