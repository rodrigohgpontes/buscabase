export type PageClass =
	| 'home'
	| 'home_consulta'
	| 'habilidade'
	| 'indices'
	| 'documento'
	| 'dimensao'
	| 'institucional'
	| 'outro';

export type UsageDevice = 'mobile' | 'desktop' | 'bot';

const BOT_RE = /bot|crawler|spider|slurp|facebookexternalhit|preview|linkedinbot|twitterbot|bingpreview/i;
const MOBILE_RE = /Mobile|Android|iPhone|iPad|iPod/i;

const SKIP_PATHS = new Set(['/robots.txt', '/sitemap.xml', '/llms.txt']);

export function pageClass(pathname: string, search: URLSearchParams): PageClass {
	if (pathname === '/') {
		return search.get('modo') ? 'home_consulta' : 'home';
	}
	if (pathname.startsWith('/habilidade/') || pathname.startsWith('/aprendizagem/')) {
		return 'habilidade';
	}
	if (pathname === '/indices') return 'indices';
	if (pathname.startsWith('/documento/')) return 'documento';
	if (
		pathname.startsWith('/etapa/') ||
		pathname.startsWith('/ano/') ||
		pathname.startsWith('/area/') ||
		pathname.startsWith('/componente/') ||
		pathname.startsWith('/competencia/')
	) {
		return 'dimensao';
	}
	if (pathname === '/sobre' || pathname === '/privacidade' || pathname === '/acessibilidade') {
		return 'institucional';
	}
	return 'outro';
}

export function shouldRecordPage(pathname: string): boolean {
	if (pathname.startsWith('/uso') || pathname.startsWith('/api') || pathname.startsWith('/sitemaps')) {
		return false;
	}
	return !SKIP_PATHS.has(pathname);
}

export function deviceClass(userAgent: string | null | undefined): UsageDevice {
	if (!userAgent) return 'desktop';
	if (BOT_RE.test(userAgent)) return 'bot';
	if (MOBILE_RE.test(userAgent)) return 'mobile';
	return 'desktop';
}

export function referrerHost(value: string | null | undefined, originHost = ''): string | undefined {
	if (!value) return undefined;
	const raw = value.trim();
	if (!raw || raw.toLowerCase() === 'direct') return 'direct';
	try {
		const url = new URL(raw.includes('://') ? raw : `https://${raw}`);
		let host = url.hostname.toLowerCase();
		if (host.startsWith('www.')) host = host.slice(4);
		let origin = originHost.toLowerCase();
		if (origin.startsWith('www.')) origin = origin.slice(4);
		if (!host || host === origin || host === 'localhost' || host === '127.0.0.1') return undefined;
		return host;
	} catch {
		return undefined;
	}
}

export function recordClientEvent(body: {
	kind: 'copy' | 'share';
	copy_kind?: 'texto' | 'texto_e_referencia' | 'link';
	mode?: 'codigo' | 'filtros' | 'buscar' | 'perguntar';
	codigo?: string;
}) {
	if (typeof fetch === 'undefined') return;
	fetch('/api/eventos', {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify(body),
		keepalive: true
	}).catch(() => {});
}

export function usoGuard(
	password: string | undefined,
	user: string | undefined,
	authorization: string | null
): 404 | 401 | 200 {
	if (!password) return 404;
	const expectedUser = user || 'uso';
	if (!authorization || !authorization.startsWith('Basic ')) return 401;
	let decoded = '';
	try {
		decoded = atob(authorization.slice(6));
	} catch {
		return 401;
	}
	const idx = decoded.indexOf(':');
	if (idx < 0) return 401;
	if (decoded.slice(0, idx) !== expectedUser || decoded.slice(idx + 1) !== password) return 401;
	return 200;
}
