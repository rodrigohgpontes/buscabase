<script lang="ts">
	import { onDestroy } from 'svelte';
	import type { Snippet } from 'svelte';

	let {
		id,
		title,
		subtitle,
		open,
		disabled = false,
		disabledTitle,
		onexpand,
		onactivate,
		children
	}: {
		id: string;
		title: string;
		subtitle: string;
		open: boolean;
		disabled?: boolean;
		disabledTitle?: string;
		onexpand: () => void;
		onactivate?: () => void;
		children: Snippet;
	} = $props();

	const titleId = $derived(`titulo-${id}`);
	const bodyId = $derived(`corpo-${id}`);
	const heading = $derived(disabled && disabledTitle ? disabledTitle : title);

	let activateTimer: ReturnType<typeof setTimeout> | undefined;

	function onFocusIn() {
		if (!open || disabled) return;
		// Collapse siblings after the originating click, so a first tap on a
		// suggestion or <details> still performs that action.
		clearTimeout(activateTimer);
		activateTimer = setTimeout(() => onactivate?.());
	}

	onDestroy(() => clearTimeout(activateTimer));
</script>

<section
	class={['mode-section', !open && 'is-collapsed', disabled && 'is-disabled']}
	aria-labelledby={titleId}
>
	{#if open}
		<div class="mode-head">
			<h2 id={titleId}>{heading}</h2>
			{#if !disabled}
				<p class="mode-subtitle">{subtitle}</p>
			{/if}
		</div>
	{:else}
		<button
			class="mode-head mode-head-button"
			type="button"
			id={titleId}
			aria-expanded="false"
			aria-controls={bodyId}
			aria-label={disabled ? heading : `Abrir ${title}`}
			disabled={disabled}
			onclick={onexpand}
		>
			<span class="mode-title">{heading}</span>
		</button>
	{/if}

	<div class={['fold', !open && 'is-closed']} id={bodyId} inert={!open}>
		<div class="fold-inner" onfocusin={onFocusIn}>
			<div class="mode-body-slot">
				{@render children()}
			</div>
		</div>
	</div>
</section>
