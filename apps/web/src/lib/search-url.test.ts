import { describe, expect, it } from 'vitest';
import {
	parseSearchUrl,
	SEARCH_N_MAX,
	SEARCH_PAGE_SIZE,
	serializeSearchUrl,
	searchUrlEquals,
	visibleCount
} from '$lib/search-url';

describe('parseSearchUrl', () => {
	it('lê busca simples e o número de resultados visíveis', () => {
		const parsed = parseSearchUrl(new URLSearchParams('modo=buscar&q=frações no 5º ano&n=40'));
		expect(parsed).toEqual({ mode: 'buscar', q: 'frações no 5º ano', n: 40 });
	});

	it('lê pesquisa por código', () => {
		expect(parseSearchUrl(new URLSearchParams('modo=codigo&codigo=EF05MA03'))).toEqual({
			mode: 'codigo',
			codigo: 'EF05MA03'
		});
	});

	it('lê campo e documento', () => {
		const params = new URLSearchParams();
		params.set('modo', 'filtros');
		params.append('campo', 'ei-campo-eo');
		params.append('documento', 'computacao-2022');
		expect(parseSearchUrl(params)).toEqual({
			mode: 'filtros',
			etapas: [],
			anos: [],
			componentes: [],
			areas: [],
			campos: ['ei-campo-eo'],
			documentos: ['computacao-2022'],
			tipos: [],
			incluirRevogados: false,
			n: null
		});
	});

	it('lê filtros repetidos e itens revogados', () => {
		const params = new URLSearchParams();
		params.set('modo', 'filtros');
		params.append('etapa', 'EF');
		params.append('etapa', 'EM');
		params.append('ano', 'ef-ano-05');
		params.append('componente', 'ef-comp-ma');
		params.set('incluir_revogados', 'true');
		expect(parseSearchUrl(params)).toEqual({
			mode: 'filtros',
			etapas: ['EF', 'EM'],
			anos: ['ef-ano-05'],
			componentes: ['ef-comp-ma'],
			areas: [],
			campos: [],
			documentos: [],
			tipos: [],
			incluirRevogados: true,
			n: null
		});
	});

	it('lê pergunta sem restaurar conversa', () => {
		expect(parseSearchUrl(new URLSearchParams('modo=perguntar&pergunta=O que é EF05MA03'))).toEqual({
			mode: 'perguntar',
			pergunta: 'O que é EF05MA03'
		});
	});

	it('ignora n padrão ou inválido', () => {
		expect(parseSearchUrl(new URLSearchParams('modo=buscar&q=frações&n=20'))).toMatchObject({
			n: null
		});
		expect(parseSearchUrl(new URLSearchParams('modo=buscar&q=frações&n=abc'))).toMatchObject({
			n: null
		});
	});

	it('limita n para evitar listas excessivas', () => {
		expect(
			parseSearchUrl(new URLSearchParams(`modo=buscar&q=frações&n=${SEARCH_N_MAX + 80}`))
		).toMatchObject({ n: SEARCH_N_MAX });
	});

	it('recusa modo incompleto', () => {
		expect(parseSearchUrl(new URLSearchParams('modo=buscar'))).toBeNull();
		expect(parseSearchUrl(new URLSearchParams('modo=codigo'))).toBeNull();
		expect(parseSearchUrl(new URLSearchParams())).toBeNull();
	});
});

describe('serializeSearchUrl', () => {
	it('omite n na primeira página', () => {
		expect(
			serializeSearchUrl({ mode: 'buscar', q: 'frações', n: SEARCH_PAGE_SIZE }).toString()
		).toBe('modo=buscar&q=fra%C3%A7%C3%B5es');
	});

	it('preserva o recorte visível depois de mostrar mais', () => {
		expect(serializeSearchUrl({ mode: 'buscar', q: 'frações', n: 40 }).toString()).toBe(
			'modo=buscar&q=fra%C3%A7%C3%B5es&n=40'
		);
	});

	it('faz ida e volta dos filtros', () => {
		const state = {
			mode: 'filtros' as const,
			etapas: ['EF'],
			anos: ['ef-ano-05'],
			componentes: [],
			areas: [],
			campos: ['ei-campo-eo'],
			documentos: ['bncc-2018'],
			tipos: ['habilidade'],
			incluirRevogados: false,
			n: 60
		};
		expect(parseSearchUrl(serializeSearchUrl(state))).toEqual(state);
	});
});

describe('searchUrlEquals e visibleCount', () => {
	it('compara o estado canônico', () => {
		expect(
			searchUrlEquals(
				{ mode: 'buscar', q: 'frações', n: null },
				{ mode: 'buscar', q: 'frações', n: null }
			)
		).toBe(true);
		expect(
			searchUrlEquals(
				{ mode: 'buscar', q: 'frações', n: 40 },
				{ mode: 'buscar', q: 'frações', n: null }
			)
		).toBe(false);
		expect(searchUrlEquals(null, null)).toBe(true);
	});

	it('só registra n além da primeira página', () => {
		expect(visibleCount(20)).toBeNull();
		expect(visibleCount(40)).toBe(40);
	});
});
