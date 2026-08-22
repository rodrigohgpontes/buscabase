import { error } from '@sveltejs/kit';
import { apiBase } from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ request, url, setHeaders }) => {
	setHeaders({ 'X-Robots-Tag': 'noindex, nofollow' });
	const dias = url.searchParams.get('dias') === '30' ? 30 : 7;
	const auth = request.headers.get('authorization') || '';
	const response = await fetch(`${apiBase()}/api/uso?dias=${dias}`, {
		headers: { accept: 'application/json', authorization: auth }
	});
	if (response.status === 401) {
		error(401, 'Autenticação necessária.');
	}
	if (response.status === 404) {
		error(404, 'Não encontrado.');
	}
	if (!response.ok) {
		error(500, 'Não foi possível carregar o uso.');
	}
	return { resumo: await response.json(), dias };
};
