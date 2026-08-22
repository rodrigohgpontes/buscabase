<script lang="ts">
	import CartaoDeAprendizagem from '$lib/components/CartaoDeAprendizagem.svelte';
	import { snippetText } from '$lib/answer';
	import type { CitedSource } from '$lib/types';

	let {
		sources,
		idPrefix = 'fonte'
	}: {
		sources: CitedSource[];
		idPrefix?: string;
	} = $props();
</script>

{#if sources.length}
	<div class="fontes">
		<h3>Fontes</h3>
		{#each sources as entry (entry.n)}
			{#if entry.kind === 'prose'}
				<article class="fonte fonte-prose" id={`${idPrefix}-${entry.n}`}>
					<p class="code">[{entry.n}] {entry.documento}, p. {entry.page}</p>
					<p class="meta card-label"><strong>Texto oficial (reconstrução)</strong></p>
					<p class="snip">{snippetText(entry.texto)}</p>
					<p>
						<a href={entry.url_path}>Abrir na reconstrução</a>
					</p>
				</article>
			{:else}
				<details class="fonte" id={`${idPrefix}-${entry.n}`}>
					<summary class="fonte-summary">
						<span class="code">[{entry.n}] {entry.item.codigo}</span>
						<p class="snip">{snippetText(entry.item.texto)}</p>
						<p class="ctx">{entry.item.contexto_curto || entry.item.tipo_label}</p>
					</summary>
					<div class="fonte-body">
						<CartaoDeAprendizagem item={entry.item} detail perguntarAtivo={false} />
					</div>
				</details>
			{/if}
		{/each}
	</div>
{/if}
