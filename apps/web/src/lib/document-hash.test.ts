import { describe, expect, it } from 'vitest';
import { blockIdFromHash, pageFromSearchParams, parseProseBlockId } from '$lib/document-hash';

describe('parseProseBlockId', () => {
	it('lê página de bloco e figura', () => {
		expect(parseProseBlockId('bncc-2018-p297-b12')).toEqual({
			documentoId: 'bncc-2018',
			page: 297,
			kind: 'b',
			seq: 12
		});
		expect(parseProseBlockId('bncc-2018-p1-f3')).toEqual({
			documentoId: 'bncc-2018',
			page: 1,
			kind: 'f',
			seq: 3
		});
	});

	it('rejeita hash que não é bloco', () => {
		expect(parseProseBlockId('conversa=abc')).toBeNull();
		expect(parseProseBlockId('')).toBeNull();
	});
});

describe('blockIdFromHash', () => {
	it('aceita só id de bloco', () => {
		expect(blockIdFromHash('#bncc-2018-p297-b12')).toBe('bncc-2018-p297-b12');
		expect(blockIdFromHash('#conversa=abc')).toBeNull();
	});
});

describe('pageFromSearchParams', () => {
	it('lê pagina da query', () => {
		expect(pageFromSearchParams(new URLSearchParams('pagina=12'))).toBe(12);
		expect(pageFromSearchParams(new URLSearchParams(''))).toBe(1);
		expect(pageFromSearchParams(new URLSearchParams('pagina=abc'))).toBe(1);
	});
});
