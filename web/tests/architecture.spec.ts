import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { fixturePlayback, openWatch, status, storage } from './playback-helpers';

const titles = ['Public pictures', 'AI assessments', 'Checked evidence', 'Static website', 'Your exploration', 'Human decision'];
const headings = ['Start with traceable pictures.', 'Ask the models before the visit.', 'Check answers against the references.', 'Serve the evidence as ordinary files.', 'Explore the trade-offs in your browser.', 'Leave the next step to a person.'];

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
  const flow = page.getByRole('group', { name: 'Solution flow' });
  await expect(page.getByRole('navigation', { name: 'Main navigation' }).getByRole('button')).toHaveText(['Try it', 'Watch AI Inspect', 'Results', 'Architecture']);
  for (let n = 0; n < titles.length; n++) {
    await flow.getByRole('button', { name: new RegExp(titles[n]) }).click();
    await expect(page.locator('#architecture-detail-title')).toHaveText(headings[n]);
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
  const flow = page.getByRole('group', { name: 'Solution flow' });
  for (let n = 0; n < titles.length; n++) {
    await page.keyboard.press('Tab');
    const node = flow.getByRole('button', { name: new RegExp(titles[n]) });
    await expect(node).toBeFocused();
    await page.keyboard.press(n % 2 ? 'Space' : 'Enter');
    await expect(node).toBeFocused(); await expect(node).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('#architecture-detail-title')).toHaveText(headings[n]);
    const box = (await node.boundingBox())!;
    expect(box.width).toBeGreaterThanOrEqual(44); expect(box.height).toBeGreaterThanOrEqual(44);
    expect(await node.evaluate(el => getComputedStyle(el).outlineStyle)).toBe('solid');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
  await expect(page.locator('nav [aria-current="page"]')).toHaveText('Architecture');
  if (width <= 650) {
    const resultsBox = (await page.getByRole('button', { name: 'Results', exact: true }).boundingBox())!;
    const architectureBox = (await architecture.boundingBox())!;
    expect(resultsBox.y).toBe(architectureBox.y);
    expect(resultsBox.x + resultsBox.width).toBeLessThanOrEqual(architectureBox.x);
  }
  await flow.getByRole('button').first().click();
  await expect.poll(async () => {
    const detail = (await page.locator('#architecture-detail').boundingBox())!;
    return detail.y >= 0 && detail.y + detail.height <= 1000;
  }).toBe(true);
  expect((await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations).toEqual([]);
  expect(images).toEqual([]); // Explaining architecture does not load source pictures.
});

test('fixture notice remains explicit when exploring Architecture', async ({ page }) => {
  await fixturePlayback(page);
  await page.goto('/'); await page.getByRole('button', { name: 'See the results', exact: false }).click();
  await page.getByRole('button', { name: 'Architecture', exact: true }).click();
  await expect(page.getByText('TEST EXAMPLES ONLY', { exact: false })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'How it all fits together.' })).toBeVisible();
});
