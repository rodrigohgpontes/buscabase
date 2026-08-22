<script lang="ts">
	import BotaoDeCopia from '$lib/components/BotaoDeCopia.svelte';
	import { shareTargets } from '$lib/share';
	import { recordClientEvent } from '$lib/usage';
	import type { Attachment } from 'svelte/attachments';

	let {
		open = $bindable(false),
		url,
		titulo,
		texto,
		aviso = '',
		codigo,
		mode
	}: {
		open?: boolean;
		url: string;
		titulo: string;
		texto: string;
		aviso?: string;
		codigo?: string;
		mode?: 'codigo' | 'filtros' | 'buscar' | 'perguntar';
	} = $props();

	const titleId = `share-title-${Math.random().toString(36).slice(2, 10)}`;
	const inputId = `share-url-${titleId}`;

	const targets = $derived(url ? shareTargets(url, texto) : []);

	const focusPanel: Attachment<HTMLElement> = (node) => {
		const previous = document.activeElement as HTMLElement | null;
		node.focus();
		function onKey(event: KeyboardEvent) {
			if (event.key === 'Escape') {
				event.preventDefault();
				fechar();
			}
		}
		window.addEventListener('keydown', onKey);
		return () => {
			window.removeEventListener('keydown', onKey);
			previous?.focus?.();
		};
	};

	function fechar() {
		open = false;
	}

	function selecionar(e: FocusEvent & { currentTarget: HTMLInputElement }) {
		e.currentTarget.select();
	}
</script>

<div class="share-root">
	<button class="share-scrim" type="button" aria-label="Fechar" onclick={fechar}></button>
	<div
		class="share-panel"
		role="dialog"
		aria-modal="true"
		aria-labelledby={titleId}
		tabindex="-1"
		{@attach focusPanel}
	>
		<header class="share-head">
			<h2 id={titleId} class="share-title">{titulo}</h2>
			<button class="btn btn-tertiary share-close" type="button" onclick={fechar}>Fechar</button>
		</header>

		{#if aviso}
			<p class="help">{aviso}</p>
		{:else if !url}
			<p class="help">Montando o link…</p>
		{:else}
			<div class="field share-url-field">
				<label for={inputId}>Link</label>
				<div class="field-with-action">
					<input id={inputId} type="text" readonly value={url} onfocus={selecionar} />
					<BotaoDeCopia
						class="btn btn-primary"
						text={url}
						success="Link copiado."
						copyKind="link"
						{codigo}
						{mode}
					>
						Copiar link
					</BotaoDeCopia>
				</div>
			</div>

			<p class="help">Abra em outro aplicativo ou copie o link.</p>

			<ul class="share-targets">
				{#each targets as target (target.id)}
					<li>
						<a
							class="btn btn-secondary share-target"
							href={target.href}
							target={target.id === 'email' ? undefined : '_blank'}
							rel={target.id === 'email' ? undefined : 'noopener noreferrer'}
							onclick={() => recordClientEvent({ kind: 'share', codigo, mode })}
						>
							{#if target.id === 'whatsapp'}
								<svg class="share-icon" viewBox="0 0 24 24" aria-hidden="true"
									><path
										fill="currentColor"
										d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2m.01 1.67c2.2 0 4.26.86 5.82 2.42a8.23 8.23 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.24 8.23-1.48 0-2.93-.39-4.19-1.15l-.3-.17-3.12.82.83-3.04-.2-.32a8.2 8.2 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.25-8.24m4.52 10.4c-.25-.12-1.47-.72-1.7-.8-.23-.09-.39-.12-.56.12-.17.25-.64.8-.79.96-.14.17-.29.19-.54.06-.25-.12-1.05-.39-2-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.43.13-.14.17-.25.25-.41.09-.17.04-.31-.02-.43-.06-.12-.56-1.35-.76-1.84-.2-.49-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.88 2.4 1 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.14-1.18-.06-.1-.23-.17-.48-.29"
									/></svg
								>
							{:else if target.id === 'linkedin'}
								<svg class="share-icon" viewBox="0 0 24 24" aria-hidden="true"
									><path
										fill="currentColor"
										d="M19 3A2 2 0 0 1 21 5v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77Z"
									/></svg
								>
							{:else if target.id === 'telegram'}
								<svg class="share-icon" viewBox="0 0 24 24" aria-hidden="true"
									><path
										fill="currentColor"
										d="M9.78 18.65 10.06 14.42 17.74 7.5c.34-.31-.07-.46-.52-.19L7.74 13.4 3.64 12.15c-.88-.25-.89-.86.2-1.3l15.97-6.16c.73-.33 1.43.18 1.15 1.3l-2.72 12.81c-.19.91-.74 1.13-1.5.71L12.6 16.3l-1.99 1.93c-.23.23-.42.42-.83.42Z"
									/></svg
								>
							{:else}
								<svg class="share-icon" viewBox="0 0 24 24" aria-hidden="true"
									><path
										fill="currentColor"
										d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2m0 4-8 5-8-5V6l8 5 8-5v2Z"
									/></svg
								>
							{/if}
							{target.label}
						</a>
					</li>
				{/each}
			</ul>
		{/if}

	</div>
</div>

<style>
	.share-root {
		position: fixed;
		inset: 0;
		z-index: 80;
		display: grid;
		place-items: center;
		padding: var(--space-4);
	}

	.share-scrim {
		position: absolute;
		inset: 0;
		border: 0;
		padding: 0;
		background: rgba(26, 33, 24, 0.45);
		cursor: pointer;
	}

	.share-panel {
		position: relative;
		z-index: 1;
		width: min(32rem, 100%);
		padding: var(--space-6);
		display: grid;
		gap: var(--space-4);
		border: 1px solid var(--color-border-strong);
		background: var(--color-surface);
		color: var(--color-text);
	}

	.share-head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: var(--space-3);
	}

	.share-title {
		font-family: var(--font-title);
		font-size: var(--text-xl);
		font-weight: 700;
		margin: 0;
	}

	.share-close {
		flex-shrink: 0;
	}

	.share-url-field {
		margin: 0;
	}

	.share-targets {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--space-3);
	}

	.share-target {
		width: 100%;
		gap: var(--space-2);
	}

	.share-icon {
		width: 1.25rem;
		height: 1.25rem;
		flex-shrink: 0;
	}
</style>
