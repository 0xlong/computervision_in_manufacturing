import { test, expect } from '@playwright/test';
import type { Page } from '@playwright/test';

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
  await watch.getByLabel('Viewing time', { exact: true }).selectOption('6');
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(1199);
  await expect(status).toContainText('Look at the picture');
  await page.clock.runFor(1);
  await expect(status).toContainText('AI assessment');
  await page.clock.runFor(500);
  await watch.getByLabel('Viewing time', { exact: true }).selectOption('3');
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
