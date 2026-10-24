import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests', workers: 1, fullyParallel: false, timeout: 30000,
  use: { baseURL: 'http://127.0.0.1:4175', viewport: { width: 1440, height: 1000 }, trace: 'retain-on-failure' },
  webServer: { command: 'npm run build && npm run preview -- --port 4175', url: 'http://127.0.0.1:4175', reuseExistingServer: false },
  reporter: [['list'], ['html', { open: 'never' }]],
});
