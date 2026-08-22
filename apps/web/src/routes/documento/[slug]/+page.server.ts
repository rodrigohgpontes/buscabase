import { error } from '@sveltejs/kit';
import { getDimensao } from '$lib/api';
import type { PageServerLoad } from './$types';

export const prerender = 'auto';

export const load: PageServerLoad = async ({ params }) => {
	try {
		return await getDimensao('documento', params.slug);
	} catch {
		error(404, 'Esse documento não está no recorte atual.');
	}
};
