import { error } from '@sveltejs/kit';
import { getItem } from '$lib/api';
import type { PageServerLoad } from './$types';

export const prerender = 'auto';

export const load: PageServerLoad = async ({ params }) => {
	try {
		return { item: await getItem(params.id) };
	} catch {
		error(404, 'Esse registro não está no recorte atual.');
	}
};
