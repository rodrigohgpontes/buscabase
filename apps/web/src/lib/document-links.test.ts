import { describe, expect, it } from 'vitest';
import { officialDocumentLinks } from './document-links';

describe('officialDocumentLinks', () => {
	it('devolve o PDF homologado da BNCC', () => {
		const links = officialDocumentLinks('bncc-2018');
		expect(links).toHaveLength(1);
		expect(links[0].href).toContain('basenacionalcomum.mec.gov.br');
		expect(links[0].href).toMatch(/\.pdf$/);
	});

	it('devolve o anexo, o parecer e a resolução de Computação', () => {
		const labels = officialDocumentLinks('computacao-2022').map((link) => link.label);
		expect(labels).toEqual([
			'Anexo ao Parecer CNE/CEB nº 2/2022',
			'Parecer CNE/CEB nº 2/2022',
			'Resolução CNE/CEB nº 1/2022'
		]);
		expect(officialDocumentLinks('computacao-2022').every((link) => link.href.includes('gov.br'))).toBe(
			true
		);
	});

	it('devolve o parecer de Arte', () => {
		const links = officialDocumentLinks('arte-2026');
		expect(links).toHaveLength(1);
		expect(links[0].href).toBe('https://www.gov.br/mec/pt-br/cne/2026/marco-2026/pceb002_26.pdf');
	});

	it('não inventa link para documento desconhecido', () => {
		expect(officialDocumentLinks('inexistente')).toEqual([]);
		expect(officialDocumentLinks(null)).toEqual([]);
	});
});
