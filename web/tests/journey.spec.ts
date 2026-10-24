import { test, expect } from '@playwright/test';
import type { Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import fixture from '../../tests/fixtures/fastener-bundle.fixture.json' with { type: 'json' };

async function fixtures(page: Page) {
  await page.route('**/evidence/**', async route => {
    const path = new URL(route.request().url()).pathname;
    if (path === '/evidence/bundle.json') return route.fulfill({ json: fixture });
    if (/^\/evidence\/(images|masks)\/img-\d{6}\.png$/.test(path)) return route.fulfill({
      contentType: 'image/png', body: await readFile(resolve('../tests/fixtures/fastener-assets', path.slice('/evidence/'.length))),
    });
    return route.fulfill({ status: 404, body: 'Unavailable test asset' });
  });
}
async function start(page: Page) {
  await page.goto('/'); await page.getByRole('button', { name: 'Start the inspection' }).click();
  await expect(page.getByRole('button', { name: 'Looks acceptable', exact: true })).toBeEnabled();
}

test('five answers, gated reveal, zoom, locked answers, refresh, export and reset', async ({ page }) => {
  await fixtures(page);
  const outgoing: string[] = [];
  page.on('request', request => { if (!request.url().startsWith('http://127.0.0.1:4175') && !request.url().startsWith('blob:')) outgoing.push(request.url()); });
  await start(page);
  await expect(page.getByText('Dataset reference', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Reveal evidence' })).toBeDisabled();
  await page.getByRole('button', { name: 'Zoom in', exact: true }).click();
  await expect(page.getByText('125%', { exact: true })).toBeVisible();
  for (let n = 0; n < 5; n++) {
    const answer = page.getByRole('button', { name: n % 2 ? 'Needs further inspection' : 'Looks acceptable', exact: true });
    await expect(answer).toBeEnabled(); await answer.click();
    await page.getByRole('button', { name: 'Reveal evidence' }).click();
    await expect(page.getByText('Dataset reference', { exact: true })).toBeVisible();
    await expect(answer).toBeDisabled();
    await expect(page.getByText('Saved model assessment', { exact: true })).toBeVisible();
    if (n < 4) await page.getByRole('button', { name: 'Next →', exact: true }).click();
  }
  await expect(page.getByRole('heading', { name: 'Your five-picture summary' })).toBeVisible();
  await page.reload();
  await expect(page.getByText('5 of 5 answered', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Go to image 1, answered' }).click();
  await expect(page.getByRole('button', { name: 'Looks acceptable', exact: true })).toBeDisabled();
  await page.getByRole('button', { name: 'Evidence & pilot', exact: true }).click();
  await page.getByLabel('Available review minutes per day').fill('0');
  await expect(page.getByText('Review demand exceeds the entered capacity.', { exact: false })).toBeVisible();
  await page.getByLabel('Collect more evidence', { exact: true }).check();
  await page.getByLabel('Your reasoning', { exact: false }).fill('<script>TEST rationale</script>');
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download pilot brief (.md)' }).click();
  const download = await downloadPromise;
  const text = await readFile((await download.path())!, 'utf-8');
  expect(text).toContain('coverage: 0.5'); expect(text).toContain('Collect more evidence');
  expect(text).not.toContain('<script>'); expect(outgoing).toEqual([]);
  await page.getByRole('button', { name: 'Reset current track' }).click();
  await page.getByRole('button', { name: 'Keep progress' }).click();
  await expect(page.getByLabel('Collect more evidence', { exact: true })).toBeChecked();
  await page.getByRole('button', { name: 'Reset all progress' }).click();
  await page.getByRole('button', { name: 'Confirm reset' }).click();
  await page.getByRole('button', { name: 'Start the inspection' }).click();
  await expect(page.getByText('0 of 5 answered', { exact: true })).toBeVisible();
});

test('invalid assumptions suspend projections and export; untrusted rationale stays text', async ({ page }) => {
  await fixtures(page); await page.goto('/');
  await page.getByRole('button', { name: 'See the results' }).click();
  await page.getByLabel('Pilot with human review', { exact: true }).check();
  await expect(page.getByRole('button', { name: 'Download pilot brief (.md)' })).toBeEnabled();
  await page.getByLabel('Components per day', { exact: true }).fill('-1');
  await expect(page.getByText('Projections and export are paused.', { exact: false })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Download pilot brief (.md)' })).toBeDisabled();
  await page.getByLabel('Components per day', { exact: true }).fill('0');
  await expect(page.getByRole('button', { name: 'Download pilot brief (.md)' })).toBeEnabled();
  await page.getByLabel('Your reasoning', { exact: false }).fill('<img src=x onerror=alert(1)>');
  await expect(page.locator('.decision img')).toHaveCount(0);
});

test('corrupt progress and blocked storage remain usable', async ({ page }) => {
  await fixtures(page);
  await page.addInitScript(() => localStorage.setItem('ai-inspection-pilot-lab:visitor:v1', '{broken'));
  await page.goto('/'); await expect(page.getByText('Saved progress could not be read.', { exact: false })).toBeVisible();
  await page.addInitScript(() => Object.defineProperty(window, 'localStorage', { get() { throw Error('TEST storage blocked'); } }));
  await page.reload(); await expect(page.getByText('Browser storage is unavailable.', { exact: false }).first()).toBeVisible();
  await page.getByRole('button', { name: 'Start the inspection' }).click();
  await expect(page.getByRole('button', { name: 'Looks acceptable', exact: true })).toBeEnabled();
});

test('missing/corrupt evidence and missing images have recovery controls', async ({ page }) => {
  await page.route('**/evidence/bundle.json', route => route.fulfill({ json: { schema_version: 999 } }));
  await page.goto('/'); await expect(page.getByRole('button', { name: 'Retry evidence' })).toBeVisible();
  await page.unroute('**/evidence/bundle.json'); await fixtures(page);
  await page.route('**/evidence/images/**', route => route.fulfill({ status: 404 }));
  await page.getByRole('button', { name: 'Retry evidence' }).click();
  await page.getByRole('button', { name: 'Start the inspection' }).click();
  await expect(page.getByRole('button', { name: 'Retry picture' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Looks acceptable', exact: true })).toBeDisabled();
});

for (const width of [360, 768, 1440]) test(`keyboard, accessibility and layout at ${width}px`, async ({ page }) => {
  await page.setViewportSize({ width, height: 1000 }); await fixtures(page); await page.goto('/');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeVisible();
  await page.keyboard.press('Tab'); await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Enter');
  await page.getByRole('button', { name: 'Start the inspection' }).focus(); await page.keyboard.press('Enter');
  await expect(page.getByRole('button', { name: 'Looks acceptable', exact: true })).toBeEnabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect((await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations).toEqual([]);
  await page.getByRole('button', { name: 'Looks acceptable', exact: true }).focus(); await page.keyboard.press('Enter');
  await page.getByRole('button', { name: 'Reveal evidence' }).focus(); await page.keyboard.press('Enter');
  await expect(page.getByText('Dataset reference', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Evidence & pilot', exact: true }).click();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect((await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()).violations).toEqual([]);
});
