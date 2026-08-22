import { describe, expect, it } from 'vitest';
import {
	absoluteUrl,
	DEFAULT_OG_IMAGE,
	HOME_TITLE,
	OG_IMAGE_ALT,
	searchSharePreview,
	SITE_ORIGIN,
	socialPreview,
	truncateText
} from '$lib/social';

describe('absoluteUrl', () => {
	it('prefixa caminhos do site', () => {
		expect(absoluteUrl('/habilidade/EF05MA03')).toBe(`${SITE_ORIGIN}/habilidade/EF05MA03`);
		expect(absoluteUrl('/?modo=buscar&q=frações')).toBe(`${SITE_ORIGIN}/?modo=buscar&q=frações`);
	});

	it('preserva URLs absolutas', () => {
		expect(absoluteUrl('https://www.buscabase.com.br/sobre')).toBe(
			'https://www.buscabase.com.br/sobre'
		);
	});
});

describe('truncateText', () => {
	it('não corta textos curtos', () => {
		expect(truncateText('frações', 60)).toBe('frações');
	});

	it('corta com reticências', () => {
		expect(truncateText('abcdefghijklmnopqrstuvwxyz', 10)).toBe('abcdefghi…');
	});
});

describe('HOME_TITLE', () => {
	it('usa o título atual da home', () => {
		expect(HOME_TITLE).toBe('Encontre o que você precisa na BNCC | Busca Base');
		expect(OG_IMAGE_ALT).toBe('Encontre o que você precisa na Base Nacional Comum Curricular');
		expect(DEFAULT_OG_IMAGE).toBe(`${SITE_ORIGIN}/og-default.png`);
	});
});

describe('socialPreview', () => {
	it('preenche imagem, tipo e locale padrão', () => {
		expect(
			socialPreview({
				title: 'Sobre o Busca Base | Busca Base',
				description: 'Projeto independente.',
				url: `${SITE_ORIGIN}/sobre`
			})
		).toEqual({
			title: 'Sobre o Busca Base | Busca Base',
			description: 'Projeto independente.',
			url: `${SITE_ORIGIN}/sobre`,
			image: DEFAULT_OG_IMAGE,
			type: 'website',
			locale: 'pt_BR'
		});
	});
});

describe('searchSharePreview', () => {
	it('título e descrição para código', () => {
		expect(searchSharePreview({ mode: 'codigo', codigo: 'EF05MA03' })).toEqual({
			title: 'EF05MA03 na BNCC | Busca Base',
			description: 'Consulte o texto de EF05MA03 na Base Nacional Comum Curricular.'
		});
	});

	it('título e descrição para busca, com recorte de consulta longa', () => {
		const q = 'a'.repeat(80);
		const preview = searchSharePreview({ mode: 'buscar', q, n: null });
		expect(preview.title).toBe(`Busca: ${'a'.repeat(59)}… | Busca Base`);
		expect(preview.description).toContain('Resultados da busca');
		expect(preview.description).toContain('na Base Nacional Comum Curricular.');
	});

	it('título e descrição para filtros', () => {
		expect(
			searchSharePreview({
				mode: 'filtros',
				etapas: ['EF'],
				anos: [],
				componentes: [],
				areas: [],
				campos: [],
				documentos: [],
				tipos: [],
				incluirRevogados: false,
				n: null
			})
		).toEqual({
			title: 'Consulta por filtros na BNCC | Busca Base',
			description: 'Itens da BNCC selecionados por etapa, ano, campo, área, componente ou documento.'
		});
	});

	it('título e descrição para perguntar, com a pergunta', () => {
		expect(searchSharePreview({ mode: 'perguntar', pergunta: 'O que é EF05MA03?' })).toEqual({
			title: 'O que é EF05MA03? | Busca Base',
			description:
				'Uma pergunta sobre o que a Base Nacional Comum Curricular diz: “O que é EF05MA03?”.'
		});
	});

	it('título genérico quando a pergunta está vazia', () => {
		expect(searchSharePreview({ mode: 'perguntar', pergunta: '' })).toEqual({
			title: 'Pergunta sobre a BNCC | Busca Base',
			description: 'Uma pergunta sobre o que a Base Nacional Comum Curricular diz.'
		});
	});
});
