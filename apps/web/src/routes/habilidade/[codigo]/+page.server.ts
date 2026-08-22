import { error, redirect } from '@sveltejs/kit';
import { getItem } from '$lib/api';
import type { PageServerLoad } from './$types';

export const prerender = 'auto';

export const load: PageServerLoad = async ({ params }) => {
	const codigo = params.codigo.toUpperCase();
	if (codigo !== params.codigo) {
		redirect(301, `/habilidade/${codigo}`);
	}
	try {
		const item = await getItem(codigo);
		if (item.tipo === 'objetivo') {
			redirect(301, `/aprendizagem/${codigo}`);
		}
		if (item.tipo.startsWith('competencia')) {
			redirect(301, `/competencia/${codigo}`);
		}
		return { item };
	} catch {
		error(404, 'Esse registro não está no recorte atual.');
	}
};
