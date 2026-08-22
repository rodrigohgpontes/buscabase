import { error } from '@sveltejs/kit';
import { getDimensao } from '$lib/api';
import type { PageServerLoad } from './$types';

export const prerender = 'auto';

export const load: PageServerLoad = async ({ params }) => {
	try {
		return await getDimensao('area', params.slug);
	} catch {
		error(404, 'Essa área não está no recorte atual.');
	}
};
