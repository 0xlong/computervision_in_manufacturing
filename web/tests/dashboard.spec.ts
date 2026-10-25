import { test, expect } from '@playwright/test';
import type { Locator, Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json' with { type: 'json' };
import type { Bundle } from '../src/types';

const artifacts = resolve('../artifacts/comparison-dashboard');
const storage = 'ai-inspection-pilot-lab:visitor:v1';

async function start(page: Page, withJudgment = false) {
  await page.goto('/');
  if (withJudgment) {
    await page.getByRole('button', { name: 'Try it', exact: false }).click();
    await page.getByRole('button', { name: 'Looks fine', exact: true }).click();
    await page.getByRole('button', { name: 'Reveal AI assessment' }).click();
  }
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  const watch = page.getByRole('region', { name: 'Watch AI Inspect', exact: true });
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Look at the picture');
  await page.clock.install({ time: new Date('2026-10-25T12:00:00Z') });
  await page.clock.pauseAt(new Date('2026-10-25T13:00:00Z'));
  return watch;
}

async function finish(page: Page, watch: Locator, total: number) {
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  for (let index = 0; index < total; index++) {
    await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText(`Picture ${index + 1} of ${total} · Playing · Look at the picture`);
    await page.clock.runFor(1000);
    await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('AI assessment');
    await page.clock.runFor(1000);
    await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Dataset reference');
    await expect(watch.getByRole('region', { name: 'The complete comparison', exact: true })).toHaveCount(0);
    await page.clock.runFor(1000);
  }
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText(`Picture ${total} of ${total} · Finished`);
  const dashboard = watch.getByRole('region', { name: 'The complete comparison', exact: true });
  await expect(dashboard).toBeVisible();
  await expect(dashboard.getByRole('heading', { name: 'The complete comparison', exact: true })).toBeFocused();
  await expect(watch.getByRole('button', { name: 'Play', exact: true })).toBeDisabled();
  return dashboard;
}

// Independent recount deliberately does not import the app's comparison helpers.
function recount(saved: Bundle['runs'][number]) {
  let correct = 0, missed = 0, falseAlarms = 0, unsure = 0, unavailable = 0;
  for (const image of saved.report.images) {
    const p = saved.evidence.predictions.find(p => p.image_id === image.image_id)!;
    const decision = p.status === 'success' ? p.attempts.at(-1)!.response?.decision : null;
    if (decision === null) unavailable++;
    else if (decision === 'uncertain') unsure++;
    else if (decision === (image.label === 'anomalous' ? 'needs_review' : 'looks_acceptable')) correct++;
    else if (image.label === 'anomalous') missed++;
    else falseAlarms++;
  }
  const times = saved.evidence.predictions.flatMap(p => p.attempts).flatMap(a => a.latency_ms === null ? [] : [a.latency_ms]).sort((a, b) => a - b);
  const mid = Math.floor(times.length / 2);
  return { correct, missed, falseAlarms, unsure, unavailable,
    defective: saved.report.images.filter(i => i.label === 'anomalous').length,
    good: saved.report.images.filter(i => i.label === 'normal').length,
    median: times.length ? (times.length % 2 ? times[mid] : (times[mid - 1] + times[mid]) / 2) : null };
}

test('complete and filtered endings retain full evidence scores, count both models once and preserve judgments', async ({ page, browser }) => {
  test.setTimeout(90000);
  const errors: string[] = [], external: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (!r.url().startsWith('http://127.0.0.1:4175') && !r.url().startsWith('blob:')) external.push(r.url()); });
  const watch = await start(page, true);
  const before = await page.evaluate(key => localStorage.getItem(key), storage);
  const bundle = await page.request.get('/evidence/bundle.json').then(r => r.json()) as Bundle;
  expect(bundle.execution).toBe('recorded_live');
  const dashboard = await finish(page, watch, 5);
  await expect(dashboard).toContainText('You viewed 5 of 5 selected playback pictures. The benchmark below covers all 115 pictures.');
  const summaries = [];
  for (const saved of bundle.runs) {
    const c = recount(saved);
    const card = dashboard.getByRole('article', { name: `${saved.report.model_id} full benchmark`, exact: true });
    await expect(card.locator('.benchmark-score strong')).toHaveText(`${(c.correct / 115 * 100).toFixed(1)}%`);
    const bars = card.locator('.benchmark-bar');
    for (const [index, count, total] of [[0, c.correct, 115], [1, c.missed, c.defective], [2, c.falseAlarms, c.good]]) {
      await expect(bars.nth(index).locator('strong')).toContainText(`${count} / ${total}`);
      const width = await bars.nth(index).locator('.bar-track > div').evaluate(el => parseFloat(el.style.width));
      expect(Math.abs(width - count / total * 100)).toBeLessThan(0.001);
    }
    const details = card.locator('dd');
    await expect(details.nth(0)).toHaveText(`${c.unsure} / 115`);
    await expect(details.nth(1)).toHaveText(`${c.unavailable} / 115`);
    await expect(details.nth(2)).toHaveText(`${(c.median! / 1000).toFixed(2)} s`);
    summaries.push({ model: saved.report.model_id, ...c });
  }
  expect(summaries.map(s => s.correct)).toEqual([98, 89]);
  const cardsBefore = await dashboard.locator('.benchmark-cards').innerText();
  await page.clock.runFor(30000);
  await expect(dashboard).toBeVisible();
  // The dashboard focus lands before its three native buttons; all work by keyboard.
  await page.keyboard.press('Tab');
  await expect(dashboard.getByRole('button', { name: 'Review pictures', exact: true })).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(dashboard.getByRole('button', { name: 'Review different answers', exact: true })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(watch).toBeFocused();
  await expect(watch.getByRole('button', { name: 'Different answers only', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Picture 1 of 2 · Paused · Look at the picture');
  await expect(watch.getByRole('group', { name: 'Picture filter' })).toContainText('2 of 5 selected pictures');
  // A mid-play filter change pauses immediately and exposes the all-pictures escape.
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(400);
  await watch.getByRole('button', { name: 'Show all pictures', exact: true }).click();
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Picture 1 of 5 · Paused');
  await page.clock.runFor(9000);
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Paused · Look at the picture');
  await watch.getByRole('button', { name: 'Different answers only', exact: true }).click();
  await finish(page, watch, 2);
  await expect(dashboard).toContainText('You viewed 2 of 2 matching pictures in filtered playback. The benchmark below covers all 115 pictures.');
  expect(await dashboard.locator('.benchmark-cards').innerText()).toBe(cardsBefore);
  for (const [index, saved] of bundle.runs.entries()) {
    const totals = watch.getByRole('region', { name: `${saved.report.model_id} playback totals`, exact: true });
    await expect(totals).toContainText('2 of 2 references shown · 0 unsure · 0 unavailable');
    await expect(totals.getByRole('region', { name: 'Good parts flagged', exact: true }).locator('strong')).toHaveText(index === 0 ? '2' : '0');
  }
  // Review a counted picture without adding it a second time.
  await watch.getByRole('button', { name: 'Previous', exact: true }).click();
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(1000);
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('AI assessment');
  await page.clock.runFor(1000);
  for (const saved of bundle.runs) await expect(watch.getByRole('region', { name: `${saved.report.model_id} playback totals`, exact: true })).toContainText('2 of 2 references shown');
  await page.clock.runFor(1000);
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Look at the picture');
  await page.clock.runFor(1000);
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('AI assessment');
  await page.clock.runFor(1000);
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Dataset reference');
  await page.clock.runFor(1000);
  await expect(dashboard).toBeVisible();
  await dashboard.getByRole('button', { name: 'Watch again', exact: true }).click();
  await expect(watch).toBeFocused();
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Picture 1 of 2 · Paused · Look at the picture');
  for (const saved of bundle.runs) {
    const totals = watch.getByRole('region', { name: `${saved.report.model_id} playback totals`, exact: true });
    await expect(totals).toContainText('0 of 2 references shown');
    for (const metric of ['Defects flagged', 'Defects missed', 'Good parts flagged']) await expect(totals.getByRole('region', { name: metric, exact: true }).locator('strong')).toHaveText('0');
  }
  await finish(page, watch, 2);
  await dashboard.getByRole('button', { name: 'Review pictures', exact: true }).click();
  await expect(watch).toBeFocused();
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Picture 1 of 5 · Paused · Look at the picture');
  expect(await page.evaluate(key => localStorage.getItem(key), storage)).toBe(before);
  await page.getByRole('button', { name: 'Try it yourself', exact: true }).click();
  await expect(page.getByRole('region', { name: 'Your answer', exact: true })).toContainText('Looks fine');
  expect(errors).toEqual([]); expect(external).toEqual([]);
  await mkdir(artifacts, { recursive: true });
  await writeFile(resolve(artifacts, 'evidence-and-endings.json'), JSON.stringify({ bundle_id: bundle.bundle_id, browser: browser.version(), summaries,
    full_end: true, filtered_end: true, filtered_pictures: 2, full_denominator: 115, scores_unchanged: true,
    repeat_reveal_counted_once: true, replay_paused_cleared: true, visitor_storage_preserved: true, errors, external }, null, 2));
});

for (const width of [360, 768, 1440]) test(`final comparison keyboard and equal cards at ${width}px`, async ({ page }) => {
  test.setTimeout(60000);
  await page.setViewportSize({ width, height: 1000 });
  const watch = await start(page);
  const dashboard = await finish(page, watch, 5);
  const boxes = await dashboard.locator('.benchmark-card').evaluateAll(cards => cards.map(card => {
    const b = card.getBoundingClientRect(); return { x: b.x, y: b.y, width: b.width, height: b.height };
  }));
  expect(boxes).toHaveLength(2);
  expect(Math.abs(boxes[0].width - boxes[1].width)).toBeLessThan(1);
  expect(Math.abs(boxes[0].height - boxes[1].height)).toBeLessThan(1);
  if (width === 360) expect(boxes[1].y).toBeGreaterThanOrEqual(boxes[0].y + boxes[0].height);
  else expect(Math.abs(boxes[0].y - boxes[1].y)).toBeLessThan(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.keyboard.press('Tab');
  await expect(dashboard.getByRole('button', { name: 'Review pictures', exact: true })).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(dashboard.getByRole('button', { name: 'Review different answers', exact: true })).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(dashboard.getByRole('button', { name: 'Watch again', exact: true })).toBeFocused();
  expect(await dashboard.getByRole('button', { name: 'Watch again', exact: true }).evaluate(el => getComputedStyle(el).outlineStyle)).toBe('solid');
  await page.clock.resume();
  const violations = (await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations;
  expect(violations).toEqual([]);
  await mkdir(artifacts, { recursive: true });
  // Dashboard-only crops contain no source photographs.
  await dashboard.screenshot({ path: resolve(artifacts, `dashboard-${width}.png`) });
  await writeFile(resolve(artifacts, `layout-${width}.json`), JSON.stringify({ width, boxes, violations, overflow: false, keyboard_focus: true }, null, 2));
  await page.keyboard.press('Enter');
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Picture 1 of 5 · Paused');
});

async function useFixture(page: Page, twoModels: boolean) {
  const data = structuredClone(fixture);
  if (twoModels) {
    const second = structuredClone(data.runs[0]);
    second.evidence.run.run_id = 'fixture-identical-answers';
    second.evidence.run.model_id = 'fixture-second-model';
    second.report.run_id = second.evidence.run.run_id;
    second.report.model_id = second.evidence.run.model_id;
    second.evidence.predictions.forEach(p => { p.run_id = second.evidence.run.run_id; });
    data.runs.push(second);
  }
  data.runs.forEach(r => r.evidence.predictions.forEach(p => p.attempts.forEach(a => { a.latency_ms = null; })));
  await page.route('**/evidence/**', async route => {
    const path = new URL(route.request().url()).pathname;
    if (path === '/evidence/bundle.json') return route.fulfill({ json: data });
    if (/^\/evidence\/(images|masks)\/img-\d{6}\.png$/.test(path)) return route.fulfill({ contentType: 'image/png', body: await readFile(resolve('../tests/fixtures/fastener-assets', path.slice('/evidence/'.length))) });
    return route.fulfill({ status: 404 });
  });
}

test('fixture ending excludes unsure and unavailable from correct decisions and uses full class denominators', async ({ page }) => {
  await useFixture(page, false);
  const watch = await start(page);
  const dashboard = await finish(page, watch, 5);
  const card = dashboard.getByRole('article');
  await expect(card.locator('.benchmark-score strong')).toHaveText('0.0%');
  await expect(card.locator('.benchmark-bar').nth(0)).toContainText('0 / 6');
  await expect(card.locator('.benchmark-bar').nth(1)).toContainText('1 / 3');
  await expect(card.locator('.benchmark-bar').nth(2)).toContainText('1 / 3');
  await expect(card.locator('dd').nth(0)).toHaveText('1 / 6');
  await expect(card.locator('dd').nth(1)).toHaveText('3 / 6');
  await expect(card.locator('dd').nth(2)).toHaveText('Unavailable');
  await expect(dashboard.getByRole('button', { name: 'Review different answers', exact: true })).toBeDisabled();
  await expect(watch.getByRole('button', { name: 'Different answers only', exact: true })).toBeDisabled();
  await expect(dashboard).toContainText('Test examples only');
});

test('zero disagreements has a paused empty state and show-all recovery', async ({ page }) => {
  await useFixture(page, true);
  const watch = await start(page);
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await watch.getByRole('button', { name: 'Different answers only', exact: true }).click();
  await expect(watch.getByRole('status')).toHaveText('No matching pictures · Paused');
  await expect(watch.getByRole('button', { name: 'Play', exact: true })).toBeDisabled();
  await expect(watch.getByRole('button', { name: 'Next', exact: true })).toBeDisabled();
  await watch.focus(); await page.keyboard.press('Space');
  await page.clock.runFor(20000);
  await expect(watch.getByRole('status')).toHaveText('No matching pictures · Paused');
  await expect(watch.getByRole('region', { name: 'The complete comparison', exact: true })).toHaveCount(0);
  await watch.getByRole('button', { name: 'Show all pictures', exact: true }).click();
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Picture 1 of 5 · Paused · Look at the picture');
});
