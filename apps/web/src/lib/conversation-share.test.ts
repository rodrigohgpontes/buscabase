import { describe, expect, it } from 'vitest';
import {
	conversaFromHash,
	conversationShareUrl,
	decodeConversation,
	encodeConversation,
	type SharedConversationTurn
} from '$lib/conversation-share';
import type { CitedSource, Item } from '$lib/types';

function sampleItem(codigo: string): Item {
	return {
		codigo,
		tipo: 'habilidade',
		tipo_label: 'Habilidade',
		texto: `Texto de ${codigo}`,
		etapa: 'EF',
		anos: [5],
		anos_label: '5º ano',
		componente: 'Matemática',
		area: 'Matemática',
		unidade_ou_campo: 'Números',
		objetos: [{ nome: 'Frações' }],
		documento: 'BNCC',
		documento_id: 'bncc',
		vigencia: { status: 'vigente' },
		fonte: {},
		pagina_pdf: 'p. 10',
		url_path: `/habilidade/${codigo}`,
		permalink: `https://www.buscabase.com.br/habilidade/${codigo}`,
		recorte: 'dados-2026.07.1',
		contexto_curto: '5º ano · Matemática',
		metadados_linha: '5º ano · Matemática · Números',
		nome_acessivel: `Habilidade ${codigo}`
	};
}

describe('conversation-share', () => {
	it('round-trip encode/decode preserva turnos e citações', async () => {
		const turns: SharedConversationTurn[] = [
			{ role: 'user', text: 'Explique frações no 5º ano' },
			{
				role: 'assistant',
				text: 'A Base trata disso em [1].',
				citedSources: [{ n: 1, kind: 'item', item: sampleItem('EF05MA03') }]
			}
		];
		const encoded = await encodeConversation(turns, 'dados-2026.07.1');
		const decoded = await decodeConversation(encoded);
		expect(decoded?.v).toBe(2);
		expect(decoded?.recorte).toBe('dados-2026.07.1');
		expect(decoded?.turns).toHaveLength(2);
		expect(decoded?.turns[1].citedSources?.[0].n).toBe(1);
		const cited = decoded?.turns[1].citedSources?.[0];
		expect(cited?.kind).toBe('item');
		expect(cited?.kind === 'item' && cited.item.codigo).toBe('EF05MA03');
		expect(decoded?.turns[1].text).toBe('A Base trata disso em [1].');
	});

	it('ignora payload corrompido', async () => {
		expect(await decodeConversation('isto-nao-e-valido')).toBeNull();
		expect(await decodeConversation('')).toBeNull();
	});

	it('lê conversa do hash', () => {
		expect(conversaFromHash('#conversa=abc')).toBe('abc');
		expect(conversaFromHash('conversa=abc&x=1')).toBe('abc');
		expect(conversaFromHash('#modo=perguntar')).toBeNull();
		expect(conversaFromHash('')).toBeNull();
	});

	it('monta URL de compartilhamento no hash', async () => {
		const url = await conversationShareUrl('https://www.buscabase.com.br', [
			{ role: 'user', text: 'Pergunta' },
			{ role: 'assistant', text: 'Resposta [1].', citedSources: [{ n: 1, kind: 'item', item: sampleItem('EF05MA03') }] }
		]);
		expect(url.startsWith('https://www.buscabase.com.br/?modo=perguntar#conversa=')).toBe(true);
		const encoded = conversaFromHash(url.slice(url.indexOf('#')));
		expect(encoded).toBeTruthy();
		const decoded = await decodeConversation(encoded as string);
		expect(decoded?.turns[0].text).toBe('Pergunta');
	});

	it('codifica sem travar mesmo com várias fontes', async () => {
		const turns: SharedConversationTurn[] = [
			{ role: 'user', text: 'Explique frações' },
			{
				role: 'assistant',
				text: 'Veja [1] e [2].',
				citedSources: [
					{ n: 1, kind: 'item', item: sampleItem('EF05MA03') },
					{ n: 2, kind: 'item', item: sampleItem('EF05MA04') }
				]
			}
		];
		await expect(encodeConversation(turns)).resolves.toMatch(/^[A-Za-z0-9_-]+$/);
	});

	it('aguenta um fio com quatro turnos curtos', async () => {
		const turns: SharedConversationTurn[] = [1, 2, 3, 4].flatMap((n) => [
			{ role: 'user' as const, text: `Pergunta ${n}` },
			{
				role: 'assistant' as const,
				text: `Resposta ${n} [1].`,
				citedSources: [{ n: 1, kind: 'item', item: sampleItem(`EF05MA0${n}`) }]
			}
		]);
		const encoded = await encodeConversation(turns);
		const decoded = await decodeConversation(encoded);
		expect(decoded?.turns).toHaveLength(8);
		expect(encoded.length).toBeLessThan(8000);
	});

	it('decodifica compartilhamento v1 só com itens', async () => {
		const payload = {
			v: 1,
			recorte: 'dados-2026.07.1',
			turns: [
				{ role: 'user', text: 'Explique frações' },
				{
					role: 'assistant',
					text: 'A Base trata disso [1].',
					citedSources: [{ n: 1, item: sampleItem('EF05MA03') }]
				}
			]
		};
		const json = new TextEncoder().encode(JSON.stringify(payload));
		const compressed = new Uint8Array(
			await new Response(
				new Blob([json]).stream().pipeThrough(new CompressionStream('deflate-raw'))
			).arrayBuffer()
		);
		let binary = '';
		for (const byte of compressed) binary += String.fromCharCode(byte);
		const encoded = btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
		const decoded = await decodeConversation(encoded);
		expect(decoded?.v).toBe(1);
		expect(decoded?.turns[1].citedSources?.[0].kind).toBe('item');
	});

	it('preserva fonte de prosa no v2', async () => {
		const prose: CitedSource = {
			n: 1,
			kind: 'prose',
			documento_id: 'arte-2026',
			documento: 'Parecer de Arte',
			page: 4,
			block_id: 'arte-2026-p4-b2',
			type: 'paragraph',
			texto: 'A Arte na educação básica',
			url_path: '/documento/arte-2026#arte-2026-p4-b2'
		};
		const encoded = await encodeConversation([
			{ role: 'user', text: 'O que o parecer diz?' },
			{ role: 'assistant', text: 'Trata de Arte [1].', citedSources: [prose] }
		]);
		const decoded = await decodeConversation(encoded);
		expect(decoded?.v).toBe(2);
		expect(decoded?.turns[1].citedSources?.[0]).toMatchObject({
			kind: 'prose',
			block_id: 'arte-2026-p4-b2',
			page: 4
		});
	});
});
