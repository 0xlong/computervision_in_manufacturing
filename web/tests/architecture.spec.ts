import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { readFileSync } from 'node:fs';
import { fixturePlayback, openWatch, status, storage } from './playback-helpers';

const titles = ['Picture checks', 'Model runner', 'Gemini 3.5 Flash-Lite', 'Gemma 4 26B', 'Check & package', 'Saved evidence', 'Website host', 'Evidence loader', 'Website app', 'Workload calculator', 'Your saved progress', 'Brief download'];
const hints = ['without the dataset’s answers', 'does not run when you visit', 'One of two models', 'no third model’s results', 'Counts errors and failures', 'no new assessment is requested', 'not a verified deployment', 'Checks the saved files', 'never sent to a model', 'not new AI results', 'no server-side visitor database', 'same inputs give the same file'];

test('diagram model names match complete authentic saved runs and frozen configurations', async ({ page }) => {
  const bundle = JSON.parse(readFileSync('public/evidence/bundle.json', 'utf8'));
  expect(bundle.execution).toBe('recorded_live');
  const ids = bundle.runs.map(({ evidence, report }) => {
    const run = evidence.run;
    const config = JSON.parse(readFileSync(`public/evidence/configurations/${run.run_id}.json`, 'utf8'));
    expect(config.frozen_plan.model_id).toBe(run.model_id);
    expect(run.state).toBe('complete');
    expect(run.provider).toBe('gemini');
    expect(report.expected).toBe(115);
    expect(evidence.predictions).toHaveLength(report.expected);
    expect(report.model_id).toBe(run.model_id);
    return run.model_id;
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'See the results', exact: false }).click();
  await page.getByRole('button', { name: 'Architecture', exact: true }).click();
  expect(await page.locator('[data-model-id]').evaluateAll(nodes => nodes.map(n => n.getAttribute('data-model-id')))).toEqual(ids);
  for (const title of ['Gemini 3.5 Flash-Lite', 'Gemma 4 26B']) {
    await page.getByRole('button', { name: title, exact: true }).click();
    // A model highlights both its picture input and its assessment return.
    await expect(page.locator('.architecture-edge-active')).toHaveCount(2);
  }
  await expect(page.locator('.architecture-connection-label', { hasText: 'assessment' })).toHaveText(['Gemini assessment', 'Gemma assessment', 'Saved assessments']);
  await expect(page.locator('.architecture-legend')).toContainText('diagram clicks never call a model');
});

