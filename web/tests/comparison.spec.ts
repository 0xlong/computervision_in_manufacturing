import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json' with { type: 'json' };
import type { Bundle } from '../src/types';

const artifacts = resolve('../artifacts/model-comparison');

test('genuine complete-set comparison row shows real counts and measured request time', async ({ page, browser }) => {
  test.setTimeout(90000); // Multiple genuine rows and three responsive accessibility scans.
  const external: string[] = [], errors: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (!r.url().startsWith('http://127.0.0.1:4175') && !r.url().startsWith('blob:')) external.push(r.url()); });
  await page.goto('/');
  await page.getByRole('button', { name: 'See the results' }).click();
  const section = page.getByRole('region', { name: 'Compare models', exact: true });
  const table = section.getByRole('table');
  const row = table.getByRole('row').nth(1);
  const bundle = await page.request.get('/evidence/bundle.json').then(r => r.json()) as Bundle;
  if (bundle.runs.length === 1) await expect(section).toContainText('One completed model so far.');
  else await expect(section.getByText('One completed model so far.', { exact: false })).toHaveCount(0);
  await expect(table).toHaveAccessibleName('Complete 115-picture test set · Saved AI results');
  await expect(table.getByRole('row')).toHaveCount(bundle.runs.length + 1);
  await expect(row.getByRole('button', { name: 'gemini-3.5-flash-lite', exact: true })).toHaveAttribute('aria-pressed', 'true');
  const cells = row.getByRole('cell');
  await expect(cells.nth(0)).toHaveText('12 / 93');
  await expect(cells.nth(1)).toHaveText('5 / 22');
  await expect(cells.nth(2)).toHaveText('115 / 115');
  await expect(cells.nth(3)).toHaveText('0 / 115');
  await expect(cells.nth(4)).toHaveText('0 / 115');
  const times = bundle.runs[0].evidence.predictions.flatMap(p => p.attempts).map(a => a.latency_ms!).sort((a, b) => a - b);
  const median = (times[57] + times[58]) / 2;
  await expect(cells.nth(5)).toContainText(`${(median / 1000).toFixed(2)} s`);
  await expect(cells.nth(5)).toContainText('116 / 116 attempts timed');
  await expect(cells.nth(6)).toHaveText('86 / 115');
  // Check every genuine row, including coverage, uncertainty and retry timing.
  for (const [index, saved] of bundle.runs.entries()) {
    const values = table.getByRole('row').nth(index + 1).getByRole('cell');
    const m = saved.report.successful_output;
    await expect(values.nth(0)).toHaveText(`${m.fn} / ${m.anomalous}`);
    await expect(values.nth(1)).toHaveText(`${m.fp} / ${m.normal}`);
    await expect(values.nth(2)).toHaveText(`${saved.report.succeeded} / 115`);
    await expect(values.nth(3)).toHaveText(`${saved.report.failed} / 115`);
    const unsure = saved.evidence.predictions.filter(p => p.status === 'success' && p.attempts.at(-1)!.response?.decision === 'uncertain').length;
    await expect(values.nth(4)).toHaveText(`${unsure} / ${saved.report.succeeded}`);
    const attempts = saved.evidence.predictions.flatMap(p => p.attempts);
    const measured = attempts.flatMap(a => a.latency_ms === null ? [] : [a.latency_ms]).sort((a, b) => a - b);
    const mid = Math.floor(measured.length / 2);
    const requestMedian = measured.length % 2 ? measured[mid] : (measured[mid - 1] + measured[mid]) / 2;
    await expect(values.nth(5)).toContainText(`${(requestMedian / 1000).toFixed(2)} s`);
    await expect(values.nth(5)).toContainText(`${measured.length} / ${attempts.length} attempts timed`);
    await expect(values.nth(6)).toHaveText(`${saved.report.full_set_routing.review_count} / 115`);
  }
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
    genuine_models: bundle.runs.length, models: bundle.runs.map(r => ({ model: r.report.model_id, report: r.report })), images: 115, median_attempt_ms: median, attempts: times.length, scans,
    external_requests: external, page_errors: errors, visual_subject: 'Table only; no source photographs',
    note: 'All genuine complete rows checked against saved reports; baseline values also independently fixed above. Labelled fixtures retain failure edge cases.' }, null, 2));
});

