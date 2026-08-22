import { sequence } from '@sveltejs/kit/hooks';
import { env } from '$env/dynamic/private';
import type { Handle, HandleServerError } from '@sveltejs/kit';
import { apiBase } from '$lib/api';
import { deviceClass, pageClass, referrerHost, shouldRecordPage, usoGuard } from '$lib/usage';

const security: Handle = async ({ event, resolve }) => {
	const uso = usoGuard(env.USO_PASSWORD, env.USO_USER, event.request.headers.get('authorization'));
	if (event.url.pathname.startsWith('/uso')) {
		if (uso === 404) {
			return new Response('Não encontrado.', {
				status: 404,
				headers: { 'X-Robots-Tag': 'noindex, nofollow' }
			});
		}
		if (uso === 401) {
			return new Response('Autenticação necessária.', {
				status: 401,
				headers: {
					'WWW-Authenticate': 'Basic realm="Busca Base"',
					'X-Robots-Tag': 'noindex, nofollow'
				}
			});
		}
	}
	const response = await resolve(event, {
		preload: ({ type }) => type === 'js' || type === 'css' || type === 'font'
	});
	response.headers.set('X-Content-Type-Options', 'nosniff');
	response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
	response.headers.set('X-Frame-Options', 'DENY');
	recordPage(event);
	return response;
};

function recordPage(event: Parameters<Handle>[0]['event']) {
	if (event.isDataRequest) return;
	if (!shouldRecordPage(event.url.pathname)) return;
	const accept = event.request.headers.get('accept') || '';
	if (!accept.includes('text/html')) return;
	const ua = event.request.headers.get('user-agent');
	const referer = event.request.headers.get('referer');
	const payload = {
		kind: 'page',
		page_class: pageClass(event.url.pathname, event.url.searchParams),
		referrer_host: referrerHost(referer, event.url.hostname),
		device: deviceClass(ua)
	};
	const forwarded = event.request.headers.get('x-forwarded-for') || event.getClientAddress();
	fetch(`${apiBase()}/api/eventos`, {
		method: 'POST',
		headers: {
			'content-type': 'application/json',
			'user-agent': ua || '',
			'x-forwarded-for': forwarded,
			referer: referer || ''
		},
		body: JSON.stringify(payload),
		signal: AbortSignal.timeout(200)
	}).catch(() => {});
}

export const handle = sequence(security);

export const handleError: HandleServerError = ({ status }) => {
	if (status === 404) {
		return {
			message: 'Não encontramos esta página.',
			titulo: 'Página não encontrada',
			texto: 'Ela pode ter mudado de endereço ou ainda não estar no recorte atual.'
		};
	}
	return {
		message: 'Não foi possível concluir agora.',
		titulo: 'Não foi possível concluir agora',
		texto: 'Sua consulta foi preservada. Tente novamente ou volte à busca.'
	};
};
