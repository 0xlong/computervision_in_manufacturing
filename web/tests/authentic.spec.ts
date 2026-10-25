import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { existsSync, readFileSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import type { Bundle } from '../src/types';

const bundlePath = resolve('public/evidence/bundle.json');
const bundle = existsSync(bundlePath) ? JSON.parse(readFileSync(bundlePath, 'utf-8')) as Bundle : null;
const artifacts = resolve('../artifacts/browser-verification');

test('simple opening page has clear paths and keyboard-accessible background', async ({ page }) => {
  test.setTimeout(90000); // Multiple responsive accessibility scans share this test.
  test.skip(!bundle, 'Authentic saved evidence is required.');
  const directory = resolve('../artifacts/ui-simplification');
  await mkdir(directory, { recursive: true });
  const scans: { width: number; closed: number; expanded: number }[] = [];
  const imageRequests: string[] = [];
  page.on('request', r => { if (r.url().includes('/evidence/images/')) imageRequests.push(r.url()); });
  for (const width of [360, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto('/');
    await expect(page).toHaveTitle('AI Visual Inspection for Manufacturing');
    await expect(page.locator('footer')).toHaveCount(0);
    await expect(page.getByRole('link', { name: 'Dataset source', exact: true })).toBeHidden();
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('AI Visual Inspectionfor Manufacturing');
    await expect(page.getByText('A public-image demo', { exact: false })).toBeVisible();
    await expect(page.locator('main button')).toHaveCount(3);
    const about = page.getByText('About this demo', { exact: true });
    const background = page.getByText('The AI answers are saved responses', { exact: false });
    await expect(background).toBeHidden();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const closed = (await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations;
    expect(closed).toEqual([]);
    // Reach the disclosure in the natural tab order, starting from the skip link.
    await page.keyboard.press('Tab');
    await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
    for (let i = 0; i < 5; i++) await page.keyboard.press('Tab');
    await expect(about).toBeFocused();
    await page.screenshot({ path: resolve(directory, `opening-${width}.png`), fullPage: true });
    await page.keyboard.press('Enter');
    await expect(background).toBeVisible();
    await expect(page.getByRole('link', { name: 'Dataset source', exact: true })).toBeVisible();
    await expect(page.getByRole('link', { name: 'CC-BY-NC-SA-4.0', exact: true })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const expanded = (await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations;
    expect(expanded).toEqual([]);
    scans.push({ width, closed: closed.length, expanded: expanded.length });
    if (width === 1440) await page.screenshot({ path: resolve(directory, 'opening-about-expanded.png'), fullPage: true });
    await page.keyboard.press('Space');
    await expect(background).toBeHidden();
  }
  expect(imageRequests).toEqual([]);
  await page.getByRole('button', { name: 'See the results' }).focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main')).toBeFocused();
  await expect(page.getByText('115 assessed · 0 unavailable', { exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Manufacturing / AI Inspection' }).click();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('AI Visual Inspectionfor Manufacturing');
  await page.getByRole('button', { name: 'Try it' }).focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main')).toBeFocused();
  await expect(page.getByRole('button', { name: 'Looks fine', exact: true })).toBeEnabled();
  await writeFile(resolve(directory, 'opening-checks.json'), JSON.stringify({
    bundle_id: bundle!.bundle_id, accessibility: scans, entry_paths: ['challenge', 'results'],
    keyboard_disclosure: true, content_focus: true, opening_image_requests: 0,
  }, null, 2));
});

test('authentic fastener inspection to brief, responsive evidence and private state', async ({ page, browser }) => {
  test.setTimeout(90000); // Complete journey, downloads and responsive scans.
  test.skip(!bundle, 'Authentic local bundle has not been prepared. Fixture checks cannot replace it.');
  const b = bundle!, report = b.runs[0].report;
  expect(b.execution).toBe('recorded_live'); expect(report.expected).toBe(115);
  expect(report.succeeded + report.failed).toBe(115);
  await mkdir(artifacts, { recursive: true });
  const errors: string[] = [], external: string[] = [], methods: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { methods.push(r.method()); if (!r.url().startsWith('http://127.0.0.1:4175') && !r.url().startsWith('blob:')) external.push(r.url()); });
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Try it' })).toBeVisible();
  await page.screenshot({ path: resolve(artifacts, 'landing-1440.png'), fullPage: true });
  await page.getByRole('button', { name: 'Try it' }).click();
  for (let n = 0; n < 5; n++) {
    const answer = page.getByRole('button', { name: n % 2 ? 'Needs checking' : 'Looks fine', exact: true });
    await expect(answer).toBeEnabled();
    await expect(page.getByText('Dataset reference', { exact: true })).toHaveCount(0);
    if (n === 0) await page.screenshot({ path: resolve(artifacts, 'inspect-original-1440.png'), fullPage: true });
    await answer.click(); await page.getByRole('button', { name: 'Reveal AI assessment' }).click();
    await expect(page.locator('.answer-buttons')).toHaveCount(0);
    await expect(page.getByLabel('Revealed assessment', { exact: true })).toBeFocused();
    await expect(page.getByText('AI assessment', { exact: true })).toBeVisible();
    const response = b.runs[0].evidence.predictions.find(p => p.image_id === b.challenge.image_ids[n])!.attempts.at(-1)!.response!;
    await expect(page.getByRole('group', { name: 'Answer comparison' }).getByRole('region')).toHaveCount(3);
    const yourCard = page.getByRole('region', { name: 'Your answer', exact: true });
    const aiCard = page.getByRole('region', { name: 'AI assessment', exact: true });
    const referenceCard = page.getByRole('region', { name: 'Dataset reference', exact: true });
    await expect(yourCard.locator('.comparison-value')).toHaveText(n % 2 ? 'Needs checking' : 'Looks fine');
    await expect(referenceCard.locator('.comparison-value')).toHaveText(b.images.find(i => i.image_id === b.challenge.image_ids[n])!.label === 'normal' ? 'Looks fine' : 'Needs checking');
    await expect(aiCard.locator('.comparison-value')).toHaveText(response.decision === 'looks_acceptable' ? 'Looks fine' : response.decision === 'needs_review' ? 'Needs checking' : 'Unsure');
    await page.getByText('Why AI said this', { exact: true }).click();
    await expect(page.locator('.assessment .observation')).toHaveText(response.observation);
    await expect(page.locator('.assessment .observation')).toBeVisible();
    await page.getByText('Why AI said this', { exact: true }).click();
    if (n === 1) {
      await expect(aiCard).toContainText('Missed defect');
      await expect(page.getByText('You and AI disagree', { exact: true })).toBeVisible();
      await mkdir(resolve('../artifacts/ui-comparison'), { recursive: true });
      for (const width of [360, 768, 1440]) {
        await page.setViewportSize({ width, height: 1000 });
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
        if (width >= 768) {
          const boxes = await Promise.all([yourCard, aiCard, referenceCard].map(card => card.boundingBox()));
          for (const box of boxes) {
            expect(box!.y).toBeCloseTo(boxes[0]!.y, 0);
            expect(box!.height).toBeCloseTo(boxes[0]!.height, 0);
            expect(box!.width).toBeCloseTo(boxes[0]!.width, 0);
          }
        }
        expect((await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations).toEqual([]);
        await page.locator('.reveal').screenshot({ path: resolve(`../artifacts/ui-comparison/comparison-${width}.png`) });
      }
    }
    if (n === 0) await expect(aiCard).toContainText('False alarm');
    if (n === 3) {
      await expect(page.getByText('You and AI agree', { exact: true })).toBeVisible();
      await expect(yourCard).toContainText('Matches reference');
      await expect(aiCard).toContainText('Matches reference');
    }
    if (n === 1) {
      await page.getByRole('button', { name: 'Show reference outline' }).click();
      await expect(page.locator('.reference-mask')).toBeVisible();
      expect((await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations).toEqual([]);
      await page.screenshot({ path: resolve(artifacts, 'reveal-outline-1440.png'), fullPage: true });
    }
    if (n < 4) {
      await page.getByRole('button', { name: 'Next →', exact: true }).click();
      await expect(page.getByRole('heading', { name: 'Does this part need checking?' })).toBeFocused();
      expect(await page.evaluate(() => window.scrollY)).toBe(0);
    }
  }
  await expect(page.getByRole('heading', { name: 'Your five-picture summary' })).toBeVisible();
  await page.reload(); await expect(page.getByText('5 of 5 answered', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Go to image 1, answered' }).click();
  await expect(page.locator('.answer-buttons')).toHaveCount(0);
  await page.getByRole('button', { name: 'Results', exact: true }).click();
  await expect(page.getByText(`${report.succeeded} assessed · ${report.failed} unavailable`, { exact: true })).toBeVisible();
  const highlights = page.locator('.result-highlights section');
  await expect(highlights.nth(0).locator('strong')).toHaveText('81');
  await expect(highlights.nth(1).locator('strong')).toHaveText('12');
  await expect(highlights.nth(2).locator('strong')).toHaveText('5');
  await expect(page.getByText('86 of 115 parts sent for checking.', { exact: true })).toBeVisible();
  await expect(page.getByLabel('Components per day', { exact: true })).toBeHidden();
  await expect(page.getByRole('heading', { name: 'Successful AI assessments', exact: true })).toBeHidden();
  await mkdir(resolve('../artifacts/ui-iteration-two'), { recursive: true });
  for (const width of [360, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect((await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations).toEqual([]);
    await page.screenshot({ path: resolve(`../artifacts/ui-iteration-two/results-${width}.png`), fullPage: true });
  }
  await page.getByText('Explore a workday & download a brief', { exact: true }).click();
  await page.getByLabel('Available review minutes per day').fill('0');
  await page.getByLabel('Collect more evidence', { exact: true }).check();
  await page.getByLabel('Your reasoning', { exact: false }).fill('Local verification: representative site evidence and review capacity still need agreement.');
  await page.getByText('Where the results come from', { exact: true }).click();
  for (const asset of b.configuration_assets) {
    const configurationDownload = page.waitForEvent('download');
    await page.getByRole('link', { name: `Download frozen instructions, normal reference and image settings (${asset.run_id})`, exact: true }).click();
    const contents = await readFile((await (await configurationDownload).path())!, 'utf-8');
    expect(createHash('sha256').update(contents).digest('hex')).toBe(asset.sha256);
    const configuration = JSON.parse(contents);
    expect(configuration.run_id).toBe(asset.run_id);
    expect(configuration.frozen_plan.model_id).toBe(b.runs.find(r => r.report.run_id === asset.run_id)!.report.model_id);
    expect(configuration.frozen_plan.configuration.prompt).toContain('Inspect the candidate metal nut');
  }
  const contents: string[] = [];
  for (let n = 0; n < 2; n++) {
    const pending = page.waitForEvent('download'); await page.getByRole('button', { name: 'Download pilot brief (.md)' }).click();
    const download = await pending; contents.push(await readFile((await download.path())!, 'utf-8'));
  }
  expect(contents[0]).toBe(contents[1]); expect(contents[0]).toContain(b.runs[0].evidence.run.run_id);
  expect(contents[0]).toContain(`successful: ${report.succeeded}; failed: ${report.failed}`);
  await writeFile(resolve(artifacts, 'verified-pilot-brief.md'), contents[0]);
  await page.reload();
  await page.getByText('Explore a workday & download a brief', { exact: true }).click();
  await page.getByText('Detailed results', { exact: true }).click();
  await expect(page.getByLabel('Collect more evidence', { exact: true })).toBeChecked();
  const accessibility: { width: number; violations: number }[] = [];
  for (const width of [360, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const scan = await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
    expect(scan.violations).toEqual([]); accessibility.push({ width, violations: scan.violations.length });
    await page.screenshot({ path: resolve(artifacts, `lab-${width}.png`), fullPage: true });
  }
  const updates = await page.evaluate(async () => {
    const input = document.getElementById('scenario-volume') as HTMLInputElement;
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!;
    const durations = [];
    for (let i = 0; i < 100; i++) {
      const start = performance.now(); setter.call(input, String(1000 + i % 2)); input.dispatchEvent(new Event('input', { bubbles: true }));
      await new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
      durations.push(performance.now() - start);
    }
    return durations;
  });
  const p95 = [...updates].sort((a, b) => a - b)[94]; expect(p95).toBeLessThan(100);
  await page.evaluate(() => localStorage.setItem('unrelated-verification-key', 'keep'));
  await page.getByText('About this demo & reset progress', { exact: true }).click();
  await page.getByRole('button', { name: 'Reset all progress' }).click(); await page.getByRole('button', { name: 'Confirm reset' }).click();
  expect(await page.evaluate(() => localStorage.getItem('unrelated-verification-key'))).toBe('keep');
  expect(external).toEqual([]); expect(methods.every(m => m === 'GET')).toBe(true); expect(errors).toEqual([]);
  await writeFile(resolve(artifacts, 'journey.json'), JSON.stringify({ bundle_id: b.bundle_id, browser: browser.version(),
    viewport_checks: accessibility, scenario_changes: 100, scenario_update_p95_ms: p95, external_requests: external,
    page_errors: errors, deterministic_download: true, frozen_configuration_download: true, distinct_dataset_examples_in_screenshots: 2,
    note: 'Automated Chromium verification; VS Code integrated browser not verified. Screenshot subjects are not a manual-review count; separate visual review is recorded in the verification document.' }, null, 2));
});

test('authentic first challenge under 10 Mbps / 100 ms RTT', async ({ page, context, browser }) => {
  test.skip(!bundle, 'Authentic local bundle is required for timing.');
  const session = await context.newCDPSession(page);
  await session.send('Network.enable');
  await session.send('Network.emulateNetworkConditions', { offline: false, downloadThroughput: 1_250_000, uploadThroughput: 1_250_000, latency: 100 });
  const images: string[] = []; page.on('request', r => { if (r.url().includes('/evidence/images/')) images.push(r.url()); });
  const started = performance.now(); await page.goto('/'); await page.getByRole('button', { name: 'Try it' }).click();
  await expect(page.getByRole('button', { name: 'Looks fine', exact: true })).toBeEnabled();
  const milliseconds = performance.now() - started;
  expect(images).toHaveLength(1); expect(milliseconds).toBeLessThan(3000);
  await mkdir(artifacts, { recursive: true });
  await writeFile(resolve(artifacts, 'startup.json'), JSON.stringify({ browser: browser.version(),
    profile: '10 Mbps download/upload; 100 ms RTT; fresh Chromium context; production static preview',
    first_usable_challenge_ms: milliseconds, requested_challenge_images: images.length }, null, 2));
});
