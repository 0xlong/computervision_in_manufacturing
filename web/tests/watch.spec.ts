import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { bundle, catalog, fixturePlayback, metric, modelNames, openWatch, status, storage, tick, totals } from './playback-helpers';

test('picture → first model → second model → reference; counts wait for the reference and navigation stays minimal', async ({ page }) => {
  const images: string[] = [];
  page.on('request', r => { if (r.url().includes('/evidence/images/')) images.push(r.url()); });
  const watch = await openWatch(page);
  await expect(status(watch)).toContainText('Picture 1 of 115 · Paused · Picture');
  await expect(watch.locator('.watch-heading p')).toHaveCount(0);
  await expect(watch.getByText('About this playback', { exact: true })).toHaveCount(0);
  await expect(page.locator('.about-demo')).toBeHidden();
  await expect(page.locator('.context-bar')).toHaveCount(0);
  expect(await status(watch).evaluate(el => getComputedStyle(el).clipPath)).toBe('inset(50%)');
  expect((await status(watch).boundingBox())!.height).toBe(1);
  await expect(page.getByRole('navigation', { name: 'Main navigation' }).getByRole('button')).toHaveText(['Try it', 'Watch AI Inspect', 'Results']);
  await expect(page.getByRole('button', { name: 'Try it yourself', exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Watch AI Inspect', exact: true })).toHaveCount(1);
  await expect(watch.getByRole('combobox')).toHaveCount(1); // Viewing time; both models are always shown.
  expect(new Set(images).size).toBe(1); // Catalog is complete; images load one at a time.
  const comparison = watch.getByRole('group', { name: 'Saved answer comparison', exact: true });
  await expect(comparison.getByRole('region').getByRole('heading')).toHaveText([...modelNames, 'Dataset reference']);
  await expect(comparison.locator('.comparison-value:visible')).toHaveCount(0);
  for (let n = 0; n < 2; n++) await expect(totals(watch, n)).toBeVisible();
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await tick(page, watch, modelNames[0]);
  await expect(comparison.locator('.comparison-value:visible')).toHaveCount(1);
  await expect(comparison.getByRole('region', { name: modelNames[0], exact: true })).toContainText('Needs checking');
  await expect(comparison.getByRole('group', { name: `${modelNames[0]} playback score`, exact: true })).toBeVisible();
  await expect(totals(watch, 0).locator('strong')).toHaveText('0 / 0');
  await tick(page, watch, modelNames[1]);
  await expect(comparison.locator('.comparison-value:visible')).toHaveCount(2);
  await expect(comparison.getByRole('region', { name: 'Dataset reference', exact: true }).locator('.comparison-value')).toBeHidden();
  for (let n = 0; n < 2; n++) await expect(metric(totals(watch, n), 'Defects flagged')).toHaveText('0');
  const scoreDetails = totals(watch, 0).getByText('Score details', { exact: true });
  await scoreDetails.focus(); await page.keyboard.press('Enter');
  await expect(metric(totals(watch, 0), 'Defects flagged')).toBeVisible();
  await tick(page, watch, 'Dataset reference');
  await expect(scoreDetails).toBeFocused(); // Reference reveal preserves this open control.
  await expect(metric(totals(watch, 0), 'Defects flagged')).toBeVisible();
  await expect(comparison.getByRole('region')).toHaveCount(3);
  await expect(comparison.locator('.comparison-value:visible')).toHaveCount(3);
  for (let n = 0; n < 2; n++) {
    await expect(metric(totals(watch, n), 'Defects flagged')).toHaveText('1');
    await expect(totals(watch, n).locator('strong')).toHaveText('1 / 1');
  }
  await expect(watch.locator('.playback-results')).toHaveCount(0);
  await tick(page, watch, 'Picture 2 of 115');
  await expect(comparison.locator('.comparison-value:visible')).toHaveCount(0);
  for (let n = 0; n < 2; n++) {
    await expect(totals(watch, n)).toBeVisible();
    await expect(totals(watch, n).locator('strong')).toHaveText('1 / 1');
  }
  await tick(page, watch, modelNames[0]);
  for (let n = 0; n < 2; n++) {
    await expect(totals(watch, n)).toBeVisible();
    await expect(totals(watch, n).locator('strong')).toHaveText('1 / 1');
  }
  // Revisit the same reference; neither model gains a second count.
  await watch.focus(); await page.keyboard.press('Home');
  await expect(metric(totals(watch, 0), 'Defects flagged')).toHaveText('0');
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  for (const stage of [...modelNames, 'Dataset reference']) await tick(page, watch, stage);
  await watch.getByRole('button', { name: 'Next', exact: true }).click();
  await watch.getByRole('button', { name: 'Previous', exact: true }).click();
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  for (const stage of [...modelNames, 'Dataset reference']) await tick(page, watch, stage);
  await expect(metric(totals(watch, 0), 'Defects flagged')).toHaveText('1');
});

test('pause keeps remaining viewing time; speed, top tabs and hidden tabs preserve the stage and visitor judgments', async ({ page }) => {
  const watch = await openWatch(page, true);
  const before = await page.evaluate(key => localStorage.getItem(key), storage);
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(400);
  await watch.getByRole('button', { name: 'Pause', exact: true }).click();
  await page.clock.runFor(5000);
  await expect(status(watch)).toContainText('Paused · Picture');
  await watch.getByLabel('Viewing time', { exact: true }).selectOption('8');
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(1199); await expect(status(watch)).toContainText('Playing · Picture');
  await tick(page, watch, modelNames[0], 1);
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('button', { name: 'Try it', exact: true }).click();
  await page.clock.runFor(10000);
  await expect(page.getByRole('region', { name: 'Your answer', exact: true })).toContainText('Looks fine');
  expect(await page.evaluate(key => localStorage.getItem(key), storage)).toBe(before);
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  await expect(status(watch)).toContainText(`Paused · ${modelNames[0]}`);
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, value: true }); document.dispatchEvent(new Event('visibilitychange')); });
  await page.clock.runFor(10000);
  await expect(status(watch)).toContainText(`Paused · ${modelNames[0]}`);
  await page.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, value: false }); document.dispatchEvent(new Event('visibilitychange')); });
  expect(await page.evaluate(key => localStorage.getItem(key), storage)).toBe(before);
});

