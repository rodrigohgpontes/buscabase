export const SEARCH_PAGE_SIZE = 20;
export const SEARCH_API_MAX_LIMIT = 50;
export const SEARCH_N_MAX = 500;

export type SearchUrlState =
	| { mode: 'codigo'; codigo: string }
	| { mode: 'buscar'; q: string; n: number | null }
	| {
			mode: 'filtros';
			etapas: string[];
			anos: string[];
			componentes: string[];
			areas: string[];
			campos: string[];
			documentos: string[];
			tipos: string[];
			incluirRevogados: boolean;
			n: number | null;
	  }
	| { mode: 'perguntar'; pergunta: string };

function parseN(params: URLSearchParams): number | null {
	const raw = params.get('n');
	if (!raw) return null;
	const n = Number.parseInt(raw, 10);
	if (!Number.isFinite(n) || n <= SEARCH_PAGE_SIZE) return null;
	return Math.min(n, SEARCH_N_MAX);
}

function appendAll(params: URLSearchParams, key: string, values: string[]) {
	for (const value of values) {
		if (value) params.append(key, value);
	}
}

export function parseSearchUrl(params: URLSearchParams): SearchUrlState | null {
	const modo = params.get('modo');
	if (modo === 'codigo') {
		const codigo = (params.get('codigo') || '').trim();
		if (!codigo) return null;
		return { mode: 'codigo', codigo };
	}
	if (modo === 'buscar') {
		const q = (params.get('q') || '').trim();
		if (!q) return null;
		return { mode: 'buscar', q, n: parseN(params) };
	}
	if (modo === 'filtros') {
		return {
			mode: 'filtros',
			etapas: params.getAll('etapa').filter(Boolean),
			anos: params.getAll('ano').filter(Boolean),
			componentes: params.getAll('componente').filter(Boolean),
			areas: params.getAll('area').filter(Boolean),
			campos: params.getAll('campo').filter(Boolean),
			documentos: params.getAll('documento').filter(Boolean),
			tipos: params.getAll('tipo').filter(Boolean),
			incluirRevogados: params.get('incluir_revogados') === 'true',
			n: parseN(params)
		};
	}
	if (modo === 'perguntar') {
		return { mode: 'perguntar', pergunta: (params.get('pergunta') || '').trim() };
	}
	return null;
}

export function serializeSearchUrl(state: SearchUrlState): URLSearchParams {
	const params = new URLSearchParams();
	params.set('modo', state.mode);
	if (state.mode === 'codigo') {
		params.set('codigo', state.codigo);
		return params;
	}
	if (state.mode === 'buscar') {
		params.set('q', state.q);
		if (state.n && state.n > SEARCH_PAGE_SIZE) params.set('n', String(state.n));
		return params;
	}
	if (state.mode === 'filtros') {
		appendAll(params, 'etapa', state.etapas);
		appendAll(params, 'ano', state.anos);
		appendAll(params, 'componente', state.componentes);
		appendAll(params, 'area', state.areas);
		appendAll(params, 'campo', state.campos);
		appendAll(params, 'documento', state.documentos);
		appendAll(params, 'tipo', state.tipos);
		if (state.incluirRevogados) params.set('incluir_revogados', 'true');
		if (state.n && state.n > SEARCH_PAGE_SIZE) params.set('n', String(state.n));
		return params;
	}
	if (state.pergunta) params.set('pergunta', state.pergunta);
	return params;
}

export function searchUrlEquals(a: SearchUrlState | null, b: SearchUrlState | null): boolean {
	if (!a || !b) return a === b;
	return serializeSearchUrl(a).toString() === serializeSearchUrl(b).toString();
}

export function visibleCount(resultCount: number): number | null {
	return resultCount > SEARCH_PAGE_SIZE ? resultCount : null;
}
