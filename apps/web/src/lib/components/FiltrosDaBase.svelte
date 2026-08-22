<script lang="ts">
	import {
		appliedChips,
		formatAppliedCount,
		groupByEtapa,
		helpDependente,
		needsGrouping,
		nomeAno,
		pruneSelection,
		showsEiAxes,
		showsEscolarAxes,
		visibleAnos,
		visibleCampos,
		visibleComponentes,
		visibleForEtapas,
		visibleTipos,
		type AppliedChip,
		type AppliedKind,
		type FilterSelection
	} from '$lib/filters';
	import type { Snippet } from 'svelte';
	import type { Taxonomies, TaxOption } from '$lib/types';

	let {
		taxonomias,
		compact = false,
		etapas = $bindable<string[]>([]),
		anos = $bindable<string[]>([]),
		componentes = $bindable<string[]>([]),
		areas = $bindable<string[]>([]),
		campos = $bindable<string[]>([]),
		documentos = $bindable<string[]>([]),
		tipos = $bindable<string[]>([]),
		incluirRevogados = $bindable(false),
		onactivate
	}: {
		taxonomias: Taxonomies | null;
		compact?: boolean;
		onactivate?: () => void;
		etapas?: string[];
		anos?: string[];
		componentes?: string[];
		areas?: string[];
		campos?: string[];
		documentos?: string[];
		tipos?: string[];
		incluirRevogados?: boolean;
	} = $props();
	const uid = $props.id();

	let alterar = $state(false);
	let filtroComponente = $state('');
	let anuncio = $state('');

	const tax = $derived({
		etapas: taxonomias?.etapas || [],
		anos: taxonomias?.anos || [],
		componentes: taxonomias?.componentes || [],
		areas: taxonomias?.areas || [],
		campos: taxonomias?.campos || [],
		documentos: taxonomias?.documentos || [],
		tipos: taxonomias?.tipos || []
	});

	const etapasSelecionadas = $derived(tax.etapas.filter((etapa) => etapas.includes(etapa.id)));
	const temEtapa = $derived(etapasSelecionadas.length > 0);
	const mostrarEi = $derived(showsEiAxes(etapas));
	const mostrarEscolar = $derived(showsEscolarAxes(etapas));
	const compsSelecionados = $derived(tax.componentes.filter((comp) => componentes.includes(comp.id)));
	const anosSelecionados = $derived(tax.anos.filter((ano) => anos.includes(ano.id)));
	const anosVisiveis = $derived(visibleAnos(tax.anos, etapas, compsSelecionados));
	const areasVisiveis = $derived(visibleForEtapas(tax.areas, etapas));
	const componentesVisiveis = $derived(
		visibleComponentes(tax.componentes, etapas, areas, anosSelecionados)
	);
	const componentesListados = $derived(
		componentesVisiveis.filter((comp) =>
			comp.nome.toLowerCase().includes(filtroComponente.trim().toLowerCase())
		)
	);
	const camposVisiveis = $derived(visibleCampos(tax.campos, etapas));
	const tiposVisiveis = $derived(visibleTipos(tax.tipos, etapas));
	const gruposComponentes = $derived(groupByEtapa(componentesListados, tax.etapas));
	const gruposAreas = $derived(groupByEtapa(areasVisiveis, tax.etapas));
	const anosEi = $derived(anosVisiveis.filter((ano) => !ano.etapa || ano.etapa === 'EI'));
	const anosEscolares = $derived(anosVisiveis.filter((ano) => ano.etapa !== 'EI'));
	const gruposAnosEi = $derived(groupByEtapa(anosEi, tax.etapas));
	const gruposAnosEscolares = $derived(groupByEtapa(anosEscolares, tax.etapas));
	const agruparComponentes = $derived(needsGrouping(etapas.length, gruposComponentes.length));
	const agruparAreas = $derived(needsGrouping(etapas.length, gruposAreas.length));
	const agruparAnosEi = $derived(needsGrouping(etapas.length, gruposAnosEi.length));
	const agruparAnosEscolares = $derived(needsGrouping(etapas.length, gruposAnosEscolares.length));
	const buscarComponente = $derived(componentesVisiveis.length > 12);
	const mostrarEscolhas = $derived(!compact || alterar);
	const chips = $derived(
		appliedChips({
			etapas,
			anos,
			componentes,
			areas,
			campos,
			documentos,
			tipos,
			incluirRevogados,
			tax
		})
	);
	const ajudaAnos = $derived(helpDependente(etapasSelecionadas));
	const tituloRecorte = $derived(
		mostrarEi && !mostrarEscolar
			? 'Faixa e campo'
			: !mostrarEi && mostrarEscolar
				? 'Área, componente e ano'
				: 'Recorte da Base'
	);

	function currentSelection(): FilterSelection {
		return {
			etapas,
			anos,
			componentes,
			areas,
			campos,
			documentos,
			tipos,
			incluirRevogados
		};
	}

	function applySelection(next: FilterSelection) {
		etapas = next.etapas;
		anos = next.anos;
		componentes = next.componentes;
		areas = next.areas;
		campos = next.campos;
		documentos = next.documentos;
		tipos = next.tipos;
		incluirRevogados = next.incluirRevogados;
	}

	function sync(partial: Partial<FilterSelection>, message: string) {
		const before = currentSelection();
		const next = pruneSelection({ ...before, ...partial }, tax);
		applySelection(next);
		if (before.tipos.some((id) => !next.tipos.includes(id))) {
			anuncio = `${message} Tipos que não cabem neste recorte foram retirados.`;
			return;
		}
		anuncio = message;
	}

	function toggle(list: string[], id: string) {
		return list.includes(id) ? list.filter((item) => item !== id) : [...list, id];
	}

	function onEtapa(id: string) {
		const next = toggle(etapas, id);
		sync(
			{ etapas: next },
			next.length
				? 'As opções agora seguem as etapas escolhidas.'
				: 'Sem etapa, as opções de todas as etapas voltaram a aparecer.'
		);
	}

	function onArea(id: string) {
		const next = toggle(areas, id);
		sync(
			{ areas: next },
			next.length
				? 'Componentes agora seguem a área escolhida.'
				: 'Componentes de todas as áreas visíveis voltaram a aparecer.'
		);
	}

	function onAno(id: string) {
		sync({ anos: toggle(anos, id) }, 'Faixa ou ano atualizado.');
	}

	function onComponente(id: string) {
		sync({ componentes: toggle(componentes, id) }, 'Componente atualizado.');
	}

	function onCampo(id: string) {
		sync({ campos: toggle(campos, id) }, 'Campo de experiências atualizado.');
	}

	function onDocumento(id: string) {
		sync({ documentos: toggle(documentos, id) }, 'Documento atualizado.');
	}

	function onTipo(id: string) {
		sync({ tipos: toggle(tipos, id) }, 'Tipo de item atualizado.');
	}

	function removeChip(chip: AppliedChip) {
		const actions: Record<AppliedKind, () => void> = {
			etapa: () => onEtapa(chip.id),
			ano: () => onAno(chip.id),
			campo: () => onCampo(chip.id),
			componente: () => onComponente(chip.id),
			area: () => onArea(chip.id),
			documento: () => onDocumento(chip.id),
			tipo: () => onTipo(chip.id),
			revogados: () => (incluirRevogados = false)
		};
		actions[chip.kind]();
	}

	function limpar() {
		applySelection({
			etapas: [],
			anos: [],
			componentes: [],
			areas: [],
			campos: [],
			documentos: [],
			tipos: [],
			incluirRevogados: false
		});
		filtroComponente = '';
		anuncio = 'Filtros removidos.';
	}

	function renderGroups(
		groups: { id: string | null; nome: string; items: TaxOption[] }[],
		grouped: boolean
	): { nome: string | null; items: TaxOption[] }[] {
		if (!grouped) return [{ nome: null, items: groups.flatMap((group) => group.items) }];
		return groups.map((group) => ({ nome: group.nome, items: group.items }));
	}

	function stopEnter(event: KeyboardEvent) {
		if (event.key === 'Enter') event.preventDefault();
	}

	function stagePress(event: PointerEvent) {
		if (event.button) return;
		const details = (event.currentTarget as HTMLElement).closest('details');
		if (!details) return;
		event.preventDefault();
		details.open = !details.open;
		onactivate?.();
	}

	function escolhasLabel(n: number): string {
		if (n === 1) return '1 escolhida';
		return `${n} escolhidas`;
	}

	const escolhasEtapa = $derived(etapas.length);
	const escolhasRecorte = $derived(anos.length + campos.length + areas.length + componentes.length);
	const escolhasDocumento = $derived(documentos.length);
	const escolhasTipo = $derived(tipos.length + (incluirRevogados ? 1 : 0));
