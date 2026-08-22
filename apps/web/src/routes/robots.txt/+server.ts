import type { RequestHandler } from './$types';

export const prerender = true;

export const GET: RequestHandler = async () => {
	const body = `User-agent: *
Allow: /
Disallow: /*?*modo=
Disallow: /*?*q=
Disallow: /*?*codigo=
Disallow: /*?*pergunta=
Disallow: /uso

Sitemap: https://www.buscabase.com.br/sitemap.xml
`;
	return new Response(body, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
};
