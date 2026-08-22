import type { TaxOption, Taxonomies } from '$lib/types';

export type AppliedKind =
	| 'etapa'
	| 'ano'
	| 'campo'
	| 'area'
	| 'componente'
	| 'documento'
	| 'tipo'
	| 'revogados';

export type AppliedChip = {
	key: string;
	kind: AppliedKind;
	id: string;
	label: string;
	removeLabel: string;
};

export type FilterGroup<T> = {
	id: string | null;
	nome: string;
	items: T[];
};

export type FilterSelection = {
	etapas: string[];
	anos: string[];
	componentes: string[];
	areas: string[];
	campos: string[];
	documentos: string[];
	tipos: string[];
	incluirRevogados: boolean;
};

export type EmptyFilterReason = {
	titulo: string;
	texto: string;
};

const TIPO_EI = new Set(['objetivo', 'competencia_geral']);
const TIPO_EF_EM = new Set(['habilidade', 'competencia_geral', 'competencia_especifica']);
const FAIXAS_SEM_COMPUTACAO = new Set(['ei-grupo-01', 'ei-grupo-02']);

export function joinNomes(nomes: string[]): string {
	if (nomes.length <= 1) return nomes[0] || '';
	if (nomes.length === 2) return `${nomes[0]} e ${nomes[1]}`;
	return `${nomes.slice(0, -1).join(', ')} e ${nomes[nomes.length - 1]}`;
}

export function formatAppliedCount(n: number): string {
	if (n === 1) return '1 filtro aplicado';
	return `${n} filtros aplicados`;
}

export function etapaNome(etapas: TaxOption[], id: string | null | undefined): string {
	if (!id) return '';
	return etapas.find((etapa) => etapa.id === id)?.nome || id;
}

export function nomeAno(item: TaxOption): string {
	return item.faixa ? `${item.nome} (${item.faixa})` : item.nome;
}

export function hasFilterScope(selection: FilterSelection): boolean {
	return Boolean(
		selection.etapas.length ||
			selection.anos.length ||
			selection.componentes.length ||
			selection.areas.length ||
			selection.campos.length ||
			selection.documentos.length ||
			selection.tipos.length
	);
}

export function etapaFlags(etapas: string[]): { ei: boolean; escolar: boolean; onlyEI: boolean } {
	const ei = etapas.includes('EI');
	const escolar = etapas.includes('EF') || etapas.includes('EM');
	return { ei, escolar, onlyEI: ei && !escolar && etapas.every((id) => id === 'EI') };
}

export function showsEiAxes(etapas: string[]): boolean {
	return !etapas.length || etapas.includes('EI');
}

export function showsEscolarAxes(etapas: string[]): boolean {
	return !etapas.length || etapas.includes('EF') || etapas.includes('EM');
}

export function visibleForEtapas<T extends { etapa?: string | null }>(
	items: T[],
	etapas: string[]
): T[] {
	if (!etapas.length) return items;
	return items.filter((item) => !item.etapa || etapas.includes(item.etapa));
}

function recorteYears(item: TaxOption): number[] {
	return item.anos?.length ? item.anos : [];
}

function presencaAnos(item: TaxOption): number[] {
	return item.presenca?.anos?.length ? item.presenca.anos : [];
}

function yearSetsOverlap(left: number[], right: number[]): boolean {
	if (!left.length || !right.length) return false;
	return left.some((year) => right.includes(year));
}

export function visibleTipos(tipos: TaxOption[], etapas: string[]): TaxOption[] {
	if (!etapas.length) return tipos;
	const { ei, escolar, onlyEI } = etapaFlags(etapas);
	if (onlyEI) return tipos.filter((tipo) => TIPO_EI.has(tipo.id));
	if (escolar && !ei) return tipos.filter((tipo) => TIPO_EF_EM.has(tipo.id));
	return tipos;
}

export function visibleCampos(campos: TaxOption[], etapas: string[]): TaxOption[] {
	if (!showsEiAxes(etapas)) return [];
	return campos;
}

