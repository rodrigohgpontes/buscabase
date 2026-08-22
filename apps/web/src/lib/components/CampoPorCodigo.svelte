<script lang="ts">
	import { getSuggestions } from '$lib/api';
	import PainelDeModo from '$lib/components/PainelDeModo.svelte';
	import SugestoesDeCodigo from '$lib/components/SugestoesDeCodigo.svelte';
	import type { Suggestion } from '$lib/types';

	let {
		value = $bindable(''),
		open = true,
		onexpand,
		onactivate
	}: {
		value?: string;
		open?: boolean;
		onexpand: () => void;
		onactivate?: () => void;
	} = $props();

	const PREVIEW_LIMIT = 5;
	const PEEK_LIMIT = 9;
	const ALL_LIMIT = 50;
	const SHOW_ALL_FROM_CHARS = 6;
	const SHOW_ALL_MAX_TOTAL = 8;

	let suggestions = $state<Suggestion[]>([]);
	let verMais = $state(false);
	let anuncio = $state('');
	let listaAberta = $state(false);
	let timer: ReturnType<typeof setTimeout> | undefined;
	let fetchGen = 0;

	function normalizedCode(raw: string) {
		return raw.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
	}

	async function loadSuggestions(raw: string, expand = false) {
		const typed = normalizedCode(raw).length;
		const gen = ++fetchGen;
		if (typed < 2) {
			suggestions = [];
			verMais = false;
			anuncio = '';
			listaAberta = false;
			return;
		}
		const wantAll = expand || typed >= SHOW_ALL_FROM_CHARS;
		try {
			const data = await getSuggestions(raw, wantAll ? ALL_LIMIT : PEEK_LIMIT);
			if (gen !== fetchGen) return;
			const tooMany = data.items.length > SHOW_ALL_MAX_TOTAL || data.ver_mais;
			if (wantAll || !tooMany) {
				suggestions = data.items;
				verMais = false;
			} else {
				suggestions = data.items.slice(0, PREVIEW_LIMIT);
				verMais = true;
			}
			anuncio = suggestions.length
				? `${suggestions.length} sugestões de código.`
				: 'Nenhuma sugestão para este início de código.';
			listaAberta = true;
		} catch {
			if (gen !== fetchGen) return;
			suggestions = [];
			verMais = false;
			anuncio = 'Nenhuma sugestão para este início de código.';
			listaAberta = true;
		}
	}

	function expandSuggestions() {
		void loadSuggestions(value, true);
	}

	$effect(() => {
		const q = value;
		clearTimeout(timer);
		timer = setTimeout(() => {
			void loadSuggestions(q);
		}, 150);
	});

	function onInput() {
		onactivate?.();
	}

	function submit(event: Event) {
		event.preventDefault();
	}

	function onKey(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			listaAberta = false;
		}
		if (event.key === 'Enter') {
			event.preventDefault();
		}
	}
</script>

<PainelDeModo
	id="codigo"
	title="Pesquisa por código"
	subtitle="Quando você sabe o código, ou ao menos o começo dele."
	{open}
	{onexpand}
	{onactivate}
>
	<form class="mode-body" onsubmit={submit}>
		<div class="field field-lead">
			<label for="campo-codigo">Digite o código</label>
			<p id="ajuda-codigo" class="help">O código começa com EI, EF ou EM. Exemplo: EF05MA03</p>
			<input
				id="campo-codigo"
				name="codigo"
				type="text"
				autocomplete="off"
				spellcheck="false"
				placeholder="EF05MA03"
				aria-describedby="ajuda-codigo"
				bind:value
				oninput={onInput}
				onkeydown={onKey}
			/>
		</div>
		<p class="live" aria-live="polite">{anuncio}</p>
		{#if listaAberta}
			{#if suggestions.length}
				<p class="help">Escolha uma sugestão para abrir o item.</p>
				<SugestoesDeCodigo items={suggestions} {verMais} onVerMais={expandSuggestions} />
			{:else}
				<p class="help">Nenhuma sugestão para este início de código.</p>
			{/if}
		{/if}
	</form>
</PainelDeModo>
