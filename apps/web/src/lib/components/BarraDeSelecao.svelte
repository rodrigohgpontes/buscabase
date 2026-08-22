<script lang="ts">
	import { exportItems } from '$lib/api';
	import BotaoDeCopia from '$lib/components/BotaoDeCopia.svelte';
	import { formatSelectedCount, formatSelectedHint, previewCodigos, referenceText } from '$lib/format';
	import type { Item } from '$lib/types';

	let { items, onClear }: { items: Item[]; onClear: () => void } = $props();
	let status = $state('');

	const preview = $derived(previewCodigos(items));
	const countLabel = $derived(formatSelectedCount(items.length));
	const hint = $derived(formatSelectedHint(items.length));
	const copyText = $derived(items.map(referenceText).join('\n\n'));

	async function download(formato: 'txt' | 'csv') {
		try {
			const blob = await exportItems(
				items.map((i) => i.codigo),
				formato
			);
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = formato === 'csv' ? 'buscabase.csv' : 'buscabase.txt';
			a.click();
			URL.revokeObjectURL(url);
			status = 'Arquivo baixado.';
		} catch {
			status = 'Não foi possível exportar os itens.';
		}
		setTimeout(() => (status = ''), 2500);
	}
</script>

<div class="selection-bar mobile-fixed" role="region" aria-label="Itens selecionados para exportar">
	<div class="selection-summary">
		<p class="selection-count">{countLabel}</p>
		<ul class="selection-preview">
			{#each preview.codes as codigo (codigo)}
				<li><span class="code">{codigo}</span></li>
			{/each}
			{#if preview.extra}
				<li class="selection-extra">e mais {preview.extra}</li>
			{/if}
		</ul>
		<p class="help">{hint}</p>
	</div>
	<div class="selection-actions">
		<BotaoDeCopia
			text={copyText}
			success="Texto e referência copiados."
			copyKind="texto_e_referencia"
			>Copiar texto e referência</BotaoDeCopia
		>
		<button class="btn btn-secondary" type="button" onclick={() => download('txt')}
			>Baixar todos em .txt</button
		>
		<button class="btn btn-secondary" type="button" onclick={() => download('csv')}
			>Baixar todos em .csv</button
		>
		<button class="btn btn-tertiary" type="button" onclick={onClear}>Limpar seleção</button>
	</div>
	<p class="live" aria-live="polite">{status}</p>
</div>
