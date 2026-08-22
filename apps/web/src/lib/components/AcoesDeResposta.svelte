<script lang="ts">
	import BotaoDeCopia from '$lib/components/BotaoDeCopia.svelte';
	import { answerWithSourcesText } from '$lib/format';
	import type { CitedSource } from '$lib/types';

	let {
		answerText,
		citedSources = [],
		onShare
	}: {
		answerText: string;
		citedSources?: CitedSource[];
		onShare?: () => void | Promise<void>;
	} = $props();

	let status = $state('');

	function download() {
		const body = answerWithSourcesText(answerText, citedSources);
		const blob = new Blob([body], { type: 'text/plain;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'busca-base-resposta.txt';
		a.click();
		URL.revokeObjectURL(url);
		status = 'Arquivo baixado.';
		setTimeout(() => (status = ''), 2500);
	}
</script>

<div class="actions">
	<BotaoDeCopia text={answerText} success="Resposta copiada." copyKind="texto" mode="perguntar"
		>Copiar resposta</BotaoDeCopia
	>
	<BotaoDeCopia
		text={answerWithSourcesText(answerText, citedSources)}
		success="Resposta e fontes copiadas."
		copyKind="texto_e_referencia"
		mode="perguntar"
	>
		Copiar resposta e fontes
	</BotaoDeCopia>
	<button class="btn btn-secondary" type="button" onclick={() => onShare?.()}>Compartilhar</button>
	<button class="btn btn-secondary" type="button" onclick={download}>Baixar .txt</button>
</div>
<p class="live" aria-live="polite">{status}</p>
