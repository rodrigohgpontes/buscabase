<script lang="ts">
	import PainelDeModo from '$lib/components/PainelDeModo.svelte';

	let {
		open = true,
		compact = false,
		disabled = false,
		busy = false,
		threadActive = false,
		value = $bindable(''),
		onexpand,
		onactivate,
		onsubmit
	}: {
		open?: boolean;
		compact?: boolean;
		disabled?: boolean;
		busy?: boolean;
		threadActive?: boolean;
		value?: string;
		onexpand: () => void;
		onactivate?: () => void;
		onsubmit: (q: string) => void;
	} = $props();

	function example(text: string) {
		if (busy) return;
		value = text;
		onactivate?.();
		document.getElementById('campo-perguntar')?.focus();
	}

	function examplePress(event: PointerEvent, text: string) {
		if (event.button) return;
		event.preventDefault();
		example(text);
	}

	function submit(event: Event) {
		event.preventDefault();
		if (!disabled && !busy && value.trim()) onsubmit(value);
	}
</script>

<PainelDeModo
	id="perguntar"
	title="Pesquisa conversacional"
	subtitle="Quando você quer entender melhor a BNCC interagindo com uma IA."
	{open}
	{disabled}
	disabledTitle="Pesquisa conversacional está temporariamente indisponível."
	{onexpand}
	{onactivate}
>
	{#if disabled}
		<p>
			Você ainda pode encontrar e copiar itens usando Pesquisa por código, Pesquisa por filtros ou
			Pesquisa simples.
		</p>
	{:else if threadActive}
		<p class="help">
			A continuação usa os códigos e a resposta anteriores. Nova consulta começa outra conversa.
		</p>
	{:else}
		<form class="mode-body" onsubmit={submit}>
			<div class="field field-lead">
				<label for="campo-perguntar">O que você quer entender ou comparar?</label>
				<p id="aviso-perguntar" class="help">
					As respostas usam trechos da Base e mostram as fontes. A BNCC não é um plano de aula.
				</p>
				<p id="priv-perguntar" class="help">
					Não inclua nomes ou outros dados pessoais de estudantes.
				</p>
				<textarea
					id="campo-perguntar"
					bind:value
					placeholder="Ex.: compare leitura no 2º e no 3º ano"
					aria-describedby="aviso-perguntar priv-perguntar"
					disabled={busy}
				></textarea>
			</div>
			<button class="btn btn-primary btn-lead" type="submit" disabled={busy}>Perguntar</button>
			{#if !compact}
				<div class="examples">
					<button
						class="example"
						type="button"
						disabled={busy}
						onpointerdown={(event) =>
							examplePress(event, 'Explique EF05MA03 em palavras mais simples')}
						onclick={() => example('Explique EF05MA03 em palavras mais simples')}
						>Explique EF05MA03 em palavras mais simples</button
					>
					<button
						class="example"
						type="button"
						disabled={busy}
						onpointerdown={(event) => examplePress(event, 'Compare frações no 5º e no 6º ano')}
						onclick={() => example('Compare frações no 5º e no 6º ano')}
						>Compare frações no 5º e no 6º ano</button
					>
				</div>
			{/if}
		</form>
	{/if}
</PainelDeModo>
