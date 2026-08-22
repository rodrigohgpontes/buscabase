<script lang="ts">
	import { chipRemoveLabel } from '$lib/inferred';
	import type { InferredChip } from '$lib/types';

	let {
		chips,
		onremove
	}: {
		chips: InferredChip[];
		onremove: (chip: InferredChip) => void;
	} = $props();
</script>

{#if chips.length}
	<div class="inferred">
		<p class="inferred-lead">Lido da sua busca</p>
		<ul class="filter-chips">
			{#each chips as chip (chip.kind + chip.id)}
				<li>
					<button
						class="chip"
						type="button"
						aria-label={chipRemoveLabel(chip)}
						onclick={() => onremove(chip)}
					>
						<span>{chip.label}</span>
						<span class="chip-remove">Remover</span>
					</button>
				</li>
			{/each}
		</ul>
	</div>
{/if}

<style>
	.inferred {
		display: grid;
		gap: var(--space-2);
	}

	.inferred-lead {
		margin: 0;
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}
</style>
