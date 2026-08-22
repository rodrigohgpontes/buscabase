import { getHealth } from '$lib/api';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async () => {
	try {
		const health = await getHealth();
		return { recorte: health.recorte, perguntar: health.perguntar, item_count: health.item_count };
	} catch {
		return { recorte: null, perguntar: false, item_count: 0 };
	}
};
