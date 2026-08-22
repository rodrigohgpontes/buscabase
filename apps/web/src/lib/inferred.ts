import type { InferredChip } from '$lib/types';

export function escapeRegExp(value: string): string {
	return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export function stripInferredPhrase(query: string, phrase: string): string {
	if (!phrase.trim()) return query.trim();
	const pattern = new RegExp(escapeRegExp(phrase.trim()), 'gi');
	return query.replace(pattern, ' ').replace(/\s+/g, ' ').trim();
}

export function chipRemoveLabel(chip: InferredChip): string {
	return `Remover recorte ${chip.label}`;
}
