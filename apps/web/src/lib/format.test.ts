import { describe, expect, it } from 'vitest';
import {
	answerWithSourcesText,
	formatCount,
	formatSelectedCount,
	formatSelectedHint,
	previewCodigos
} from '$lib/format';
import type { CitedSource, Item } from '$lib/types';

describe('formatCount', () => {
	it('usa singular', () => {
		expect(formatCount(1)).toBe('1 resultado');
	});
	it('usa plural', () => {
		expect(formatCount(12)).toBe('12 resultados');
	});
});

describe('seleção para exportar', () => {
	it('deixa claro que a ação inclui todos os itens', () => {
		expect(formatSelectedCount(1)).toBe('1 item selecionado para exportar');
		expect(formatSelectedCount(3)).toBe('3 itens selecionados para exportar');
		expect(formatSelectedHint(1)).toBe('Copiar ou baixar inclui este item.');
		expect(formatSelectedHint(3)).toBe('Copiar ou baixar inclui todos os 3 itens.');
	});

	it('mostra um recorte dos códigos', () => {
		const preview = previewCodigos(
			[{ codigo: 'A' }, { codigo: 'B' }, { codigo: 'C' }, { codigo: 'D' }],
			2
		);
		expect(preview).toEqual({ codes: ['A', 'B'], extra: 2 });
	});
});

describe('answerWithSourcesText', () => {
	it('junta a resposta com as fontes numeradas', () => {
		const item = {
			codigo: 'EF05MA03',
			texto: 'Resolver problemas',
			metadados_linha: '5º ano · Matemática',
			pagina_pdf: null,
			recorte: 'dados-2026.07.1',
			permalink: 'https://www.buscabase.com.br/habilidade/EF05MA03'
		} as Item;
		const text = answerWithSourcesText('A Base trata disso em [1].', [
			{ n: 1, kind: 'item', item }
		]);
		expect(text).toContain('A Base trata disso em [1].');
		expect(text).toContain('Fontes');
		expect(text).toContain('[1] EF05MA03 — Resolver problemas');
		expect(text).toContain('https://www.buscabase.com.br/habilidade/EF05MA03');
	});

	it('copia fonte de prosa com página e aviso da reconstrução', () => {
		const source: CitedSource = {
			n: 1,
			kind: 'prose',
			documento_id: 'arte-2026',
			documento: 'Parecer CNE/CEB nº 2/2026',
			page: 4,
			block_id: 'arte-2026-p4-b2',
			type: 'paragraph',
			texto: 'A Arte na educação básica',
			url_path: '/documento/arte-2026#arte-2026-p4-b2'
		};
		const text = answerWithSourcesText('O parecer trata disso [1].', [source]);
		expect(text).toContain('Parecer CNE/CEB nº 2/2026, p. 4 — A Arte na educação básica');
		expect(text).toContain('reconstrução do PDF oficial');
		expect(text).toContain('https://www.buscabase.com.br/documento/arte-2026#arte-2026-p4-b2');
	});
});
