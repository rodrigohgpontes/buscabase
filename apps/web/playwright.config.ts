import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
	webServer: process.env.PLAYWRIGHT_SKIP_WEBSERVER
		? undefined
		: {
				command: 'npm run preview -- --host 127.0.0.1 --port 4173',
				port: 4173,
				reuseExistingServer: true
			},
	testDir: 'e2e',
	use: {
		baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:4173',
		locale: 'pt-BR'
	},
	projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }]
});
