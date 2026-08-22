export type ParsedProseBlockId = {
	documentoId: string;
	page: number;
	kind: 'b' | 'f';
	seq: number;
};

const BLOCK_ID_RE = /^(?<documentoId>[a-z0-9-]+)-p(?<page>\d+)-(?<kind>[bf])(?<seq>\d+)$/i;

export function parseProseBlockId(raw: string): ParsedProseBlockId | null {
	const value = (raw || '').trim();
	const match = BLOCK_ID_RE.exec(value);
	if (!match?.groups) return null;
	const page = Number(match.groups.page);
	const seq = Number(match.groups.seq);
	if (!Number.isFinite(page) || page < 1) return null;
	return {
		documentoId: match.groups.documentoId,
		page,
		kind: match.groups.kind.toLowerCase() as 'b' | 'f',
		seq
	};
}

export function blockIdFromHash(hash: string): string | null {
	const raw = hash.startsWith('#') ? hash.slice(1) : hash;
	if (!raw || raw.includes('=')) return null;
	return parseProseBlockId(raw) ? raw : null;
}

export function pageFromSearchParams(params: URLSearchParams, fallback = 1): number {
	const raw = params.get('pagina');
	const page = raw ? Number(raw) : fallback;
	if (!Number.isFinite(page) || page < 1) return fallback;
	return Math.floor(page);
}
