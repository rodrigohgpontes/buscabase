import type { SearchUrlState } from '$lib/search-url';

export const SITE_ORIGIN = 'https://www.buscabase.com.br';
export const DEFAULT_OG_IMAGE = `${SITE_ORIGIN}/og-default.png`;
export const OG_IMAGE_WIDTH = 1200;
export const OG_IMAGE_HEIGHT = 630;

export const HOME_TITLE = 'Encontre o que você precisa na BNCC | Busca Base';
export const HOME_DESCRIPTION =
	'Encontre, confira e reutilize o texto da Base Nacional Comum Curricular. Busque por código, por filtros ou por tema. Se quiser, também pode perguntar.';
export const OG_IMAGE_ALT = 'Encontre o que você precisa na Base Nacional Comum Curricular';

export type SocialPreview = {
	title: string;
	description: string;
	url: string;
	image: string;
	type: 'website';
	locale: 'pt_BR';
};

export function absoluteUrl(pathAndQuery: string): string {
	if (pathAndQuery.startsWith('http://') || pathAndQuery.startsWith('https://')) return pathAndQuery;
	if (pathAndQuery.startsWith('/')) return `${SITE_ORIGIN}${pathAndQuery}`;
	return `${SITE_ORIGIN}/${pathAndQuery}`;
}

export function truncateText(value: string, max: number): string {
	const text = value.trim();
	if (text.length <= max) return text;
	return `${text.slice(0, max - 1).trimEnd()}…`;
}

export function socialPreview(input: {
	title: string;
	description: string;
	url: string;
	image?: string;
}): SocialPreview {
	return {
		title: input.title,
		description: input.description,
		url: input.url,
		image: input.image ?? DEFAULT_OG_IMAGE,
		type: 'website',
		locale: 'pt_BR'
	};
}

export function searchSharePreview(state: SearchUrlState): { title: string; description: string } {
	if (state.mode === 'codigo') {
		return {
			title: `${state.codigo} na BNCC | Busca Base`,
			description: `Consulte o texto de ${state.codigo} na Base Nacional Comum Curricular.`
		};
	}
	if (state.mode === 'buscar') {
		const q = truncateText(state.q, 60);
		return {
			title: `Busca: ${q} | Busca Base`,
			description: `Resultados da busca “${truncateText(state.q, 120)}” na Base Nacional Comum Curricular.`
		};
	}
	if (state.mode === 'filtros') {
		return {
			title: 'Consulta por filtros na BNCC | Busca Base',
			description: 'Itens da BNCC selecionados por etapa, ano, campo, área, componente ou documento.'
		};
	}
	const pergunta = truncateText(state.pergunta, 60);
	if (pergunta) {
		return {
			title: `${pergunta} | Busca Base`,
			description: `Uma pergunta sobre o que a Base Nacional Comum Curricular diz: “${truncateText(state.pergunta, 120)}”.`
		};
	}
	return {
		title: 'Pergunta sobre a BNCC | Busca Base',
		description: 'Uma pergunta sobre o que a Base Nacional Comum Curricular diz.'
	};
}
