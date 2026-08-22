import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

const apiTarget = process.env.API_INTERNAL_URL || 'http://127.0.0.1:8000';
const hmrClientPort = Number(process.env.VITE_HMR_CLIENT_PORT || 0);

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0',
		port: Number(process.env.PORT) || 5173,
		strictPort: true,
		hmr: hmrClientPort ? { clientPort: hmrClientPort } : undefined,
		watch: {
			usePolling: process.env.CHOKIDAR_USEPOLLING === 'true',
			interval: 300
		},
		proxy: {
			'/api': {
				target: apiTarget,
				changeOrigin: true,
				timeout: 180_000
			}
		}
	},
	test: {
		include: ['src/**/*.test.ts']
	}
});

