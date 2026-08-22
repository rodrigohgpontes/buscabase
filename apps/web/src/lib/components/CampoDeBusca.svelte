<script lang="ts">
	import PainelDeModo from '$lib/components/PainelDeModo.svelte';

	let {
		value = $bindable(''),
		open = true,
		compact = false,
		onexpand,
		onactivate,
		onsubmit
	}: {
		value?: string;
		open?: boolean;
		compact?: boolean;
		onexpand: () => void;
		onactivate?: () => void;
		onsubmit: (q: string) => void;
	} = $props();

	function submit(event: Event) {
		event.preventDefault();
		if (!value.trim()) return;
		onsubmit(value);
	}

	function example(text: string) {
		value = text;
		onactivate?.();
		document.getElementById('campo-busca')?.focus();
	}

	function examplePress(event: PointerEvent, text: string) {
		if (event.button) return;
		event.preventDefault();
		example(text);
	}
</script>

<PainelDeModo
	id="buscar"
	title="Pesquisa simples"
	subtitle="Quando você sabe o que quer achar, mas não o código."
	{open}
	{onexpand}
	{onactivate}
>
	<form class="mode-body" onsubmit={submit}>
		<div class="field-with-action">
			<div class="field field-lead">
				<label for="campo-busca">O que você quer encontrar na BNCC?</label>
				<p class="help">
					Digite um tema, um ano ou um componente. A busca encontra habilidades e outros itens da
					Base.
				</p>
				<p id="ajuda-busca" class="help">
					Não precisa do código. Exemplo: frações no 5º ano. Perguntas mais amplas também podem
					mostrar trechos do documento oficial.
				</p>
				<input
					id="campo-busca"
					name="q"
					type="search"
					placeholder="Ex.: frações no 5º ano"
					aria-describedby="ajuda-busca"
					bind:value
				/>
			</div>
			<button class="btn btn-primary btn-lead" type="submit">Buscar</button>
		</div>
		{#if !compact}
			<div class="examples">
				<button
					class="example"
					type="button"
					onpointerdown={(event) => examplePress(event, 'frações no 5º ano')}
					onclick={() => example('frações no 5º ano')}>frações no 5º ano</button
				>
				<button
					class="example"
					type="button"
					onpointerdown={(event) => examplePress(event, 'argumentação no Ensino Médio')}
					onclick={() => example('argumentação no Ensino Médio')}
					>argumentação no Ensino Médio</button
				>
			</div>
		{/if}
	</form>
</PainelDeModo>
