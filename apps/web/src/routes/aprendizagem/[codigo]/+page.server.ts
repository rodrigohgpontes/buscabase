import { error, redirect } from '@sveltejs/kit';
import { getItem } from '$lib/api';
import type { PageServerLoad } from './$types';

export const prerender = 'auto';

export const load: PageServerLoad = async ({ params }) => {
	const codigo = params.codigo.toUpperCase();
	if (codigo !== params.codigo) redirect(301, `/aprendizagem/${codigo}`);
	try {
		return { item: await getItem(codigo) };
	} catch {
		error(404, 'Esse registro não está no recorte atual.');
	}
};