export function visibleAnos(
	anos: TaxOption[],
	etapas: string[],
	componentes: TaxOption[]
): TaxOption[] {
	let list = visibleForEtapas(anos, etapas);
	const restricted = componentes.filter((comp) => presencaAnos(comp).length);
	if (restricted.length && restricted.length === componentes.length && componentes.length) {
		const allowed = [...new Set(restricted.flatMap(presencaAnos))];
		list = list.filter((ano) => yearSetsOverlap(recorteYears(ano), allowed));
	}
	return list;
}

export function visibleComponentes(
	items: TaxOption[],
	etapas: string[],
	areas: string[],
	anos: TaxOption[] = []
): TaxOption[] {
	let list = visibleForEtapas(items, etapas).filter((item) => item.tem_aprendizagens !== false);
	if (areas.length) {
		list = list.filter((item) => Boolean(item.area) && areas.includes(item.area as string));
	}
	if (anos.length) {
		const yearValues = [...new Set(anos.flatMap(recorteYears))];
		const onlyEarlyEiFaixas =
			anos.length > 0 && anos.every((ano) => FAIXAS_SEM_COMPUTACAO.has(ano.id));
		list = list.filter((item) => {
			if (item.id === 'co-comp' && onlyEarlyEiFaixas) return false;
			const allowed = presencaAnos(item);
			if (!allowed.length) return true;
			return yearSetsOverlap(yearValues, allowed);
		});
	}
	return list;
}

export function keepAllowed<T extends { id: string }>(selected: string[], allowed: T[]): string[] {
	const ids = new Set(allowed.map((item) => item.id));
	return selected.filter((id) => ids.has(id));
}

export function groupByEtapa<T extends { etapa?: string | null }>(
	items: T[],
	etapas: TaxOption[]
): FilterGroup<T>[] {
	const groups: FilterGroup<T>[] = [];
	for (const etapa of etapas) {
		const list = items.filter((item) => item.etapa === etapa.id);
		if (list.length) groups.push({ id: etapa.id, nome: etapa.nome, items: list });
	}
	const rest = items.filter((item) => !item.etapa);
	if (rest.length) groups.push({ id: null, nome: 'Complementos', items: rest });
	return groups;
}

export function needsGrouping(etapasSelecionadas: number, groupCount: number): boolean {
	return etapasSelecionadas !== 1 && groupCount > 1;
}

export function nomeComContexto(
	item: TaxOption,
	todos: TaxOption[],
	etapas: TaxOption[]
): string {
	const ambiguo = todos.filter((outro) => outro.nome === item.nome).length > 1;
	if (!ambiguo) return item.nome;
	const etapa = etapaNome(etapas, item.etapa);
	return etapa ? `${item.nome} · ${etapa}` : item.nome;
}

export function helpDependente(selecionadas: TaxOption[]): string {
	if (!selecionadas.length) {
		return 'Depende da etapa. Sem etapa, as opções aparecem agrupadas.';
	}
	if (selecionadas.length === 1) {
		return `Mostrando opções de ${selecionadas[0].nome}.`;
	}
	return `Mostrando opções de ${joinNomes(selecionadas.map((etapa) => etapa.nome))}.`;
}

export function pruneSelection(selection: FilterSelection, tax: Taxonomies): FilterSelection {
	const etapas = selection.etapas.filter((id) => tax.etapas.some((etapa) => etapa.id === id));
	const areasVisiveis = visibleForEtapas(tax.areas, etapas);
	const areas = keepAllowed(selection.areas, areasVisiveis);
	const anosSelecionados = tax.anos.filter((ano) => selection.anos.includes(ano.id));
	const componentesVisiveis = visibleComponentes(tax.componentes, etapas, areas, anosSelecionados);
	const componentes = keepAllowed(selection.componentes, componentesVisiveis);
	const compsSelecionados = tax.componentes.filter((comp) => componentes.includes(comp.id));
	const anos = keepAllowed(selection.anos, visibleAnos(tax.anos, etapas, compsSelecionados));
	const campos = keepAllowed(selection.campos, visibleCampos(tax.campos || [], etapas));
	const documentos = keepAllowed(selection.documentos, tax.documentos);
	const tipos = keepAllowed(selection.tipos, visibleTipos(tax.tipos, etapas));
	return {
		etapas,
		anos,
		componentes,
		areas,
		campos,
		documentos,
		tipos,
		incluirRevogados: selection.incluirRevogados
	};
}

