import { apiBase } from '$lib/api';
import type { RequestHandler } from './$types';

export const prerender = false;

function urlset(paths: string[]): string {
	const origin = 'https://www.buscabase.com.br';
	const body = paths
		.map((path) => `  <url><loc>${origin}${path}</loc></url>`)
		.join('\n');
	return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</urlset>`;
}

async function catalog() {
	const response = await fetch(`${apiBase()}/api/catalogo`);
	if (!response.ok) return { items: [], etapas: [], recortes: [], areas: [], componentes: [], documentos: [] };
	return response.json();
}

export const GET: RequestHandler = async ({ params }) => {
	const kind = params.kind;
	const data = await catalog();
	let paths: string[] = [];
	if (kind === 'paginas.xml') {
		paths = ['/', '/sobre', '/privacidade', '/acessibilidade', '/indices'];
	} else if (kind === 'habilidades.xml') {
		paths = data.items
			.filter((i: { tipo: string; url_path: string }) => i.tipo === 'habilidade' || i.tipo === 'objetivo')
			.map((i: { url_path: string }) => i.url_path);
	} else if (kind === 'competencias.xml') {
		paths = data.items
			.filter((i: { tipo: string }) => String(i.tipo).startsWith('competencia'))
			.map((i: { url_path: string }) => i.url_path);
	} else if (kind === 'estrutura.xml') {
		paths = [
			...(data.etapas || []).map((r: { slug: string }) => `/etapa/${r.slug}`),
			...(data.recortes || []).map((r: { slug: string }) => `/ano/${r.slug}`),
			...(data.areas || []).map((r: { slug: string }) => `/area/${r.slug}`),
			...(data.componentes || []).map((r: { slug: string }) => `/componente/${r.slug}`),
			...(data.documentos || []).map((r: { slug: string }) => `/documento/${r.slug}`)
		];
	} else {
		return new Response('Não encontrado', { status: 404 });
	}
	return new Response(urlset(paths), { headers: { 'content-type': 'application/xml; charset=utf-8' } });
};
