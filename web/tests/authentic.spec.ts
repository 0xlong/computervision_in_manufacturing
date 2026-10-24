import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { existsSync, readFileSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import type { Bundle } from '../src/types';

const bundlePath = resolve('public/evidence/bundle.json');
const bundle = existsSync(bundlePath) ? JSON.parse(readFileSync(bundlePath, 'utf-8')) as Bundle : null;
const artifacts = resolve('../artifacts/browser-verification');

test('authentic fastener inspection to brief, responsive evidence and private state', async ({ page, browser }) => {
  test.skip(!bundle, 'Authentic local bundle has not been prepared. Fixture checks cannot replace it.');
  const b = bundle!, report = b.runs[0].report;
  expect(b.execution).toBe('recorded_live'); expect(report.expected).toBe(115);
  expect(report.succeeded + report.failed).toBe(115);
  await mkdir(artifacts, { recursive: true });
  const errors: string[] = [], external: string[] = [], methods: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { methods.push(r.method()); if (!r.url().startsWith('http://127.0.0.1:4175') && !r.url().startsWith('blob:')) external.push(r.url()); });
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Start the inspection' })).toBeVisible();
  await page.screenshot({ path: resolve(artifacts, 'landing-1440.png'), fullPage: true });
  await page.getByRole('button', { name: 'Start the inspection' }).click();
  for (let n = 0; n < 5; n++) {
    const answer = page.getByRole('button', { name: n % 2 ? 'Needs further inspection' : 'Looks acceptable', exact: true });
    await expect(answer).toBeEnabled();
    await expect(page.getByText('Dataset reference', { exact: true })).toHaveCount(0);
    if (n === 0) await page.screenshot({ path: resolve(artifacts, 'inspect-original-1440.png'), fullPage: true });
    await answer.click(); await page.getByRole('button', { name: 'Reveal evidence' }).click();
    await expect(answer).toBeDisabled();
    await expect(page.getByText('Saved model assessment', { exact: true })).toBeVisible();
    if (n === 1) {
      await page.getByRole('button', { name: 'Show reference outline' }).click();
      await expect(page.locator('.reference-mask')).toBeVisible();
      expect((await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations).toEqual([]);
      await page.screenshot({ path: resolve(artifacts, 'reveal-outline-1440.png'), fullPage: true });
    }
    if (n < 4) await page.getByRole('button', { name: 'Next →', exact: true }).click();
  }
  await expect(page.getByRole('heading', { name: 'Your five-picture summary' })).toBeVisible();
  await page.reload(); await expect(page.getByText('5 of 5 answered', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Go to image 1, answered' }).click();
  await expect(page.getByRole('button', { name: 'Looks acceptable', exact: true })).toBeDisabled();
  await page.getByRole('button', { name: 'Evidence & pilot', exact: true }).click();
  await expect(page.getByText(`${report.succeeded} successful assessments / 115 expected images`, { exact: true })).toBeVisible();
  await page.getByLabel('Available review minutes per day').fill('0');
  await page.getByLabel('Collect more evidence', { exact: true }).check();
  await page.getByLabel('Your reasoning', { exact: false }).fill('Local verification: representative site evidence and review capacity still need agreement.');
  await page.getByText('Inspect provenance, selection and limitations', { exact: true }).click();
  const configurationDownload = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download frozen instructions, normal reference and image settings', exact: false }).click();
  const configuration = JSON.parse(await readFile((await (await configurationDownload).path())!, 'utf-8'));
  expect(configuration.run_id).toBe(b.runs[0].evidence.run.run_id);
  expect(configuration.frozen_plan.configuration.prompt).toContain('Inspect the candidate metal nut');
  const contents: string[] = [];
  for (let n = 0; n < 2; n++) {
    const pending = page.waitForEvent('download'); await page.getByRole('button', { name: 'Download pilot brief (.md)' }).click();
    const download = await pending; contents.push(await readFile((await download.path())!, 'utf-8'));
  }
  expect(contents[0]).toBe(contents[1]); expect(contents[0]).toContain(b.runs[0].evidence.run.run_id);
  expect(contents[0]).toContain(`successful: ${report.succeeded}; failed: ${report.failed}`);
  await writeFile(resolve(artifacts, 'verified-pilot-brief.md'), contents[0]);
  await page.reload(); await expect(page.getByLabel('Collect more evidence', { exact: true })).toBeChecked();
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
  await page.getByRole('button', { name: 'Reset all progress' }).click(); await page.getByRole('button', { name: 'Confirm reset' }).click();
  expect(await page.evaluate(() => localStorage.getItem('unrelated-verification-key'))).toBe('keep');
  expect(external).toEqual([]); expect(methods.every(m => m === 'GET')).toBe(true); expect(errors).toEqual([]);
  await writeFile(resolve(artifacts, 'journey.json'), JSON.stringify({ bundle_id: b.bundle_id, browser: browser.version(),
    viewport_checks: accessibility, scenario_changes: 100, scenario_update_p95_ms: p95, external_requests: external,
    page_errors: errors, deterministic_download: true, frozen_configuration_download: true, viewed_dataset_examples_for_manual_review: 2,
    note: 'Automated Chromium verification; VS Code native browser helper unavailable. Screenshots require separate human/agent visual inspection.' }, null, 2));
});

test('authentic first challenge under 10 Mbps / 100 ms RTT', async ({ page, context, browser }) => {
  test.skip(!bundle, 'Authentic local bundle is required for timing.');
  const session = await context.newCDPSession(page);
  await session.send('Network.enable');
  await session.send('Network.emulateNetworkConditions', { offline: false, downloadThroughput: 1_250_000, uploadThroughput: 1_250_000, latency: 100 });
  const images: string[] = []; page.on('request', r => { if (r.url().includes('/evidence/images/')) images.push(r.url()); });
  const started = performance.now(); await page.goto('/'); await page.getByRole('button', { name: 'Start the inspection' }).click();
  await expect(page.getByRole('button', { name: 'Looks acceptable', exact: true })).toBeEnabled();
  const milliseconds = performance.now() - started;
  expect(images).toHaveLength(1); expect(milliseconds).toBeLessThan(3000);
  await mkdir(artifacts, { recursive: true });
  await writeFile(resolve(artifacts, 'startup.json'), JSON.stringify({ browser: browser.version(),
    profile: '10 Mbps download/upload; 100 ms RTT; fresh Chromium context; production static preview',
    first_usable_challenge_ms: milliseconds, requested_challenge_images: images.length }, null, 2));
});
