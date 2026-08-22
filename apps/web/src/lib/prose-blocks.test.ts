import { describe, expect, it } from 'vitest';
import { groupProseBlocks, headingTag, isChromeType } from '$lib/prose-blocks';
import type { ProseBlock } from '$lib/types';

function block(id: string, type: string, text = 'texto'): ProseBlock {
	return { id, type, text, page: 1, seq: 1 };
}

describe('groupProseBlocks', () => {
	it('agrupa itens de lista e células de tabela', () => {
		const groups = groupProseBlocks([
			block('a', 'paragraph'),
			block('b', 'list_item'),
			block('c', 'list_item'),
			block('d', 'table_header'),
			block('e', 'table_cell')
		]);
		expect(groups[0]).toEqual({ kind: 'single', block: block('a', 'paragraph') });
		expect(groups[1].kind).toBe('list');
		expect(groups[1].kind === 'list' && groups[1].blocks).toHaveLength(2);
		expect(groups[2].kind).toBe('table');
	});
});

describe('headingTag', () => {
	it('mapeia tipos sem segundo h1', () => {
		expect(headingTag('heading_1')).toBe('h2');
		expect(headingTag('heading_2')).toBe('h3');
		expect(headingTag('card')).toBe('article');
		expect(headingTag('paragraph')).toBe('p');
	});
});

describe('isChromeType', () => {
	it('marca cabeçalho, rodapé e número de página', () => {
		expect(isChromeType('running_header')).toBe(true);
		expect(isChromeType('page_number')).toBe(true);
		expect(isChromeType('paragraph')).toBe(false);
	});
});
