import { expect } from '@playwright/test';
import type { Locator, Page } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json' with { type: 'json' };
import catalogFixture from '../../tests/fixtures/playback-catalog.fixture.json' with { type: 'json' };
import genuine from '../public/evidence/bundle.json' with { type: 'json' };
import genuineCatalog from '../public/evidence/playback.v1.json' with { type: 'json' };
import type { Bundle, PlaybackCatalog } from '../src/types';

export const bundle = genuine as unknown as Bundle, catalog = genuineCatalog as PlaybackCatalog;
export const storage = 'ai-inspection-pilot-lab:visitor:v1';
export const status = (watch: Locator) => watch.locator('.playback-status');
export const modelNames = ['Gemini 3.5 Flash-Lite', 'Gemma 4 26B'];
export const totals = (watch: Locator, index: number) => watch.locator('.playback-score').nth(index);
export const metric = (totals: Locator, name: string) => totals.locator('dl > div').filter({ has: totals.page().getByText(name, { exact: true }) }).locator('dd');

export async function openWatch(page: Page, judgment = false) {
  await page.goto('/');
  if (judgment) {
    await page.getByRole('button', { name: 'Try it', exact: false }).click();
    await page.getByRole('button', { name: 'Looks fine', exact: true }).click();
    await page.getByRole('button', { name: 'Reveal AI assessment' }).click();
  }
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  const watch = page.getByRole('region', { name: 'Watch AI Inspect', exact: true });
  await expect(status(watch)).toContainText('Paused · Picture');
  await page.clock.install({ time: new Date('2026-10-25T12:00:00Z') });
  await page.clock.pauseAt(new Date('2026-10-25T13:00:00Z'));
  return watch;
}

export async function tick(page: Page, watch: Locator, stage: string, millis = 1000) {
  await page.clock.runFor(millis);
  await expect(status(watch)).toContainText(stage);
}

export async function fixturePlayback(page: Page, twoModels = false) {
  const data = structuredClone(fixture), pictures = structuredClone(catalogFixture);
  if (twoModels) {
    const second = structuredClone(data.runs[0]);
    second.evidence.run.run_id = 'fixture-second-run'; second.evidence.run.model_id = 'fixture-second-model';
    second.report.run_id = second.evidence.run.run_id; second.report.model_id = second.evidence.run.model_id;
    second.evidence.predictions.forEach(p => { p.run_id = second.evidence.run.run_id; });
    data.runs.push(second);
  }
  data.runs.forEach(r => r.evidence.predictions.forEach(p => p.attempts.forEach(a => { a.latency_ms = null; })));
  await page.route('**/evidence/**', async route => {
    const path = new URL(route.request().url()).pathname;
    if (path === '/evidence/bundle.json') return route.fulfill({ json: data });
    if (path === '/evidence/playback.v1.json') return route.fulfill({ json: pictures });
    if (/^\/evidence\/(images|masks)\/img-\d{6}\.png$/.test(path)) return route.fulfill({ contentType: 'image/png', body: await readFile(resolve('../tests/fixtures/fastener-assets', path.slice('/evidence/'.length))) });
    return route.fulfill({ status: 404 });
  });
  return data;
}

export async function finish(page: Page, watch: Locator, ids: string[], modelCount = 2, evidence: Bundle = bundle) {
  const duration = Math.ceil(4000 / (modelCount + 2));
  const seenCounts = evidence.runs.map(() => ({ flagged: 0, missed: 0, goodFlags: 0, correct: 0, unsure: 0, unavailable: 0 }));
  await watch.getByRole('button', { name: 'Start', exact: true }).click();
  for (const [index, id] of ids.entries()) {
    await expect(status(watch)).toContainText(`Picture ${index + 1} of ${ids.length} · Playing · Picture`);
    await expect(watch.getByRole('progressbar', { name: 'Playback progress', exact: true })).toHaveJSProperty('value', index);
    await expect(watch.locator('.playback-progress span')).toHaveText(`Picture ${index + 1} of ${ids.length}`);
    for (let n = 0; n < modelCount; n++) await expect(totals(watch, n)).toBeVisible();
    await expect(watch.locator('.playback-comparison .comparison-value:visible')).toHaveCount(0);
    for (let n = 0; n < modelCount; n++) {
      await page.clock.runFor(duration);
      await expect(watch.getByRole('group', { name: 'Saved answer comparison', exact: true }).locator('.comparison-value:visible')).toHaveCount(n + 1);
      await expect(watch.getByRole('region', { name: 'Dataset reference', exact: true }).locator('.comparison-value')).toBeHidden();
      const prediction = evidence.runs[n].evidence.predictions.find(p => p.image_id === id)!;
      const decision = prediction.status === 'success' ? prediction.attempts.at(-1)!.response?.decision : null;
      await expect(watch.getByRole('group', { name: 'Saved answer comparison', exact: true }).getByRole('region').nth(n).locator('.comparison-value')).toHaveText(
        decision === null ? 'No answer' : decision === 'uncertain' ? 'Unsure' : decision === 'looks_acceptable' ? 'Looks fine' : 'Needs checking');
    }
    await tick(page, watch, 'Dataset reference', duration);
    await expect(watch.getByRole('group', { name: 'Saved answer comparison', exact: true }).getByRole('region')).toHaveCount(modelCount + 1);
    for (const [n, run] of evidence.runs.entries()) {
      const p = run.evidence.predictions.find(p => p.image_id === id)!;
      const decision = p.status === 'success' ? p.attempts.at(-1)!.response?.decision : null;
      const label = run.report.images.find(i => i.image_id === id)!.label, count = seenCounts[n];
      if (decision === null) count.unavailable++;
      else if (decision === 'uncertain') count.unsure++;
      else if (label === 'anomalous') { if (decision === 'needs_review') { count.flagged++; count.correct++; } else count.missed++; }
      else if (decision === 'needs_review') count.goodFlags++;
      else count.correct++;
      const total = totals(watch, n);
      for (const [name, value] of [['Defects flagged', count.flagged], ['Defects missed', count.missed], ['Good parts flagged', count.goodFlags]] as const) await expect(metric(total, name)).toHaveText(String(value));
      await expect(total.locator('strong')).toHaveText(`${count.correct} / ${index + 1}`);
      await expect(total).toContainText(`${count.unsure} unsure · ${count.unavailable} unavailable`);
    }
    await expect(watch.getByRole('region', { name: 'The complete comparison', exact: true })).toHaveCount(0);
    await page.clock.runFor(duration);
  }
  const dashboard = watch.getByRole('region', { name: 'The complete comparison', exact: true });
  await expect(dashboard).toBeVisible();
  await expect(watch.getByRole('progressbar', { name: 'Playback progress', exact: true })).toHaveJSProperty('value', ids.length);
  await expect(watch.getByRole('progressbar', { name: 'Playback progress', exact: true })).toHaveJSProperty('max', ids.length);
  await expect(dashboard.getByRole('heading', { name: 'The complete comparison', exact: true })).toBeFocused();
  await expect(watch.getByRole('button', { name: 'Start', exact: true })).toBeDisabled();
  return dashboard;
}
