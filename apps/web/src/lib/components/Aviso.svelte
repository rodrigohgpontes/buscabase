<script lang="ts">
	let {
		kind = 'info',
		titulo,
		texto,
		acao,
		onAcao
	}: {
		kind?: 'info' | 'erro' | 'atencao' | 'sucesso';
		titulo?: string;
		texto: string;
		acao?: string;
		onAcao?: () => void;
	} = $props();
</script>

<div class={`aviso aviso-${kind === 'info' ? 'info' : kind}`.trim()} role={kind === 'erro' ? 'alert' : 'status'}>
	{#if titulo}
		<p><strong>{titulo}</strong></p>
	{/if}
	<p>{texto}</p>
	{#if acao && onAcao}
		<button class="btn btn-secondary" type="button" onclick={onAcao}>{acao}</button>
	{/if}
</div>
