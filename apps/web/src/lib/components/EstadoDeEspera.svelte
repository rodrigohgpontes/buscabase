<script lang="ts">
	let { texto, onCancel }: { texto: string; onCancel?: () => void } = $props();
</script>

<div class="status-line" role="status">
	<div class="spinner" aria-hidden="true"></div>
	<p>{texto}</p>
	{#if onCancel}
		<button class="btn btn-tertiary" type="button" onclick={onCancel}>Cancelar pergunta</button>
	{/if}
</div>
