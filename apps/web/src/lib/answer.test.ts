import { describe, expect, it } from 'vitest';
import {
	citationNumbers,
	citedSources,
	normalizeCitations,
	parseAnswer,
	snippetText
} from '$lib/answer';

describe('parseAnswer', () => {
	it('parseia parágrafos, negrito e citações', () => {
		const blocks = parseAnswer(
			'A Base define **leitura** no 5º ano [1].\n\nEla também trata de escrita [2].'
		);
		expect(blocks).toHaveLength(2);
		expect(blocks[0]).toEqual({
			type: 'paragraph',
			parts: [
				{ type: 'text', text: 'A Base define ' },
				{ type: 'bold', text: 'leitura' },
				{ type: 'text', text: ' no 5º ano ' },
				{ type: 'citation', n: 1 },
				{ type: 'text', text: '.' }
			]
		});
	});

	it('converte listas e títulos em blocos legíveis', () => {
		const blocks = parseAnswer(
			'## Comparação\n\n- No 5º ano [1]\n- No 6º ano [2]\n\n1. Primeiro ponto\n2. Segundo ponto'
		);
		expect(blocks[0]).toEqual({ type: 'heading', text: 'Comparação' });
		expect(blocks[1]).toMatchObject({ type: 'list', ordered: false });
		expect(blocks[1].type === 'list' && blocks[1].items).toHaveLength(2);
		expect(blocks[2]).toMatchObject({ type: 'list', ordered: true });
	});

	it('ignora texto vazio', () => {
		expect(parseAnswer('')).toEqual([]);
		expect(parseAnswer('   ')).toEqual([]);
	});
});

describe('snippetText', () => {
	it('corta com reticências', () => {
		expect(snippetText('abc', 10)).toBe('abc');
		expect(snippetText('a'.repeat(20), 10)).toBe('aaaaaaaaa…');
	});
});

describe('citationNumbers', () => {
	it('lista números únicos em ordem', () => {
		expect(citationNumbers('Ver [2] e [1] e [2].')).toEqual([1, 2]);
	});
});

describe('normalizeCitations', () => {
	it('renumerar para [1]… e filtra fontes não citadas', () => {
		const sources = [
			{ codigo: 'A' },
			{ codigo: 'B' },
			{ codigo: 'C' },
			{ codigo: 'D' },
			{ codigo: 'E' },
			{ codigo: 'F' }
		];
		const result = normalizeCitations('A Base trata disso em [6].', sources);
		expect(result.text).toBe('A Base trata disso em [1].');
		expect(result.sources).toEqual([{ n: 1, codigo: 'F' }]);
	});

	it('preserva a ordem de primeira aparição', () => {
		const sources = [{ codigo: 'A' }, { codigo: 'B' }, { codigo: 'C' }];
		const result = normalizeCitations('Compara [3] com [1] e de novo [3].', sources);
		expect(result.text).toBe('Compara [1] com [2] e de novo [1].');
		expect(result.sources).toEqual([
			{ n: 1, codigo: 'C' },
			{ n: 2, codigo: 'A' }
		]);
	});

	it('citedSources devolve só a lista renumerada', () => {
		const sources = [{ codigo: 'A' }, { codigo: 'B' }, { codigo: 'C' }];
		expect(citedSources('Só [3].', sources)).toEqual([{ n: 1, codigo: 'C' }]);
		expect(citedSources('Sem nota.', sources)).toEqual([]);
	});

	it('preserva fontes discriminadas de prosa', () => {
		const sources = [
			{ kind: 'item' as const, item: { codigo: 'EF05MA03' } },
			{ kind: 'prose' as const, block_id: 'arte-2026-p4-b2', documento: 'Arte', page: 4 }
		];
		const result = normalizeCitations('O parecer trata disso [2].', sources);
		expect(result.text).toBe('O parecer trata disso [1].');
		expect(result.sources).toEqual([
			{ n: 1, kind: 'prose', block_id: 'arte-2026-p4-b2', documento: 'Arte', page: 4 }
		]);
	});
});
