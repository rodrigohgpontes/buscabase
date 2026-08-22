import { describe, expect, it } from 'vitest';
import { parseTema, TEMA_ROTULOS } from '$lib/theme';

describe('parseTema', () => {
	it('reconhece Folia', () => {
		expect(parseTema('folia')).toBe('folia');
	});

	it('cai em Calma para qualquer outro valor', () => {
		expect(parseTema('calma')).toBe('calma');
		expect(parseTema(null)).toBe('calma');
		expect(parseTema('escuro')).toBe('calma');
	});
});

describe('rótulos', () => {
	it('nomeia as duas aparências sem hierarquia', () => {
		expect(TEMA_ROTULOS.calma).toBe('Calma');
		expect(TEMA_ROTULOS.folia).toBe('Folia');
	});
});