</script>

{#snippet choices(
	items: TaxOption[],
	selecionados: string[],
	onToggle: (id: string) => void,
	nomeCampo: string,
	rotulo?: (item: TaxOption) => string
)}
	<div class="filter-choices">
		{#each items as item (item.id)}
			<label class="filter-choice">
				<input
					type="checkbox"
					name={nomeCampo}
					value={item.id}
					checked={selecionados.includes(item.id)}
					onchange={() => onToggle(item.id)}
				/>
				{rotulo ? rotulo(item) : item.nome}
			</label>
		{/each}
	</div>
{/snippet}

{#snippet groupedChoices(
	groups: { id: string | null; nome: string; items: TaxOption[] }[],
	grouped: boolean,
	selecionados: string[],
	onToggle: (id: string) => void,
	nomeCampo: string,
	rotulo?: (item: TaxOption) => string
)}
	{#each renderGroups(groups, grouped) as group (group.nome ?? nomeCampo)}
		{#if group.items.length}
			{#if group.nome}
				<div class="filter-group" role="group" aria-label={group.nome}>
					<p class="filter-group-label">{group.nome}</p>
					{@render choices(group.items, selecionados, onToggle, nomeCampo, rotulo)}
				</div>
			{:else}
				{@render choices(group.items, selecionados, onToggle, nomeCampo, rotulo)}
			{/if}
		{/if}
	{/each}
{/snippet}

{#snippet etapaCorpo()}
	<p id="{uid}-ajuda-etapa" class="help">
		A etapa refina as listas abaixo. Você também pode buscar só por componente, documento ou tipo.
	</p>
	{@render choices(tax.etapas, etapas, onEtapa, 'etapa')}
{/snippet}

{#snippet recorteCorpo()}
	{#if mostrarEi && anosEi.length}
		<div class="filter-substep">
			<h4 class="filter-substep-title">Ano ou faixa</h4>
			<p id="{uid}-ajuda-anos-ei" class="help">{ajudaAnos}</p>
			{@render groupedChoices(gruposAnosEi, agruparAnosEi, anos, onAno, 'ano-ei', nomeAno)}
		</div>
	{/if}

	{#if mostrarEi && camposVisiveis.length}
		<div class="filter-substep">
			<h4 class="filter-substep-title">Campo de experiências</h4>
			<p class="help">A Educação Infantil se organiza por campos, não por componente.</p>
			{@render choices(camposVisiveis, campos, onCampo, 'campo')}
		</div>
	{/if}

	{#if mostrarEscolar && areasVisiveis.length}
		<div class="filter-substep">
			<h4 class="filter-substep-title">Área do conhecimento</h4>
			<p class="help">{helpDependente(etapasSelecionadas)}</p>
			{@render groupedChoices(gruposAreas, agruparAreas, areas, onArea, 'area')}
		</div>
	{/if}

	{#if mostrarEscolar && (componentesListados.length || filtroComponente.trim())}
		<div class="filter-substep">
			<h4 class="filter-substep-title">Componente curricular</h4>
			<p id="{uid}-ajuda-componente" class="help">{helpDependente(etapasSelecionadas)}</p>
			{#if buscarComponente}
				<div class="field">
					<label for="{uid}-filtro-componente">Reduzir lista de componentes</label>
					<input
						id="{uid}-filtro-componente"
						type="search"
						bind:value={filtroComponente}
						placeholder="Ex.: Matemática"
						onkeydown={stopEnter}
					/>
				</div>
			{/if}
			{#if componentesListados.length}
				{@render groupedChoices(
					gruposComponentes,
					agruparComponentes,
					componentes,
					onComponente,
					'componente'
				)}
			{:else if filtroComponente.trim()}
				<p class="help">Nenhum componente com esse nome na etapa visível.</p>
			{/if}
		</div>
	{/if}

	{#if mostrarEscolar && anosEscolares.length}
		<div class="filter-substep">
			<h4 class="filter-substep-title">Ano ou faixa</h4>
			<p id="{uid}-ajuda-anos" class="help">{ajudaAnos}</p>
			{@render groupedChoices(
				gruposAnosEscolares,
				agruparAnosEscolares,
				anos,
				onAno,
				'ano',
				nomeAno
			)}
		</div>
	{/if}
{/snippet}

{#snippet documentoCorpo()}
	<div class="filter-substep">
		<p class="help">Independente da etapa.</p>
		{@render choices(tax.documentos, documentos, onDocumento, 'documento')}
	</div>
{/snippet}

{#snippet tipoCorpo()}
	{#if tiposVisiveis.length}
		<div class="filter-substep">
			<h4 class="filter-substep-title">Tipo de item</h4>
			<p class="help">Use para ver só habilidades, objetivos de aprendizagem ou competências.</p>
			{@render choices(tiposVisiveis, tipos, onTipo, 'tipo')}
		</div>
	{/if}

	<div class="filter-substep">
		<h4 class="filter-substep-title">Vigência</h4>
		<p class="help">Itens revogados ficam de fora, salvo se você marcar esta opção.</p>
		<label class="filter-check">
			<input type="checkbox" bind:checked={incluirRevogados} />
			Incluir itens revogados
		</label>
	</div>
{/snippet}

{#snippet stage(id: string, indice: string, titulo: string, escolhas: number, marcado: boolean, corpo: Snippet)}
	<details class={['filter-stage', marcado && 'is-set']} data-stage={id}>
		<summary onpointerdown={stagePress}>
			<span class="filter-stage-index">{indice}</span>
			<span class="filter-stage-title">{titulo}</span>
			{#if escolhas}
				<span class="filter-stage-count">{escolhasLabel(escolhas)}</span>
			{/if}
		</summary>
		<div class="filter-step-body">
			{@render corpo()}
		</div>
	</details>
{/snippet}

<div class="filter-block">
	{#if chips.length}
		<div class="filter-applied">
			<p class="filter-applied-count">{formatAppliedCount(chips.length)}</p>
			<p class="help">Cada escolha pode ser retirada.</p>
			<ul class="filter-chips">
				{#each chips as chip (chip.key)}
					<li>
						<button
							class="chip"
							type="button"
							aria-label={chip.removeLabel}
							onclick={() => removeChip(chip)}
						>
							<span>{chip.label}</span>
							<span class="chip-remove">Remover</span>
						</button>
					</li>
				{/each}
			</ul>
			<button class="btn btn-tertiary" type="button" onclick={limpar}>Limpar filtros</button>
		</div>
	{:else if compact}
		<p class="help">Nenhuma escolha ainda. A etapa ajuda, mas não é obrigatória.</p>
	{/if}

	{#if compact}
		<button
			class="btn btn-secondary"
			type="button"
			aria-expanded={alterar}
			onclick={() => (alterar = !alterar)}
		>
			Alterar filtros
		</button>
	{/if}

	{#if mostrarEscolhas}
		<div class="filter-progress">
			{@render stage('etapa', '1', 'Etapa', escolhasEtapa, temEtapa, etapaCorpo)}
			{@render stage('recorte', '2', tituloRecorte, escolhasRecorte, escolhasRecorte > 0, recorteCorpo)}
			{@render stage('documento', '3', 'Documento', escolhasDocumento, escolhasDocumento > 0, documentoCorpo)}
			{@render stage('tipo', '4', 'Tipo e vigência', escolhasTipo, escolhasTipo > 0, tipoCorpo)}
		</div>
	{/if}

	<p class="visually-hidden" aria-live="polite">{anuncio}</p>
</div>
