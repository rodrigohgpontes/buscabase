<script lang="ts">
	import { headingTag, isChromeType } from '$lib/prose-blocks';
	import type { ProseBlock } from '$lib/types';

	let { block }: { block: ProseBlock } = $props();

	const tag = $derived(headingTag(block.type));
	const chrome = $derived(isChromeType(block.type));
	const isFigure = $derived(block.type === 'figure');
</script>

{#if isFigure}
	<p id={block.id} class="prose-block prose-figure">Figura no PDF oficial, p. {block.page}.</p>
{:else}
	<svelte:element this={tag} id={block.id} class={['prose-block', chrome && 'chrome']}>
		{block.text}
	</svelte:element>
{/if}
