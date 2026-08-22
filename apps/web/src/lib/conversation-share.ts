import type { CitedSource, FonteProse, Item } from '$lib/types';

export const CONVERSA_HASH_KEY = 'conversa';

export type SharedCitedSource = CitedSource;

export type SharedConversationTurn = {
	role: 'user' | 'assistant';
	text: string;
	citedSources?: SharedCitedSource[];
	incompleta?: boolean;
};

export type ConversationPayload = {
	v: 1 | 2;
	recorte: string | null;
	turns: SharedConversationTurn[];
};

const SLIM_KEYS = [
	'codigo',
	'tipo',
	'tipo_label',
	'texto',
	'etapa',
	'anos',
	'anos_label',
	'componente',
	'area',
	'unidade_ou_campo',
	'objetos',
	'documento',
	'documento_id',
	'vigencia',
	'fonte',
	'pagina_pdf',
	'url_path',
	'permalink',
	'recorte',
	'contexto_curto',
	'metadados_linha',
	'nome_acessivel'
] as const;

const PROSE_KEYS = [
	'kind',
	'documento_id',
	'documento',
	'page',
	'block_id',
	'type',
	'texto',
	'item_codigo',
	'url_path'
] as const;

function slimItem(item: Item): Item {
	const slim = {} as Item;
	for (const key of SLIM_KEYS) {
		(slim as Record<string, unknown>)[key] = item[key];
	}
	return slim;
}

function slimProse(source: FonteProse): FonteProse {
	const slim = {} as FonteProse;
	for (const key of PROSE_KEYS) {
		(slim as Record<string, unknown>)[key] = source[key];
	}
	return slim;
}

function slimCited(entry: SharedCitedSource): SharedCitedSource {
	if (entry.kind === 'prose') {
		return { ...slimProse(entry), n: entry.n };
	}
	return { n: entry.n, kind: 'item', item: slimItem(entry.item) };
}

function slimTurn(turn: SharedConversationTurn): SharedConversationTurn {
	return {
		role: turn.role,
		text: turn.text,
		incompleta: turn.incompleta,
		citedSources: turn.citedSources?.map(slimCited)
	};
}

function isRecord(value: unknown): value is Record<string, unknown> {
	return Boolean(value) && typeof value === 'object';
}

function normalizeCited(entry: unknown): SharedCitedSource | null {
	if (!isRecord(entry)) return null;
	const n = Number(entry.n);
	if (!Number.isFinite(n)) return null;
	if (entry.kind === 'prose' || (!entry.item && entry.block_id)) {
		if (typeof entry.block_id !== 'string' || typeof entry.documento !== 'string') return null;
		return {
			n,
			kind: 'prose',
			documento_id: String(entry.documento_id || ''),
			documento: entry.documento,
			page: Number(entry.page) || 0,
			block_id: entry.block_id,
			type: String(entry.type || 'paragraph'),
			texto: String(entry.texto || ''),
			item_codigo: typeof entry.item_codigo === 'string' ? entry.item_codigo : null,
			url_path: String(entry.url_path || '')
		};
	}
	if (!isRecord(entry.item) || typeof entry.item.codigo !== 'string') return null;
	return { n, kind: 'item', item: entry.item as Item };
}

function toBase64Url(bytes: Uint8Array): string {
	let binary = '';
	for (const byte of bytes) binary += String.fromCharCode(byte);
	return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

function fromBase64Url(encoded: string): Uint8Array {
	const padded = encoded.replace(/-/g, '+').replace(/_/g, '/');
	const pad = padded.length % 4 === 0 ? '' : '='.repeat(4 - (padded.length % 4));
	const binary = atob(padded + pad);
	const bytes = new Uint8Array(binary.length);
	for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
	return bytes;
}

async function transform(
	bytes: Uint8Array,
	stream: CompressionStream | DecompressionStream
): Promise<Uint8Array> {
	const input = new Blob([bytes.slice()]).stream();
	const output = input.pipeThrough(stream);
	return new Uint8Array(await new Response(output).arrayBuffer());
}

export async function encodeConversation(
	turns: SharedConversationTurn[],
	recorte: string | null = null
): Promise<string> {
	const payload: ConversationPayload = {
		v: 2,
		recorte,
		turns: turns.map(slimTurn)
	};
	const json = new TextEncoder().encode(JSON.stringify(payload));
	const compressed = await transform(json, new CompressionStream('deflate-raw'));
	return toBase64Url(compressed);
}

export async function decodeConversation(encoded: string): Promise<ConversationPayload | null> {
	try {
		const compressed = fromBase64Url(encoded.trim());
		const json = await transform(compressed, new DecompressionStream('deflate-raw'));
		const parsed = JSON.parse(new TextDecoder().decode(json)) as ConversationPayload;
		if ((parsed?.v !== 1 && parsed?.v !== 2) || !Array.isArray(parsed.turns)) return null;
		return {
			v: parsed.v,
			recorte: parsed.recorte ?? null,
			turns: parsed.turns.map((turn) => ({
				role: turn.role,
				text: turn.text,
				incompleta: turn.incompleta,
				citedSources: turn.citedSources
					?.map(normalizeCited)
					.filter((entry): entry is SharedCitedSource => entry !== null)
			}))
		};
	} catch {
		return null;
	}
}

export function conversaFromHash(hash: string): string | null {
	const raw = hash.startsWith('#') ? hash.slice(1) : hash;
	if (!raw) return null;
	return new URLSearchParams(raw).get(CONVERSA_HASH_KEY);
}

export async function conversationShareUrl(
	origin: string,
	turns: SharedConversationTurn[],
	recorte: string | null = null
): Promise<string> {
	const encoded = await encodeConversation(turns, recorte);
	const base = origin.replace(/\/$/, '');
	return `${base}/?modo=perguntar#${CONVERSA_HASH_KEY}=${encoded}`;
}
