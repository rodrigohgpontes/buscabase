import { error } from '@sveltejs/kit';
import { apiBase } from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ request, setHeaders }) => {
	setHeaders({ 'X-Robots-Tag': 'noindex, nofollow' });
	const auth = request.headers.get('authorization') || '';
	const response = await fetch(`${apiBase()}/api/recados`, {
		headers: { accept: 'application/json', authorization: auth }
	});
	if (response.status === 401) {
		error(401, 'Autenticação necessária.');
	}
	if (response.status === 404) {
		error(404, 'Não encontrado.');
	}
	if (!response.ok) {
		error(500, 'Não foi possível carregar os recados.');
	}
	const body = (await response.json()) as {
		recados: {
			id: number;
			created_at: string;
			nome: string;
			email: string;
			mensagem: string;
			pagina: string | null;
		}[];
	};
	return { recados: body.recados };
};
