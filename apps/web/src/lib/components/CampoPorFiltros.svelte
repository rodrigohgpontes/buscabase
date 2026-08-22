<script lang="ts">
	import FiltrosDaBase from '$lib/components/FiltrosDaBase.svelte';
	import PainelDeModo from '$lib/components/PainelDeModo.svelte';
	import { hasFilterScope } from '$lib/filters';
	import type { Taxonomies } from '$lib/types';

	let {
		open = true,
		compact = false,
		taxonomias,
		etapas = $bindable<string[]>([]),
		anos = $bindable<string[]>([]),
		componentes = $bindable<string[]>([]),
		areas = $bindable<string[]>([]),
		campos = $bindable<string[]>([]),
		documentos = $bindable<string[]>([]),
		tipos = $bindable<string[]>([]),
		incluirRevogados = $bindable(false),
		onexpand,
		onactivate,
		onsubmit
	}: {
		open?: boolean;
		compact?: boolean;
		taxonomias: Taxonomies | null;
		etapas?: string[];
		anos?: string[];
		componentes?: string[];
		areas?: string[];
		campos?: string[];
		documentos?: string[];
		tipos?: string[];
		incluirRevogados?: boolean;
		onexpand: () => void;
		onactivate?: () => void;
		onsubmit: () => void;
	} = $props();

	const podeBuscar = $derived(
		hasFilterScope({
			etapas,
			anos,
			componentes,
			areas,
			campos,
			documentos,
			tipos,
			incluirRevogados
		})
	);

	function submit(event: Event) {
		event.preventDefault();
		if (podeBuscar) onsubmit();
	}
</script>

<PainelDeModo
	id="filtros"
	title="Pesquisa por filtros"
	subtitle="Quando você quer escolher a etapa, o ano, o componente ou o documento."
	{open}
	{onexpand}
	{onactivate}
>
	<form class="mode-body" onsubmit={submit}>
		{#if podeBuscar}
			<div class="filter-sticky-action">
				<p id="ajuda-filtros" class="help">A busca usa as escolhas desta seção.</p>
				<button class="btn btn-primary btn-lead" type="submit" aria-describedby="ajuda-filtros">
					Buscar
				</button>
			</div>
		{/if}
		<FiltrosDaBase
			{taxonomias}
			{compact}
			{onactivate}
			bind:etapas
			bind:anos
			bind:componentes
			bind:areas
			bind:campos
			bind:documentos
			bind:tipos
			bind:incluirRevogados
		/>
	</form>
</PainelDeModo>
