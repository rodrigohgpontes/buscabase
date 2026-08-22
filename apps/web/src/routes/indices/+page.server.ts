import { getHealth, getTaxonomies } from '$lib/api';
import type { PageServerLoad } from './$types';

export const prerender = false;

export const load: PageServerLoad = async () => {
	let taxonomias = null;
	try {
		taxonomias = await getTaxonomies();
	} catch {
		taxonomias = null;
	}
	try {
		const health = await getHealth();
		return { taxonomias, tag: health.recorte, item_count: health.item_count };
	} catch {
		return { taxonomias, tag: null, item_count: 0 };
	}
};
