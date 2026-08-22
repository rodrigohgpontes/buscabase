<script lang="ts">
	import BlocoDeProsa from '$lib/components/BlocoDeProsa.svelte';
	import { groupProseBlocks } from '$lib/prose-blocks';
	import type { ProsePagePayload } from '$lib/types';

	let { page }: { page: ProsePagePayload } = $props();

	const groups = $derived(groupProseBlocks(page.blocks));
</script>

<section class="reconstrucao-pagina" aria-label={`Página ${page.page} da reconstrução`}>
	{#each groups as group, index (group.kind === 'single' ? group.block.id : `${group.kind}-${index}`)}
		{#if group.kind === 'list'}
			<ul class="prose-list">
				{#each group.blocks as block (block.id)}
					<li id={block.id} class="prose-block">{block.text}</li>
				{/each}
			</ul>
		{:else if group.kind === 'table'}
			<table class="prose-table">
				<tbody>
					{#each group.blocks as block (block.id)}
						<tr>
							{#if block.type === 'table_header'}
								<th id={block.id} class="prose-block">{block.text}</th>
							{:else}
								<td id={block.id} class="prose-block">{block.text}</td>
							{/if}
						</tr>
					{/each}
				</tbody>
			</table>
		{:else}
			<BlocoDeProsa block={group.block} />
		{/if}
	{/each}
</section>
