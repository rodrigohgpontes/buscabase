import { describe, expect, it } from 'vitest';
import { conversationHistory } from '$lib/conversation-history';

describe('conversationHistory', () => {
	it('envia só texto nos turnos do usuário', () => {
		expect(
			conversationHistory([{ role: 'user', text: 'Explique EF05MA03 em palavras mais simples' }])
		).toEqual([
			{ role: 'user', content: 'Explique EF05MA03 em palavras mais simples' }
		]);
	});

	it('anexa códigos citados da resposta anterior', () => {
		expect(
			conversationHistory([
				{ role: 'user', text: 'Explique EF05MA03' },
				{
					role: 'assistant',
					text: 'A habilidade trata de frações [1].',
					citedSources: [
						{ item: { codigo: 'EF05MA03' } },
						{ item: { codigo: 'EF05MA03' } },
						{ item: { codigo: 'EF06MA01' } }
					]
				}
			])
		).toEqual([
			{ role: 'user', content: 'Explique EF05MA03' },
			{
				role: 'assistant',
				content: 'A habilidade trata de frações [1].',
				codigos: ['EF05MA03', 'EF06MA01']
			}
		]);
	});

	it('não envia código só presente em fonte de prosa', () => {
		expect(
			conversationHistory([
				{
					role: 'assistant',
					text: 'O parecer trata disso [1].',
					citedSources: [
						{
							kind: 'prose',
							item: { codigo: 'EF05MA99' }
						},
						{ kind: 'item', item: { codigo: 'EF05MA03' } }
					]
				}
			])
		).toEqual([
			{
				role: 'assistant',
				content: 'O parecer trata disso [1].',
				codigos: ['EF05MA03']
			}
		]);
	});
});
