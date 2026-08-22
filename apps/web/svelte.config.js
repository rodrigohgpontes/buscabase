import adapter from '@sveltejs/adapter-node';
import { readFileSync, existsSync } from 'node:fs';

function prerenderEntries() {
	const catalogPath = process.env.CATALOG_PATH || '/data/catalog/catalog.json';
	const local = 'src/lib/generated/catalog.json';
	const path = existsSync(catalogPath) ? catalogPath : existsSync(local) ? local : null;
	const entries = [
		'/',
		'/sobre',
		'/privacidade',
		'/acessibilidade',
		'/indices',
		'/robots.txt',
		'/llms.txt',
		'/sitemap.xml'
	];
	if (!path) return entries;
	try {
		const catalog = JSON.parse(readFileSync(path, 'utf-8'));
		for (const item of catalog.items || []) {
			if (item.url_path) entries.push(item.url_path);
		}
		for (const row of catalog.etapas || []) entries.push(`/etapa/${row.slug}`);
		for (const row of catalog.recortes || []) entries.push(`/ano/${row.slug}`);
		for (const row of catalog.areas || []) entries.push(`/area/${row.slug}`);
		for (const row of catalog.componentes || []) entries.push(`/componente/${row.slug}`);
		for (const row of catalog.documentos || []) entries.push(`/documento/${row.slug}`);
	} catch {
		/* SSR will still serve pages */
	}
	return entries;
}

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({ out: 'build' }),
		prerender: {
			entries: prerenderEntries(),
			handleHttpError: 'warn',
			handleMissingId: 'warn',
			handleUnseenRoutes: 'ignore'
		},
		csp: {
			mode: 'auto',
			directives: {
				'script-src': ['self'],
				'object-src': ['none'],
				'base-uri': ['self']
			}
		}
	}
};

export default config;
