import { absoluteUrl } from '$lib/social';
import type { CitedSource, Item } from '$lib/types';

export function referenceText(item: Item): string {
	const fonte = item.pagina_pdf ? `, ${item.pagina_pdf}` : '';
	return [
		`${item.codigo} — ${item.texto}`,
		item.metadados_linha,
		`Fonte: Base Nacional Comum Curricular${fonte}. Recorte ${item.recorte}.`,
		item.permalink
	].join('\n');
}

export function referenceFonte(source: CitedSource): string {
	if (source.kind === 'prose') {
		const href = source.url_path.startsWith('http')
			? source.url_path
			: absoluteUrl(source.url_path);
		return [
			`${source.documento}, p. ${source.page} — ${source.texto}`,
			'Fonte: reconstrução do PDF oficial. Vale o documento homologado.',
			href
		].join('\n');
	}
	return referenceText(source.item);
}

export function formatCount(n: number): string {
	if (n === 1) return '1 resultado';
	const formatted = n.toLocaleString('pt-BR');
	if (n > 100) return `Mais de 100 resultados. Use os filtros para reduzir a lista.`;
	return `${formatted} resultados`;
}

export function formatSelectedCount(n: number): string {
	if (n === 1) return '1 item selecionado para exportar';
	return `${n} itens selecionados para exportar`;
}

export function formatSelectedHint(n: number): string {
	if (n === 1) return 'Copiar ou baixar inclui este item.';
	return `Copiar ou baixar inclui todos os ${n} itens.`;
}

export function previewCodigos(
	items: { codigo: string }[],
	max = 8
): { codes: string[]; extra: number } {
	return {
		codes: items.slice(0, max).map((item) => item.codigo),
		extra: Math.max(0, items.length - max)
	};
}

export function answerWithSourcesText(answer: string, cited: CitedSource[]): string {
	const parts = [answer.trim()];
	if (cited.length) {
		parts.push('', 'Fontes');
		for (const entry of cited) {
			parts.push('', `[${entry.n}] ${referenceFonte(entry)}`);
		}
	}
	return parts.join('\n');
}