test('Architecture preserves genuine judgments, workday calculations, decision and brief; leaving Watch pauses it', async ({ page }) => {
  const external: string[] = [], errors: string[] = [];
  page.on('request', r => { if (!r.url().startsWith('http://127.0.0.1:4175') && !r.url().startsWith('blob:')) external.push(r.url()); });
  page.on('pageerror', e => errors.push(e.message));
  const watch = await openWatch(page, true);
  await watch.getByRole('button', { name: 'Start', exact: true }).click();
  await page.clock.runFor(750);
  await expect(status(watch)).toContainText('Gemini 3.5 Flash-Lite');
  const before = await page.evaluate(key => localStorage.getItem(key), storage);
  await page.getByRole('button', { name: 'Architecture', exact: true }).click();
  await expect(page.locator('#main')).toBeFocused();
  await expect(watch).toBeHidden();
  await page.clock.runFor(12000);
  expect(await page.evaluate(key => localStorage.getItem(key), storage)).toBe(before);
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  await expect(status(watch)).toContainText('Paused · Gemini 3.5 Flash-Lite');
  await page.getByRole('button', { name: 'Try it', exact: true }).click();
  await expect(page.getByText('1 of 5 answered', { exact: true })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Your answer', exact: true }).locator('.comparison-value')).toHaveText('Looks fine');
  await expect(page.locator('.answer-buttons')).toHaveCount(0);
  await page.getByRole('button', { name: 'Results', exact: true }).click();
  await page.getByText('Explore a workday & download a brief', { exact: true }).click();
  await page.getByLabel('Components per day', { exact: true }).fill('250');
  await page.getByLabel('Collect more evidence', { exact: true }).check();
  await page.getByLabel('Your reasoning', { exact: false }).fill('Keep human review.');
  const projection = await page.locator('.projection').innerText();
  const saved = await page.evaluate(key => localStorage.getItem(key), storage);
  async function brief() {
    const download = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download pilot brief (.md)' }).click();
    const stream = await (await download).createReadStream();
    const chunks: Buffer[] = [];
    for await (const chunk of stream!) chunks.push(chunk);
    return Buffer.concat(chunks).toString('utf8');
  }
  const originalBrief = await brief();
  await page.getByRole('button', { name: 'Architecture', exact: true }).click();
  const flow = page.getByRole('group', { name: 'Software components and data flow' });
  await expect(page.getByRole('navigation', { name: 'Main navigation' }).getByRole('button')).toHaveText(['Try it', 'Watch AI Inspect', 'Results', 'Architecture']);
  for (let n = 0; n < titles.length; n++) {
    await flow.getByRole('button', { name: new RegExp(titles[n]) }).click();
    await expect(page.locator('#architecture-hint')).toContainText(hints[n]);
    await expect(flow.locator('[aria-pressed="true"]')).toHaveCount(1);
  }
  expect(await page.evaluate(key => localStorage.getItem(key), storage)).toBe(saved);
  await page.getByRole('button', { name: 'Results', exact: true }).click();
  await page.getByText('Explore a workday & download a brief', { exact: true }).click();
  expect(await page.locator('.projection').innerText()).toBe(projection);
  await expect(page.getByLabel('Collect more evidence', { exact: true })).toBeChecked();
  await expect(page.getByLabel('Your reasoning', { exact: false })).toHaveValue('Keep human review.');
  expect(await brief()).toBe(originalBrief);
  await page.reload();
  await page.getByRole('button', { name: 'Try it', exact: true }).click();
  await expect(page.getByText('1 of 5 answered', { exact: true })).toBeVisible();
  expect(external).toEqual([]); expect(errors).toEqual([]);
});

for (const width of [320, 360, 768, 1440]) test(`Architecture keyboard, accessibility and layout at ${width}px`, async ({ page }) => {
  test.setTimeout(60000);
  await page.setViewportSize({ width, height: 1000 });
  const images: string[] = [];
  page.on('request', r => { if (/\/evidence\/(images|masks)\//.test(r.url())) images.push(r.url()); });
  await page.goto('/');
  await page.getByRole('button', { name: 'See the results', exact: false }).click();
  const architecture = page.getByRole('button', { name: 'Architecture', exact: true });
  await page.getByRole('button', { name: 'Results', exact: true }).focus();
  await page.keyboard.press('Tab'); await expect(architecture).toBeFocused();
  await page.keyboard.press('Enter'); await expect(page.locator('#main')).toBeFocused();
  const flow = page.getByRole('group', { name: 'Software components and data flow' });
  await page.keyboard.press('Tab');
  await expect(flow.getByRole('button', { name: 'Next component', exact: false })).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.locator('.architecture-viewport')).toBeFocused();
  for (let n = 0; n < titles.length; n++) {
    await page.keyboard.press('Tab');
    const node = flow.getByRole('button', { name: new RegExp(titles[n]) });
    await expect(node).toBeFocused();
    await page.keyboard.press(n % 2 ? 'Space' : 'Enter');
    await expect(node).toBeFocused(); await expect(node).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('#architecture-hint')).toContainText(hints[n]);
    const box = (await node.boundingBox())!;
    expect(box.width).toBeGreaterThanOrEqual(44); expect(box.height).toBeGreaterThanOrEqual(44);
    expect(await node.evaluate(el => getComputedStyle(el).outlineStyle)).toBe('solid');
    const window = (await page.locator('.architecture-viewport').boundingBox())!;
    expect(box.x).toBeGreaterThanOrEqual(window.x);
    expect(box.x + box.width).toBeLessThanOrEqual(window.x + window.width);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
  await expect(page.locator('nav [aria-current="page"]')).toHaveText('Architecture');
  if (width <= 650) {
    const resultsBox = (await page.getByRole('button', { name: 'Results', exact: true }).boundingBox())!;
    const architectureBox = (await architecture.boundingBox())!;
    expect(resultsBox.y).toBe(architectureBox.y);
    expect(resultsBox.x + resultsBox.width).toBeLessThanOrEqual(architectureBox.x);
  }
  await flow.getByRole('button', { name: titles[0], exact: true }).click();
  await expect(page.locator('#architecture-hint')).toContainText(hints[0]);
  await expect(page.locator('.architecture-detail')).toHaveCount(0);
  await expect(page.locator('.architecture-task-icon')).toHaveCount(titles.length);
  await expect(page.locator('.architecture-lanes')).toHaveCount(0);
  for (const heading of ['Preparation', 'Static delivery', 'Browser runtime']) await expect(page.getByText(heading, { exact: true })).toHaveCount(0);
  await expect(page.locator('.architecture-gateway')).toHaveCount(0);
  if (width >= 1440) expect(await page.locator('.architecture-viewport').evaluate(el => el.scrollWidth <= el.clientWidth)).toBe(true);
  expect((await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations).toEqual([]);
  expect(images).toEqual([]); // Explaining architecture does not load source pictures.
});

test('fixture notice remains explicit when exploring Architecture', async ({ page }) => {
  await fixturePlayback(page);
  await page.goto('/'); await page.getByRole('button', { name: 'See the results', exact: false }).click();
  await page.getByRole('button', { name: 'Architecture', exact: true }).click();
  await expect(page.getByText('TEST EXAMPLES ONLY', { exact: false })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Software architecture' })).toBeVisible();
});

test('software component tour reaches every module and restarts; reduced motion and touch remain usable', async ({ page, browser }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/'); await page.getByRole('button', { name: 'See the results', exact: false }).click();
  await page.getByRole('button', { name: 'Architecture', exact: true }).click();
  const flow = page.getByRole('group', { name: 'Software components and data flow' });
  for (let n = 0; n < titles.length; n++) {
    await expect(flow.getByRole('button', { name: titles[n], exact: true })).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('#architecture-hint')).toContainText(hints[n]);
    await expect(page.locator('.architecture-step-count')).toHaveText(`${n + 1} / ${titles.length}`);
    expect(await page.locator('.architecture-token').evaluate(el => getComputedStyle(el).transitionDuration)).toBe('0s');
    const action = page.locator('.architecture-next');
    await expect(action).toHaveText(n === titles.length - 1 ? 'Restart ↺' : 'Next component →');
    await action.focus(); await page.keyboard.press(n % 2 ? 'Space' : 'Enter');
    await expect(action).toBeFocused();
  }
  await expect(flow.getByRole('button', { name: titles[0], exact: true })).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('.architecture-external')).toHaveCount(2);
  await expect(page.locator('.architecture-external')).toHaveText(['Gemini 3.5 Flash-LiteAI model · Google API', 'Gemma 4 26BAI model · Google API']);
  await expect(page.locator('.architecture-legend')).toContainText('AI calls happen during preparation');
  await flow.getByRole('button', { name: 'Website host', exact: true }).click();
  await expect(page.locator('#architecture-hint')).toContainText('not a verified deployment');
  await flow.getByRole('button', { name: 'Your saved progress', exact: true }).click();
  await expect(page.locator('#architecture-hint')).toContainText('no server-side visitor database');
  const context = await browser.newContext({ viewport: { width: 360, height: 800 }, hasTouch: true, isMobile: true, reducedMotion: 'reduce' });
  const touch = await context.newPage();
  try {
    await touch.goto('/'); await touch.getByRole('button', { name: 'See the results', exact: false }).tap();
    await touch.getByRole('button', { name: 'Architecture', exact: true }).tap();
    for (let n = 0; n < titles.length; n++) {
      const node = touch.getByRole('button', { name: titles[n], exact: true });
      await node.tap(); await expect(node).toHaveAttribute('aria-pressed', 'true');
      await expect(touch.locator('#architecture-hint')).toContainText(hints[n]);
      const token = (await touch.locator('.architecture-token').boundingBox())!;
      const box = (await node.boundingBox())!;
      expect(token.x).toBeGreaterThan(box.x);
      expect(token.x + token.width).toBeLessThan(box.x + box.width);
    }
  } finally { await context.close(); }
});
