import { describe, expect, it } from 'vitest';
import { shareItemText, shareSearchText, shareTargets } from '$lib/share';

describe('share texts', () => {
	it('usa textos sóbrios em português', () => {
		expect(shareSearchText()).toBe('Consulta na BNCC no Busca Base');
		expect(shareItemText('EF05MA03')).toBe('EF05MA03 na BNCC — Busca Base');
	});
});

describe('shareTargets', () => {
	const url = 'https://www.buscabase.com.br/?modo=buscar&q=fra%C3%A7%C3%B5es';
	const text = 'Consulta na BNCC no Busca Base';

	it('monta links codificados para WhatsApp, LinkedIn, Telegram e e-mail', () => {
		const targets = shareTargets(url, text);
		expect(targets.map((t) => t.id)).toEqual(['whatsapp', 'linkedin', 'telegram', 'email']);

		const byId = Object.fromEntries(targets.map((t) => [t.id, t.href]));
		expect(byId.whatsapp).toBe(
			`https://wa.me/?text=${encodeURIComponent(`${text}\n${url}`)}`
		);
		expect(byId.linkedin).toBe(
			`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`
		);
		expect(byId.telegram).toBe(
			`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`
		);
		expect(byId.email).toBe(
			`mailto:?subject=${encodeURIComponent(text)}&body=${encodeURIComponent(`${text}\n${url}`)}`
		);
	});
});
