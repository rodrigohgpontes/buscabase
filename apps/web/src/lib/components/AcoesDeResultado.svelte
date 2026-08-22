<script lang="ts">
	import { exportItems } from '$lib/api';
	import BotaoDeCopia from '$lib/components/BotaoDeCopia.svelte';
	import ModalDeCompartilhar from '$lib/components/ModalDeCompartilhar.svelte';
	import { referenceText } from '$lib/format';
	import { shareItemText } from '$lib/share';
	import type { Item } from '$lib/types';

	let {
		item,
		perguntarAtivo = true,
		onPerguntar
	}: { item: Item; perguntarAtivo?: boolean; onPerguntar?: (item: Item) => void } = $props();

	let status = $state('');
	let shareOpen = $state(false);

	async function download() {
		try {
			const blob = await exportItems([item.codigo], 'txt');
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `${item.codigo}.txt`;
			a.click();
			URL.revokeObjectURL(url);
			status = 'Arquivo baixado.';
		} catch {
			status = 'Não foi possível exportar os itens.';
		}
		setTimeout(() => (status = ''), 2500);
	}
</script>

<div class="actions">
	<BotaoDeCopia text={item.texto} success="Texto copiado." copyKind="texto" codigo={item.codigo}>
		Copiar texto
	</BotaoDeCopia>
	<BotaoDeCopia
		text={referenceText(item)}
		success="Texto e referência copiados."
		copyKind="texto_e_referencia"
		codigo={item.codigo}
	>
		Copiar texto e referência
	</BotaoDeCopia>
	<button class="btn btn-secondary" type="button" onclick={() => (shareOpen = true)}
		>Compartilhar</button
	>
	<button class="btn btn-secondary" type="button" onclick={download}>Baixar .txt</button>
	{#if perguntarAtivo && onPerguntar}
		<button class="btn btn-secondary" type="button" onclick={() => onPerguntar(item)}
			>Perguntar sobre este item</button
		>
	{/if}
</div>
<p class="live" aria-live="polite">{status}</p>

{#if shareOpen}
	<ModalDeCompartilhar
		bind:open={shareOpen}
		url={item.permalink}
		titulo={`Compartilhar ${item.codigo}`}
		texto={shareItemText(item.codigo)}
		codigo={item.codigo}
	/>
{/if}