test('genuine Gemma selection and five-picture playback keep visitor judgments unchanged', async ({ page, browser }) => {
  test.setTimeout(90000); // Five staged pictures, model switching and a mobile accessibility scan.
  const errors: string[] = [], external: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (!r.url().startsWith('http://127.0.0.1:4175') && !r.url().startsWith('blob:')) external.push(r.url()); });
  await page.goto('/');
  const bundle = await page.request.get('/evidence/bundle.json').then(r => r.json()) as Bundle;
  expect(bundle.execution).toBe('recorded_live');
  expect(bundle.runs.length).toBeGreaterThanOrEqual(2);
  const gemma = bundle.runs.find(r => r.report.model_id === 'gemma-4-26b-a4b-it')!;
  expect(gemma.report.expected).toBe(115);
  expect(gemma.evidence.run.state).toBe('complete');
  expect(gemma.evidence.run.inputs).toEqual(bundle.runs[0].evidence.run.inputs);
  await page.getByRole('button', { name: 'Try it', exact: false }).click();
  await page.getByRole('button', { name: 'Looks fine', exact: true }).click();
  await page.getByRole('button', { name: 'Reveal AI assessment' }).click();
  const before = await page.evaluate(() => JSON.parse(localStorage.getItem('ai-inspection-pilot-lab:visitor:v1')!));
  await page.getByRole('button', { name: 'Results', exact: true }).click();
  const model = page.getByRole('region', { name: 'Compare models', exact: true }).getByRole('button', { name: gemma.report.model_id, exact: true });
  await model.focus(); await page.keyboard.press('Enter');
  await expect(model).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: 'Try it', exact: true }).click();
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  const watch = page.getByRole('region', { name: 'Watch AI Inspect', exact: true });
  const status = watch.getByRole('status').filter({ hasText: 'Picture' });
  await expect(watch.getByLabel('Saved model', { exact: true })).toHaveValue(gemma.report.run_id);
  await expect(status).toContainText('Picture 1 of 5 · Paused · Look at the picture');
  await page.clock.install({ time: new Date('2026-10-25T12:00:00Z') });
  await page.clock.pauseAt(new Date('2026-10-25T13:00:00Z'));
  const results = watch.getByRole('region', { name: 'Results for this five-picture playback', exact: true });
  const count = (name: string) => results.getByRole('region', { name, exact: true }).locator('strong');
  let flagged = 0, missed = 0, falseAlarms = 0, unsure = 0, unavailable = 0;
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  for (const [index, id] of bundle.challenge.image_ids.entries()) {
    await expect(status).toContainText(`Picture ${index + 1} of 5 · Playing · Look at the picture`);
    await page.clock.runFor(1000);
    const image = bundle.images.find(i => i.image_id === id)!;
    const prediction = gemma.evidence.predictions.find(p => p.image_id === id)!;
    const response = prediction.status === 'success' ? prediction.attempts.at(-1)!.response : null;
    const expected = !response ? 'No answer' : response.decision === 'uncertain' ? 'Unsure' : response.decision === 'looks_acceptable' ? 'Looks fine' : 'Needs checking';
    await expect(watch.getByRole('region', { name: 'AI assessment', exact: true }).locator('.comparison-value')).toHaveText(expected);
    if (response) {
      await watch.getByText('Why AI said this', { exact: true }).click();
      await expect(watch.locator('.observation')).toHaveText(response.observation);
    }
    await page.clock.runFor(1000);
    if (!response) unavailable++;
    else if (response.decision === 'uncertain') unsure++;
    else if (image.label === 'anomalous') { if (response.decision === 'needs_review') flagged++; else missed++; }
    else if (response.decision === 'needs_review') falseAlarms++;
    await expect(count('Defects flagged')).toHaveText(String(flagged));
    await expect(count('Defects missed')).toHaveText(String(missed));
    await expect(count('Good parts flagged')).toHaveText(String(falseAlarms));
    await expect(results).toContainText(`${index + 1} of 5 references shown · ${unsure} unsure · ${unavailable} unavailable`);
    await page.clock.runFor(1000);
  }
  await expect(status).toContainText('Picture 5 of 5 · Finished');
  await watch.getByLabel('Saved model', { exact: true }).selectOption(bundle.runs[0].report.run_id);
  await expect(status).toContainText('Picture 5 of 5 · Paused · Look at the picture');
  await expect(results).toContainText('0 of 5 references shown');
  for (const label of ['Defects flagged', 'Defects missed', 'Good parts flagged']) await expect(count(label)).toHaveText('0');
  const after = await page.evaluate(() => JSON.parse(localStorage.getItem('ai-inspection-pilot-lab:visitor:v1')!));
  expect(after.answers).toEqual(before.answers); expect(after.revealed).toEqual(before.revealed);
  expect(after.selectedImage).toBe(before.selectedImage);
  await page.setViewportSize({ width: 360, height: 1000 });
  await page.clock.resume(); // Playback is paused; let accessibility checks schedule normally.
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
  expect(errors).toEqual([]); expect(external).toEqual([]);
  const directory = resolve('../artifacts/additional-models-oct25');
  await mkdir(directory, { recursive: true });
  await watch.getByRole('group', { name: 'Playback controls', exact: true }).screenshot({ path: resolve(directory, 'genuine-controls-360.png') });
  await writeFile(resolve(directory, 'genuine-playback-browser.json'), JSON.stringify({ bundle_id: bundle.bundle_id,
    browser: browser.version(), model: gemma.report.model_id, model_identities_match: true,
    five_picture_counts: { flagged, missed, falseAlarms, unsure, unavailable },
    model_switch_pauses_keeps_picture_and_clears_counts: true, visitor_judgments_unchanged: true,
    mobile_width: 360, automated_accessibility_violations: 0, page_errors: errors, external_requests: external,
    note: 'Production Chromium, controlled clock; not VS Code integrated browser. Counts are five teaching pictures, separate from 115-image metrics.' }, null, 2));
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