export function emptyFilterReason(
	selection: FilterSelection,
	tax: Taxonomies
): EmptyFilterReason {
	const { onlyEI } = etapaFlags(selection.etapas);
	if (onlyEI && selection.tipos.includes('habilidade')) {
		return {
			titulo: 'Não encontramos resultados para este recorte.',
			texto: 'Educação Infantil se organiza por objetivos de aprendizagem, não por habilidades.'
		};
	}
	if ((selection.etapas.includes('EF') || selection.etapas.includes('EM')) && !selection.etapas.includes('EI') && selection.tipos.includes('objetivo')) {
		return {
			titulo: 'Não encontramos resultados para este recorte.',
			texto: 'Objetivos de aprendizagem e desenvolvimento pertencem à Educação Infantil.'
		};
	}
	const ingles = tax.componentes.find(
		(comp) =>
			selection.componentes.includes(comp.id) &&
			(comp.sigla === 'LI' || /ingl[eê]sa/i.test(comp.nome))
	);
	const inglesAnos = ingles ? presencaAnos(ingles) : [];
	if (ingles && inglesAnos.length) {
		const fora = selection.anos.some((id) => {
			const ano = tax.anos.find((item) => item.id === id);
			const years = ano ? recorteYears(ano) : [];
			return years.length > 0 && !yearSetsOverlap(years, inglesAnos);
		});
		if (fora) {
			return {
				titulo: 'Não encontramos resultados para este recorte.',
				texto: 'Língua Inglesa na Base começa no 6º ano.'
			};
		}
	}
	const semItens = tax.componentes.find(
		(comp) => selection.componentes.includes(comp.id) && comp.tem_aprendizagens === false
	);
	if (semItens) {
		const area = tax.areas.find((item) => item.id === semItens.area);
		return {
			titulo: 'Não encontramos resultados para este recorte.',
			texto: area
				? `Este componente não tem itens próprios na Base; use a área ${area.nome}.`
				: 'Este componente não tem itens próprios na Base.'
		};
	}
	return {
		titulo: 'Não encontramos resultados para este recorte.',
		texto: 'Tente outro recorte ou retire a última escolha.'
	};
}

export function appliedChips(input: {
	etapas: string[];
	anos: string[];
	componentes: string[];
	areas: string[];
	campos?: string[];
	documentos?: string[];
	tipos: string[];
	incluirRevogados: boolean;
	tax: {
		etapas: TaxOption[];
		anos: TaxOption[];
		componentes: TaxOption[];
		areas: TaxOption[];
		campos?: TaxOption[];
		documentos?: TaxOption[];
		tipos: TaxOption[];
	};
}): AppliedChip[] {
	const chips: AppliedChip[] = [];
	const push = (kind: AppliedKind, id: string, label: string) => {
		chips.push({
			key: `${kind}:${id}`,
			kind,
			id,
			label,
			removeLabel: `Remover filtro ${label}`
		});
	};

	for (const id of input.etapas) {
		const item = input.tax.etapas.find((etapa) => etapa.id === id);
		if (item) push('etapa', id, item.nome);
	}
	for (const id of input.anos) {
		const item = input.tax.anos.find((ano) => ano.id === id);
		if (item) push('ano', id, nomeAno(item));
	}
	for (const id of input.campos || []) {
		const item = (input.tax.campos || []).find((campo) => campo.id === id);
		if (item) push('campo', id, item.nome);
	}
	for (const id of input.areas) {
		const item = input.tax.areas.find((area) => area.id === id);
		if (item) push('area', id, nomeComContexto(item, input.tax.areas, input.tax.etapas));
	}
	for (const id of input.componentes) {
		const item = input.tax.componentes.find((comp) => comp.id === id);
		if (item) push('componente', id, nomeComContexto(item, input.tax.componentes, input.tax.etapas));
	}
	for (const id of input.documentos || []) {
		const item = (input.tax.documentos || []).find((doc) => doc.id === id);
		if (item) push('documento', id, item.nome);
	}
	for (const id of input.tipos) {
		const item = input.tax.tipos.find((tipo) => tipo.id === id);
		if (item) push('tipo', id, item.nome);
	}
	if (input.incluirRevogados) {
		push('revogados', 'revogados', 'Itens revogados');
	}
	return chips;
}
