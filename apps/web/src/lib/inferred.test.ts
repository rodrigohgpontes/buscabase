import { describe, expect, it } from 'vitest';
import { stripInferredPhrase } from '$lib/inferred';

describe('stripInferredPhrase', () => {
	it('tira o componente e deixa o ano', () => {
		expect(stripInferredPhrase('geografia no 5º ano', 'geografia')).toBe('no 5º ano');
	});

	it('tira o ano e deixa o componente', () => {
		expect(stripInferredPhrase('geografia no 5º ano', '5º ano')).toBe('geografia no');
	});
});
