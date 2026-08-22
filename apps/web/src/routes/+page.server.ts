import { getTaxonomies } from '$lib/api';
import type { PageServerLoad } from './$types';

export const prerender = false;

export const load: PageServerLoad = async ({ url, setHeaders }) => {
	if (url.searchParams.has('modo') || url.searchParams.has('q') || url.searchParams.has('codigo')) {
		setHeaders({ 'X-Robots-Tag': 'noindex, nofollow' });
	}
	try {
		const taxonomias = await getTaxonomies();
		return { taxonomias };
	} catch {
		return { taxonomias: null };
	}
};
