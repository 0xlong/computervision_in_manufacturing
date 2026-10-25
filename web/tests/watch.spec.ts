import { test, expect } from '@playwright/test';
import type { Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json' with { type: 'json' };
import type { Bundle } from '../src/types';

const artifacts = resolve('..', 'artifacts/watch-ai');

async function freezeClock(page: Page) {
  await page.clock.install({ time: new Date('2026-10-24T12:00:00Z') });
  await page.clock.pauseAt(new Date('2026-10-24T13:00:00Z'));
}

async function openWatch(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  const watch = page.getByRole('region', { name: 'Watch AI Inspect', exact: true });
  await expect(watch.getByRole('status').filter({ hasText: 'Picture 1' })).toContainText('Look at the picture');
  await freezeClock(page);
  return watch;
}

test('saved playback starts paused, reveals in stages and keeps visitor answers separate', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  const watch = page.getByRole('region', { name: 'Watch AI Inspect', exact: true });
  await expect(watch.getByRole('img', { name: 'Metal nut for your visual inspection' })).toBeVisible();
  await expect(watch.getByRole('status').filter({ hasText: 'Picture 1' })).toContainText('Paused');
  await expect(watch.getByRole('region', { name: 'AI assessment', exact: true })).toContainText('Waiting');
  await expect(page.getByText('Your answer', { exact: true })).toHaveCount(0);
  await freezeClock(page);
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(1000);
  await expect(watch.getByRole('region', { name: 'AI assessment', exact: true })).toContainText('Needs checking');
  await expect(watch.getByRole('region', { name: 'Dataset reference', exact: true })).toContainText('Waiting');
  await watch.getByRole('button', { name: 'Pause', exact: true }).click();
  await page.clock.runFor(5000);
  await expect(watch.getByRole('region', { name: 'Dataset reference', exact: true })).toContainText('Waiting');
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(1000);
  await expect(watch.getByRole('region', { name: 'Dataset reference', exact: true })).toContainText('Looks fine');
  await page.getByRole('button', { name: 'Try it yourself', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Reveal AI assessment' })).toBeDisabled();
  await expect(page.getByRole('group', { name: 'Answer comparison', exact: true })).toHaveCount(0);
});

test('remaining viewing time survives pause and speed changes; navigation and restart pause', async ({ page }) => {
  const watch = await openWatch(page);
  const status = watch.getByRole('status').filter({ hasText: 'Picture' });
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(400);
  await watch.getByRole('button', { name: 'Pause', exact: true }).click();
  await page.clock.runFor(5000);
  await expect(status).toContainText('Look at the picture');
  await watch.getByLabel('Viewing time per picture', { exact: true }).selectOption('6');
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(1199);
  await expect(status).toContainText('Look at the picture');
  await page.clock.runFor(1);
  await expect(status).toContainText('AI assessment');
  await page.clock.runFor(500);
  await watch.getByLabel('Viewing time per picture', { exact: true }).selectOption('3');
  await page.clock.runFor(749);
  await expect(watch.getByRole('region', { name: 'Dataset reference', exact: true })).toContainText('Waiting');
  await page.clock.runFor(1);
  await expect(status).toContainText('Dataset reference');
  await watch.getByRole('button', { name: 'Next', exact: true }).click();
  await expect(status).toContainText('Picture 2 of 5 · Paused');
  await expect(status).toContainText('Look at the picture');
  await watch.getByRole('button', { name: 'Previous', exact: true }).click();
  await expect(status).toContainText('Picture 1 of 5 · Paused');
  await watch.getByRole('button', { name: 'Restart', exact: true }).click();
  await expect(status).toContainText('Picture 1 of 5 · Paused');
  await expect(watch.getByRole('region', { name: 'AI assessment', exact: true })).toContainText('Waiting');
});

test('mode and hidden-tab changes freeze playback and keep answered visitor state intact', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Try it', exact: false }).click();
  await page.getByRole('button', { name: 'Needs checking', exact: true }).click();
  const before = await page.evaluate(() => localStorage.getItem('ai-inspection-pilot-lab:visitor:v1'));
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  const watch = page.getByRole('region', { name: 'Watch AI Inspect', exact: true });
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Look at the picture');
  await freezeClock(page);
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(1000);
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('AI assessment');
  await page.clock.runFor(300);
  await page.getByRole('button', { name: 'Try it yourself', exact: true }).click();
  await page.clock.runFor(9000);
  await expect(page.getByRole('button', { name: 'Needs checking', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await expect(page.getByRole('group', { name: 'Answer comparison', exact: true })).toHaveCount(0);
  expect(await page.evaluate(() => localStorage.getItem('ai-inspection-pilot-lab:visitor:v1'))).toBe(before);
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Paused · AI assessment');
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.evaluate(() => {
    Object.defineProperty(document, 'hidden', { configurable: true, value: true });
    document.dispatchEvent(new Event('visibilitychange'));
  });
  await page.clock.runFor(9000);
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Paused · AI assessment');
  await page.evaluate(() => {
    Object.defineProperty(document, 'hidden', { configurable: true, value: false });
    document.dispatchEvent(new Event('visibilitychange'));
  });
  await expect(watch.getByRole('button', { name: 'Play', exact: true })).toBeVisible();
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(700);
  await expect(watch.getByRole('status').filter({ hasText: 'Picture' })).toContainText('Dataset reference');
  expect(await page.evaluate(() => localStorage.getItem('ai-inspection-pilot-lab:visitor:v1'))).toBe(before);
});

test('loading starts no viewing timer; broken or changed pictures pause and can be retried', async ({ page }) => {
  let release!: () => void;
  const wait = new Promise<void>(resolve => { release = resolve; });
  let blocked = true, broken = false;
  await page.route('**/evidence/images/**', async route => {
    if (blocked) await wait;
    if (broken) return route.fulfill({ status: 404 });
    return route.continue();
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  const watch = page.getByRole('region', { name: 'Watch AI Inspect', exact: true });
  const status = watch.getByRole('status').filter({ hasText: 'Picture' });
  await expect(status).toContainText('Waiting for picture');
  await freezeClock(page);
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(15000);
  await expect(status).toContainText('Picture 1 of 5');
  await expect(watch.getByRole('region', { name: 'AI assessment', exact: true })).toContainText('Waiting');
  blocked = false; release();
  await expect(status).toContainText('Look at the picture');
  await page.clock.runFor(999);
  await expect(watch.getByRole('region', { name: 'AI assessment', exact: true })).toContainText('Waiting');
  await page.clock.runFor(1);
  await expect(status).toContainText('AI assessment');
  broken = true;
  await watch.getByRole('button', { name: 'Next', exact: true }).click();
  await expect(watch.getByRole('alert')).toContainText('missing or changed');
  await expect(watch.getByRole('button', { name: 'Play', exact: true })).toBeDisabled();
  broken = false;
  await watch.getByRole('button', { name: 'Retry picture', exact: true }).click();
  await expect(status).toContainText('Picture 2 of 5 · Paused · Look at the picture');
  await expect(watch.getByRole('button', { name: 'Play', exact: true })).toBeEnabled();
});

test('all five genuine results count once, stop, restart and leave visitor storage unchanged', async ({ page, browser }) => {
  const errors: string[] = [], external: string[] = [], methods: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { methods.push(r.method()); if (!r.url().startsWith('http://127.0.0.1:4175') && !r.url().startsWith('blob:')) external.push(r.url()); });
  const watch = await openWatch(page);
  const before = await page.evaluate(() => localStorage.getItem('ai-inspection-pilot-lab:visitor:v1'));
  const bundle = await page.request.get('/evidence/bundle.json').then(r => r.json()) as Bundle;
  expect(bundle.execution).toBe('recorded_live');
  expect(bundle.runs[0].evidence.run.model_id).toBe('gemini-3.5-flash-lite');
  await expect(page.getByRole('navigation', { name: 'Main navigation' }).locator('[aria-current]')).toHaveCount(0);
  const status = watch.getByRole('status').filter({ hasText: 'Picture' });
  const counts = watch.getByRole('region', { name: `${bundle.runs[0].report.model_id} playback totals`, exact: true });
  const count = (name: string) => counts.getByRole('region', { name, exact: true }).locator('strong');
  const observations: { image: string; ai: string; reference: string }[] = [];
  let flagged = 0, missed = 0, falseAlarms = 0;
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  for (let n = 0; n < 5; n++) {
    await expect(status).toContainText(`Picture ${n + 1} of 5 · Playing · Look at the picture`);
    await expect(counts).toContainText(`${n} of 5 references shown`);
    await page.clock.runFor(1000);
    await expect(status).toContainText('AI assessment');
    await expect(counts).toContainText(`${n} of 5 references shown`);
    await page.clock.runFor(1000);
    await expect(status).toContainText('Dataset reference');
    await expect(counts).toContainText(`${n + 1} of 5 references shown`);
    const id = bundle.challenge.image_ids[n];
    const image = bundle.images.find(i => i.image_id === id)!;
    const response = bundle.runs[0].evidence.predictions.find(p => p.image_id === id)!.attempts.at(-1)!.response!;
    const label = (decision: string) => decision === 'looks_acceptable' ? 'Looks fine' : 'Needs checking';
    const ai = label(response.decision), reference = image.label === 'normal' ? 'Looks fine' : 'Needs checking';
    await expect(watch.getByRole('region', { name: 'AI assessment', exact: true }).locator('.comparison-value')).toHaveText(ai);
    await expect(watch.getByRole('region', { name: 'Dataset reference', exact: true }).locator('.comparison-value')).toHaveText(reference);
    await watch.getByText('Why AI said this', { exact: true }).click();
    await expect(watch.locator('.observation')).toHaveText(response.observation);
    if (image.label === 'anomalous') { if (response.decision === 'needs_review') flagged++; else missed++; }
    else if (response.decision === 'needs_review') falseAlarms++;
    await expect(count('Defects flagged')).toHaveText(String(flagged));
    await expect(count('Defects missed')).toHaveText(String(missed));
    await expect(count('Good parts flagged')).toHaveText(String(falseAlarms));
    observations.push({ image: id, ai, reference });
    await page.clock.runFor(1000);
  }
  await expect(status).toContainText('Picture 5 of 5 · Finished');
  await expect(watch.getByRole('button', { name: 'Play', exact: true })).toBeDisabled();
  await expect(watch.getByRole('button', { name: 'Next', exact: true })).toBeDisabled();
  await page.clock.runFor(30000);
  await expect(status).toContainText('Picture 5 of 5 · Finished');
  expect({ flagged, missed, falseAlarms }).toEqual({ flagged: 2, missed: 1, falseAlarms: 2 });
  await watch.getByRole('button', { name: 'Previous', exact: true }).click();
  await expect(status).toContainText('Picture 4 of 5 · Paused · Look at the picture');
  await watch.getByLabel('Viewing time per picture', { exact: true }).selectOption('1.5');
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(500);
  await expect(status).toContainText('AI assessment');
  await page.clock.runFor(500);
  await expect(status).toContainText('Dataset reference');
  await expect(counts).toContainText('5 of 5 references shown');
  await expect(count('Defects flagged')).toHaveText('2');
  await expect(count('Defects missed')).toHaveText('1');
  await expect(count('Good parts flagged')).toHaveText('2');
  await watch.getByRole('button', { name: 'Restart', exact: true }).click();
  await expect(status).toContainText('Picture 1 of 5 · Paused');
  await expect(counts).toContainText('0 of 5 references shown');
  for (const name of ['Defects flagged', 'Defects missed', 'Good parts flagged']) await expect(count(name)).toHaveText('0');
  expect(await page.evaluate(() => localStorage.getItem('ai-inspection-pilot-lab:visitor:v1'))).toBe(before);
  expect(external).toEqual([]); expect(errors).toEqual([]); expect(methods.every(m => m === 'GET')).toBe(true);
  await mkdir(artifacts, { recursive: true });
  await writeFile(resolve(artifacts, 'playback.json'), JSON.stringify({ bundle_id: bundle.bundle_id, browser: browser.version(), observations,
    final_counts: { flagged, missed, falseAlarms }, unique_reveals: 5, stop_at_end: true, restart_clears_counts: true,
    backward_no_double_count: true, visitor_storage_unchanged: true, external_requests: external, methods, page_errors: errors,
    clock: 'Playwright clock paused between actions; stage boundaries advanced explicitly',
    tab_visibility_check: 'Synthetic document.hidden and visibilitychange; not a VS Code tab inspection',
  }, null, 2));
});

test('uncertain and unavailable saved fixture answers stay separate from successful decisions', async ({ page }) => {
  await page.route('**/evidence/**', async route => {
    const path = new URL(route.request().url()).pathname;
    if (path === '/evidence/bundle.json') return route.fulfill({ json: fixture });
    if (/^\/evidence\/(images|masks)\/img-\d{6}\.png$/.test(path)) return route.fulfill({ contentType: 'image/png', body: await readFile(resolve('../tests/fixtures/fastener-assets', path.slice('/evidence/'.length))) });
    return route.fulfill({ status: 404 });
  });
  const watch = await openWatch(page);
  const status = watch.getByRole('status').filter({ hasText: 'Picture' });
  for (let n = 0; n < 5; n++) {
    await watch.getByRole('button', { name: 'Play', exact: true }).click();
    await page.clock.runFor(1000);
    await expect(status).toContainText('AI assessment');
    await page.clock.runFor(1000);
    await expect(status).toContainText('Dataset reference');
    const card = watch.getByRole('region', { name: 'AI assessment', exact: true });
    if (n === 2 || n === 4) { await expect(card).toContainText('No answer'); await expect(card).toContainText('Human check needed'); }
    if (n === 3) { await expect(card).toContainText('Unsure'); await expect(card).toContainText('Sent for checking'); }
    if (n < 4) await watch.getByRole('button', { name: 'Next', exact: true }).click();
  }
  const results = watch.getByRole('region', { name: 'Results for this five-picture playback', exact: true });
  await expect(results).toContainText('5 of 5 references shown · 1 unsure · 2 unavailable');
  for (const [name, value] of [['Defects flagged', '0'], ['Defects missed', '1'], ['Good parts flagged', '1']]) await expect(results.getByRole('region', { name, exact: true }).locator('strong')).toHaveText(value);
  await expect(page.getByText('TEST EXAMPLES ONLY', { exact: false })).toBeVisible();
});

for (const width of [360, 768, 1440]) test(`playback keyboard, reduced motion and accessible comparison at ${width}px`, async ({ page }) => {
  test.setTimeout(60000);
  await page.setViewportSize({ width, height: 1000 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const watch = await openWatch(page);
  const status = watch.getByRole('status').filter({ hasText: 'Picture' });
  await watch.focus();
  await expect(watch).toBeFocused();
  await page.keyboard.press('Space');
  await page.clock.runFor(1000);
  await expect(status).toContainText('AI assessment');
  await page.keyboard.press('Escape');
  await page.clock.runFor(5000);
  await expect(status).toContainText('Paused · AI assessment');
  await page.keyboard.press('Space');
  await page.clock.runFor(1000);
  await expect(status).toContainText('Dataset reference');
  await page.keyboard.press('Space');
  await expect(status).toContainText('Paused · Dataset reference');
  const comparison = watch.getByRole('group', { name: 'Saved answer comparison', exact: true });
  await expect(comparison.getByRole('region')).toHaveCount(2);
  await expect(watch.getByText('Your answer', { exact: true })).toHaveCount(0);
  const boxes = await comparison.locator('.comparison-card').evaluateAll(cards => cards.map(card => {
    const b = card.getBoundingClientRect(); return { x: b.x, y: b.y, width: b.width, height: b.height };
  }));
  expect(Math.abs(boxes[0].height - boxes[1].height)).toBeLessThan(1);
  expect(Math.abs(boxes[0].width - boxes[1].width)).toBeLessThan(1);
  if (width >= 768) expect(Math.abs(boxes[0].y - boxes[1].y)).toBeLessThan(1);
  if (width === 1440) {
    const photo = await watch.locator('.image-window').boundingBox();
    expect(photo!.x + photo!.width).toBeLessThan(boxes[0].x);
    expect(boxes[0].y + boxes[0].height).toBeLessThan(1000);
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  // Resume the test clock for axe's own scheduling; playback remains paused.
  await page.clock.resume();
  const violations = (await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations;
  expect(violations).toEqual([]);
  expect(await watch.evaluate(el => el.getAnimations({ subtree: true }).length)).toBe(0);
  await mkdir(artifacts, { recursive: true });
  await watch.screenshot({ path: resolve(artifacts, `playback-${width}.png`) });
  await comparison.screenshot({ path: resolve(artifacts, `comparison-${width}.png`) });
  await watch.focus();
  await page.keyboard.press('ArrowRight');
  await expect(status).toContainText('Picture 2 of 5 · Paused');
  await page.keyboard.press('ArrowLeft');
  await expect(status).toContainText('Picture 1 of 5 · Paused');
  await page.keyboard.press('Home');
  await expect(status).toContainText('Picture 1 of 5 · Paused');
  await watch.getByRole('button', { name: 'Play', exact: true }).focus();
  await page.keyboard.press('Enter');
  await expect(watch.getByRole('button', { name: 'Pause', exact: true })).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(watch.getByRole('button', { name: 'Play', exact: true })).toBeFocused();
  await writeFile(resolve(artifacts, `accessibility-${width}.json`), JSON.stringify({ width, violations, boxes, reduced_motion: true,
    active_animations: 0, keyboard: ['Space', 'Escape', 'ArrowRight', 'ArrowLeft', 'Home', 'Enter'], overflow: false,
    note: 'Automated Chromium keyboard and axe checks; not screen-reader certification or VS Code inspection.' }, null, 2));
});
