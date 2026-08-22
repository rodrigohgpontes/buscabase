export const TEMA_STORAGE_KEY = 'buscabase-tema';

export const TEMAS = ['calma', 'folia'] as const;

export type Tema = (typeof TEMAS)[number];

export const TEMA_ROTULOS: Record<Tema, string> = {
	calma: 'Calma',
	folia: 'Folia'
};

export const TEMA_COR_BARRA: Record<Tema, string> = {
	calma: '#185C37',
	folia: '#0A6E38'
};

export function parseTema(value: string | null | undefined): Tema {
	return value === 'folia' ? 'folia' : 'calma';
}

export function lerTemaDoDocumento(): Tema {
	if (typeof document === 'undefined') return 'calma';
	return parseTema(document.documentElement.getAttribute('data-theme'));
}

export const EVENTO_FOLIA = 'buscabase:folia';

export function aplicarTema(tema: Tema) {
	if (typeof document === 'undefined') return;
	const jaEraFolia = document.documentElement.getAttribute('data-theme') === 'folia';
	if (tema === 'folia') {
		document.documentElement.setAttribute('data-theme', 'folia');
	} else {
		document.documentElement.removeAttribute('data-theme');
	}
	if (tema === 'folia' && !jaEraFolia) {
		window.dispatchEvent(new Event(EVENTO_FOLIA));
	}
	try {
		localStorage.setItem(TEMA_STORAGE_KEY, tema);
	} catch {
		/* navegação privada ou armazenamento bloqueado */
	}
	const meta = document.querySelector('meta[name="theme-color"]');
	if (meta) meta.setAttribute('content', TEMA_COR_BARRA[tema]);
}
