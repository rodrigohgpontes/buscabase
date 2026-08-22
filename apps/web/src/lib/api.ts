import { env as publicEnv } from '$env/dynamic/public';
import { browser } from '$app/environment';
import type {
	Item,
	ProseDocumentMeta,
	ProsePagePayload,
	SearchResponse,
	SuggestionResponse,
	Taxonomies
} from '$lib/types';

export function apiBase(): string {
	if (browser) return '';
	return (
		publicEnv.PUBLIC_API_INTERNAL_URL ||
		(typeof process !== 'undefined' ? process.env.API_INTERNAL_URL : undefined) ||
		'http://api:8000'
	);
}

async function api<T>(path: string, init?: RequestInit): Promise<T> {
	const response = await fetch(`${apiBase()}${path}`, {
		...init,
		headers: { accept: 'application/json', ...(init?.headers || {}) }
	});
	if (!response.ok) {
		const body = (await response.json().catch(() => ({}))) as {
			detail?: { titulo?: string } | string;
			titulo?: string;
		};
		const titulo =
			(typeof body.detail === 'object' && body.detail && body.detail.titulo) ||
			body.titulo ||
			(typeof body.detail === 'string' ? body.detail : null) ||
			'Não foi possível concluir agora.';
		const error = new Error(titulo) as Error & {
			status: number;
			detail: unknown;
		};
		error.status = response.status;
		error.detail = body.detail ?? body;
		throw error;
	}
	return response.json() as Promise<T>;
}

export function getHealth() {
	return api<{ ok: boolean; recorte: string | null; perguntar: boolean; item_count: number }>(
		'/api/health'
	);
}

export function getTaxonomies() {
	return api<Taxonomies>('/api/taxonomias');
}

export function getSuggestions(q: string, limit = 5) {
	const params = new URLSearchParams({ q, limit: String(limit) });
	return api<SuggestionResponse>(`/api/sugestoes?${params}`);
}

export function getCodigo(codigo: string) {
	return api<Item>(`/api/codigos/${encodeURIComponent(codigo)}`);
}

export function search(params: URLSearchParams) {
	return api<SearchResponse>(`/api/buscar?${params.toString()}`);
}

export function getItem(codigo: string) {
	return api<Item>(`/api/items/${encodeURIComponent(codigo)}`);
}

export function getProseDocument(documentoId: string) {
	return api<ProseDocumentMeta>(`/api/prose/${encodeURIComponent(documentoId)}`);
}

export function getProsePage(documentoId: string, page: number) {
	return api<ProsePagePayload>(
		`/api/prose/${encodeURIComponent(documentoId)}/paginas/${page}`
	);
}

export function getDimensao(kind: string, slug: string) {
	return api<{
		id: string;
		nome: string;
		slug: string;
		tipo?: string | null;
		derivado_de?: string | null;
		payload?: Record<string, unknown> | null;
		items: Item[];
		recorte: string;
	}>(`/api/dimensao/${kind}/${slug}`);
}

export async function exportItems(codigos: string[], formato: 'txt' | 'csv') {
	const response = await fetch(`${apiBase()}/api/exportar`, {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify({ codigos, formato })
	});
	if (!response.ok) throw new Error('Não foi possível exportar os itens.');
	return response.blob();
}