test('loading and changed pictures hold the timer; retry recovers without revealing answers', async ({ page }) => {
  let release!: () => void;
  const pending = new Promise<void>(r => { release = r; });
  let blocked = true, broken = false;
  await page.route('**/evidence/images/**', async route => { if (blocked) await pending; return broken ? route.fulfill({ status: 404 }) : route.continue(); });
  await page.goto('/'); await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  const watch = page.getByRole('region', { name: 'Watch AI Inspect', exact: true });
  await expect(status(watch)).toContainText('Loading picture');
  await page.clock.install(); await page.clock.pauseAt(new Date(Date.now() + 1000));
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(20000);
  await expect(status(watch)).toContainText('Picture 1 of 115');
  await expect(watch.getByRole('group', { name: 'Saved answer comparison', exact: true }).locator('.comparison-value:visible')).toHaveCount(0);
  for (let n = 0; n < 2; n++) await expect(totals(watch, n)).toBeVisible();
  blocked = false; release();
  await expect(status(watch)).toContainText('Playing · Picture');
  await page.clock.runFor(999); await expect(status(watch)).toContainText('Playing · Picture');
  await tick(page, watch, modelNames[0], 1);
  broken = true; await watch.getByRole('button', { name: 'Next', exact: true }).click();
  await expect(watch.getByRole('alert')).toContainText('missing or changed');
  await expect(watch.getByRole('button', { name: 'Play', exact: true })).toBeDisabled();
  broken = false; await watch.getByRole('button', { name: 'Retry picture', exact: true }).click();
  await expect(status(watch)).toContainText('Picture 2 of 115 · Paused · Picture');
});

test('missing, corrupt and mismatched catalogs offer recovery and never invent a short playback', async ({ page }) => {
  let mode = 'missing';
  await page.route('**/evidence/playback.v1.json', route => {
    if (mode === 'missing') return route.fulfill({ status: 404 });
    if (mode === 'corrupt') return route.fulfill({ body: '{broken' });
    return route.fulfill({ json: mode === 'mismatch' ? { ...catalog, bundle_id: 'another-bundle' } : catalog });
  });
  await page.goto('/'); await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  for (const next of ['corrupt', 'mismatch', 'valid']) {
    await expect(page.getByRole('alert')).toContainText('Playback pictures could not be loaded');
    mode = next; await page.getByRole('button', { name: 'Retry playback', exact: true }).click();
  }
  await expect(page.locator('.playback-status')).toContainText('Picture 1 of 115 · Paused · Picture');
});

