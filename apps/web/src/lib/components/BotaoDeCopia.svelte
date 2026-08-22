<script lang="ts">
	import { onDestroy, type Snippet } from 'svelte';
	import { recordClientEvent } from '$lib/usage';

	let {
		text,
		success,
		class: className = 'btn btn-secondary',
		copyKind,
		codigo,
		mode,
		children
	}: {
		text: string;
		success: string;
		class?: string;
		copyKind?: 'texto' | 'texto_e_referencia' | 'link';
		codigo?: string;
		mode?: 'codigo' | 'filtros' | 'buscar' | 'perguntar';
		children: Snippet;
	} = $props();

	let message = $state('');
	let failed = $state(false);
	let tick = $state(0);
	let timer: ReturnType<typeof setTimeout> | undefined;

	async function copiar() {
		try {
			await navigator.clipboard.writeText(text);
			message = success;
			failed = false;
			if (copyKind) {
				recordClientEvent({ kind: 'copy', copy_kind: copyKind, codigo, mode });
			}
		} catch {
			message = 'Não foi possível copiar. Tente de novo.';
			failed = true;
		}
		tick += 1;
		if (timer) clearTimeout(timer);
		timer = setTimeout(() => (message = ''), 2500);
	}

	onDestroy(() => {
		if (timer) clearTimeout(timer);
	});
</script>

<span class="copy-wrap">
	<button class={className} type="button" onclick={copiar}>
		{@render children()}
	</button>
	{#if message}
		{#key tick}
			<span class={['copy-toast', failed && 'is-error']} role={failed ? 'alert' : 'status'}>
				{message}
			</span>
		{/key}
	{/if}
</span>

<style>
	.copy-wrap {
		position: relative;
		display: grid;
	}

	.copy-toast {
		position: absolute;
		bottom: calc(100% + var(--space-2));
		left: 50%;
		z-index: 6;
		padding: var(--space-2) var(--space-3);
		border: 1px solid var(--color-primary);
		background: var(--color-primary);
		color: var(--color-on-primary);
		font-size: var(--text-xs);
		font-weight: 600;
		line-height: 1.3;
		text-align: center;
		white-space: nowrap;
		pointer-events: none;
		translate: -50% 0;
		animation: copy-toast-in var(--duration) var(--easing);
	}

	.copy-toast.is-error {
		border-color: var(--color-error);
		background: var(--color-error);
	}

	@keyframes copy-toast-in {
		from {
			opacity: 0;
			translate: -50% 0.25rem;
		}
		to {
			opacity: 1;
			translate: -50% 0;
		}
	}
</style>
