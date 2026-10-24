import { test, expect } from '@playwright/test';

test('saved playback starts paused, reveals in stages and keeps visitor answers separate', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Watch AI Inspect', exact: true }).click();
  const watch = page.getByRole('region', { name: 'Watch AI Inspect', exact: true });
  await expect(watch.getByRole('img', { name: 'Metal nut for your visual inspection' })).toBeVisible();
  await expect(watch.getByRole('status').filter({ hasText: 'Picture 1' })).toContainText('Paused');
  await expect(watch.getByRole('region', { name: 'AI assessment', exact: true })).toContainText('Waiting');
  await expect(page.getByText('Your answer', { exact: true })).toHaveCount(0);
  await page.clock.install();
  await watch.getByRole('button', { name: 'Play', exact: true }).click();
  await page.clock.runFor(1000);
  await expect(watch.getByRole('region', { name: 'AI assessment', exact: true })).toContainText('Looks fine');
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