for (const width of [320, 360, 768, 1440]) test(`three revealed cards, keyboard and minimal layout at ${width}px`, async ({ page }) => {
  test.setTimeout(60000);
  await page.setViewportSize({ width, height: 1000 }); await page.emulateMedia({ reducedMotion: 'reduce' });
  const watch = await openWatch(page);
  for (let n = 0; n < 2; n++) await expect(totals(watch, n)).toBeVisible();
  await expect(watch.getByRole('button', { name: 'Show reference outline', exact: true })).toHaveCount(0);
  const before = await watch.locator('.playback-score').evaluateAll(scores => scores.map(el => { const b = el.getBoundingClientRect(); const card = el.closest('.comparison-card')!.getBoundingClientRect(); return { x: b.x - card.x, y: b.y - card.y }; }));
  await watch.focus(); await page.keyboard.press('Space');
  for (const stage of [...modelNames, 'Dataset reference']) await tick(page, watch, stage);
  await page.keyboard.press('Escape');
  const comparison = watch.getByRole('group', { name: 'Saved answer comparison', exact: true });
  await expect(comparison.getByRole('region')).toHaveCount(3);
  await expect(comparison.locator('.comparison-value:visible')).toHaveCount(3);
  const after = await watch.locator('.playback-score').evaluateAll(scores => scores.map(el => { const b = el.getBoundingClientRect(); const card = el.closest('.comparison-card')!.getBoundingClientRect(); return { x: b.x - card.x, y: b.y - card.y }; }));
  expect(after).toEqual(before);
  for (let n = 0; n < 2; n++) {
    const card = comparison.getByRole('region', { name: modelNames[n], exact: true });
    await expect(card.locator('.playback-score strong')).toHaveText('1 / 1');
    await expect(card.locator('.comparison-status')).toContainText('Matches reference');
    await expect(card.locator('.playback-score > details')).not.toHaveAttribute('open', '');
    const contained = await card.evaluate(el => {
      const card = el.getBoundingClientRect(), score = el.querySelector('.playback-score')!.getBoundingClientRect();
      const status = el.querySelector('.comparison-status')!.getBoundingClientRect();
      return score.top >= status.bottom && score.bottom <= card.bottom && score.left >= card.left && score.right <= card.right;
    });
    expect(contained).toBe(true);
  }
  const boxes = await comparison.locator('.comparison-card').evaluateAll(cards => cards.map(c => { const b = c.getBoundingClientRect(); return { x: b.x, y: b.y, width: b.width, height: b.height }; }));
  expect(Math.abs(boxes[0].width - boxes[1].width)).toBeLessThan(1);
  const photograph = (await watch.locator('.image-window').boundingBox())!;
  if (width >= 650) {
    for (const box of boxes) {
      expect(Math.abs(box.height - photograph.height)).toBeLessThan(1);
      expect(Math.abs(box.width - photograph.width)).toBeLessThan(1);
    }
    expect(Math.abs(boxes[0].y - photograph.y)).toBeLessThan(1);
    if (width >= 1280) for (const box of boxes) expect(Math.abs(box.y - photograph.y)).toBeLessThan(1);
    else {
      expect(boxes[1].y).toBeGreaterThan(photograph.y + photograph.height);
      expect(Math.abs(boxes[1].y - boxes[2].y)).toBeLessThan(1);
    }
  } else expect(boxes[1].y).toBeGreaterThan(boxes[0].y);
  const controls = await watch.locator('.watch-controls button, .watch-controls select').evaluateAll(elements => elements.map(el => {
    const box = el.getBoundingClientRect(), style = getComputedStyle(el);
    return { height: box.height, radius: style.borderRadius };
  }));
  for (const control of controls) {
    expect(control.height).toBeGreaterThanOrEqual(44);
    expect(control.radius).toBe('8px');
  }
  expect(Math.abs(controls.at(-1)!.height - controls.at(-2)!.height)).toBeLessThan(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.clock.resume();
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
  expect(await watch.evaluate(el => el.getAnimations({ subtree: true }).length)).toBe(0);
  const artifacts = resolve('../artifacts/aligned-watch'); await mkdir(artifacts, { recursive: true });
  await comparison.screenshot({ path: resolve(artifacts, `cards-${width}.png`) });
  await watch.locator('.watch-controls').screenshot({ path: resolve(artifacts, `controls-${width}.png`) });
  await writeFile(resolve(artifacts, `layout-${width}.json`), JSON.stringify({ width, boxes, photograph, controls, overflow: false, violations: [], reduced_motion: true }, null, 2));
  const reference = comparison.getByRole('region', { name: 'Dataset reference', exact: true });
  const outline = reference.getByRole('button', { name: 'Show reference outline', exact: true });
  await expect(watch.locator('.picture-panel').getByRole('button', { name: /reference outline/ })).toHaveCount(0);
  await outline.focus(); await page.keyboard.press('Enter');
  await expect(reference.getByRole('button', { name: 'Hide reference outline', exact: true })).toBeFocused();
  await expect(outline).toHaveCount(0);
  await expect(watch.getByRole('img', { name: 'Dataset reference region', exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.keyboard.press('Enter');
  await expect(watch.getByRole('img', { name: 'Dataset reference region', exact: true })).toHaveCount(0);
  for (let n = 0; n < 2; n++) {
    const summary = totals(watch, n).getByText('Score details', { exact: true });
    await summary.focus(); await page.keyboard.press('Enter');
    await expect(summary).toBeFocused();
    await expect(metric(totals(watch, n), 'Defects flagged')).toBeVisible();
    expect(await summary.evaluate(el => getComputedStyle(el).outlineStyle)).toBe('solid');
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await watch.focus(); await page.keyboard.press('ArrowRight');
  await expect(status(watch)).toContainText('Picture 2 of 115 · Paused');
  for (let n = 0; n < 2; n++) {
    await expect(totals(watch, n)).toBeVisible();
    await expect(totals(watch, n).locator('strong')).toHaveText('1 / 1');
  }
  await page.keyboard.press('ArrowLeft'); await expect(status(watch)).toContainText('Picture 1 of 115 · Paused');
  await page.keyboard.press('Home'); await expect(metric(totals(watch, 0), 'Defects flagged')).toHaveText('0');
});

test('reference tile lazily loads its outline, recovers a missing mask and resets between fixture pictures', async ({ page }) => {
  const data = await fixturePlayback(page);
  let broken = true;
  const masks: string[] = [];
  await page.route('**/evidence/masks/**', route => {
    masks.push(new URL(route.request().url()).pathname);
    return broken ? route.fulfill({ status: 404 }) : route.fallback();
  });
  const watch = await openWatch(page);
  const reference = watch.getByRole('region', { name: 'Dataset reference', exact: true });
  const reveal = async () => {
    await watch.getByRole('button', { name: 'Play', exact: true }).click();
    for (const stage of [data.runs[0].report.model_id, 'Dataset reference']) await tick(page, watch, stage, 1334);
    await watch.getByRole('button', { name: 'Pause', exact: true }).click();
  };
  await reveal();
  expect(masks).toEqual([]);
  await reference.getByRole('button', { name: 'Show reference outline', exact: true }).click();
  await expect(watch.getByRole('alert')).toContainText('reference outline is unavailable');
  expect(masks).toEqual(['/evidence/masks/img-000001.png']);
  broken = false;
  await watch.getByRole('button', { name: 'Retry outline', exact: true }).click();
  await expect(watch.getByRole('img', { name: 'Dataset reference region', exact: true })).toBeVisible();
  await expect(reference.getByRole('button', { name: 'Hide reference outline', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await watch.getByRole('button', { name: 'Next', exact: true }).click();
  await reveal(); // Normal fixture image has no annotation.
  await expect(reference.getByRole('button')).toHaveCount(0);
  await expect(watch.getByRole('img', { name: 'Dataset reference region', exact: true })).toHaveCount(0);
  await watch.getByRole('button', { name: 'Next', exact: true }).click();
  await reveal();
  await expect(reference.getByRole('button', { name: 'Show reference outline', exact: true })).toHaveAttribute('aria-pressed', 'false');
  await reference.getByRole('button', { name: 'Show reference outline', exact: true }).click();
  await expect(watch.getByRole('img', { name: 'Dataset reference region', exact: true })).toBeVisible();
  expect(masks.at(-1)).toBe('/evidence/masks/img-000003.png');
});

test('identical fixture models show an empty filtered state and Show all recovers paused', async ({ page }) => {
  await fixturePlayback(page, true); const watch = await openWatch(page);
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await watch.getByRole('button', { name: 'Different answers only (0)', exact: true }).click();
  await expect(status(watch)).toHaveText('No matching pictures · Paused · Different answers');
  await expect(watch.getByRole('button', { name: 'Play', exact: true })).toBeDisabled();
  await expect(watch.getByRole('button', { name: 'Next', exact: true })).toBeDisabled();
  await watch.focus(); await page.keyboard.press('Space'); await page.clock.runFor(20000);
  await expect(status(watch)).toContainText('Paused');
  await watch.getByRole('button', { name: 'Show all pictures', exact: true }).click();
  await expect(status(watch)).toContainText('Picture 1 of 6 · Paused · Picture');
});
