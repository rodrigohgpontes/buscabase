<script lang="ts">
	import type { Suggestion } from '$lib/types';

	let {
		items,
		verMais,
		onVerMais
	}: { items: Suggestion[]; verMais: boolean; onVerMais: () => void } = $props();
</script>

{#if items.length}
	<div class="suggestions">
		{#each items as item (item.codigo)}
			<a class="suggestion" href={item.url_path} aria-label={item.nome_acessivel}>
				<span class="code">{item.codigo}</span>
				<p class="snip">{item.texto}</p>
				<p class="ctx">{item.contexto}</p>
			</a>
		{/each}
		{#if verMais}
			<button class="suggestion" type="button" onclick={onVerMais}>Ver mais códigos</button>
		{/if}
	</div>
{/if}
