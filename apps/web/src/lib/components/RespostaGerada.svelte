<script lang="ts">
	import { parseAnswer, type AnswerInline } from '$lib/answer';

	let {
		text,
		onCite
	}: {
		text: string;
		onCite?: (n: number) => void;
	} = $props();

	const blocks = $derived(parseAnswer(text));

	function cite(n: number) {
		onCite?.(n);
	}
</script>

{#snippet inlines(parts: AnswerInline[])}
	{#each parts as part, i (i)}
		{#if part.type === 'text'}
			{part.text}
		{:else if part.type === 'bold'}
			<strong>{part.text}</strong>
		{:else if part.type === 'citation'}
			{#if onCite}
				<button
					class="cite"
					type="button"
					onclick={() => cite(part.n)}
					aria-label={`Ir para a fonte ${part.n}`}
				>
					[{part.n}]
				</button>
			{:else}
				<span class="cite cite-static">[{part.n}]</span>
			{/if}
		{/if}
	{/each}
{/snippet}

<div class="answer-body">
	{#each blocks as block, i (i)}
		{#if block.type === 'paragraph'}
			<p>{@render inlines(block.parts)}</p>
		{:else if block.type === 'heading'}
			<p class="answer-heading">{block.text}</p>
		{:else if block.type === 'list'}
			{#if block.ordered}
				<ol>
					{#each block.items as item, j (j)}
						<li>{@render inlines(item)}</li>
					{/each}
				</ol>
			{:else}
				<ul>
					{#each block.items as item, j (j)}
						<li>{@render inlines(item)}</li>
					{/each}
				</ul>
			{/if}
		{/if}
	{/each}
</div>
