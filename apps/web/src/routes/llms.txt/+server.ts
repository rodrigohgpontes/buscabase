import type { RequestHandler } from './$types';

export const prerender = true;

export const GET: RequestHandler = async () => {
	const body = `# Busca Base
# A consulta acontece em https://www.buscabase.com.br/
# Páginas estáveis descrevem o recorte; combinações de busca não devem ser indexadas.

https://www.buscabase.com.br/
https://www.buscabase.com.br/sobre
https://www.buscabase.com.br/privacidade
https://www.buscabase.com.br/acessibilidade
https://www.buscabase.com.br/indices
https://www.buscabase.com.br/sitemap.xml
`;
	return new Response(body, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
};
