<script lang="ts">
	import { page } from '$app/state';
	import Aviso from '$lib/components/Aviso.svelte';
	import { tick } from 'svelte';
	import type { Attachment } from 'svelte/attachments';

	let aberto = $state(false);
	let enviando = $state(false);
	let enviado = $state(false);
	let erroTitulo = $state('');
	let erroTexto = $state('');
	let nome = $state('');
	let email = $state('');
	let mensagem = $state('');
	let botao: HTMLButtonElement | undefined = $state();

	const titleId = 'recado-titulo';

	const aoAbrirPainel: Attachment<HTMLElement> = (node) => {
		tick().then(() => {
			const campo = node.querySelector<HTMLInputElement>('#recado-nome');
			(campo ?? node).focus();
		});
		function onKey(event: KeyboardEvent) {
			if (event.key === 'Escape') {
				event.preventDefault();
				fechar();
			}
		}
		window.addEventListener('keydown', onKey);
		return () => window.removeEventListener('keydown', onKey);
	};

	function abrir() {
		aberto = true;
		enviado = false;
		erroTitulo = '';
		erroTexto = '';
	}

	function fechar() {
		aberto = false;
		enviando = false;
		enviado = false;
		erroTitulo = '';
		erroTexto = '';
		nome = '';
		email = '';
		mensagem = '';
		tick().then(() => botao?.focus());
	}

	function alternar() {
		if (aberto) fechar();
		else abrir();
	}

	async function enviar(event: Event) {
		event.preventDefault();
		if (enviando || enviado) return;
		enviando = true;
		erroTitulo = '';
		erroTexto = '';
		try {
			const response = await fetch('/api/recados', {
				method: 'POST',
				headers: { accept: 'application/json', 'content-type': 'application/json' },
				body: JSON.stringify({
					nome,
					email,
					mensagem,
					pagina: page.url.pathname
				})
			});
			if (!response.ok) {
				const body = (await response.json().catch(() => ({}))) as {
					detail?: { titulo?: string; texto?: string };
				};
				const detail = body.detail;
				erroTitulo =
					(typeof detail === 'object' && detail?.titulo) ||
					'Não foi possível mandar o recado agora.';
				erroTexto =
					(typeof detail === 'object' && detail?.texto) || 'Tente de novo em instantes.';
				return;
			}
			enviado = true;
			nome = '';
			email = '';
			mensagem = '';
		} catch {
			erroTitulo = 'Não foi possível mandar o recado agora.';
			erroTexto = 'Tente de novo em instantes.';
		} finally {
			enviando = false;
		}
	}
</script>

<div class="recado-root">
	{#if aberto}
		<div
			id="recado-painel"
			class="recado-panel"
			role="dialog"
			aria-labelledby={titleId}
			tabindex="-1"
			{@attach aoAbrirPainel}
		>
			<header class="recado-head">
				<h2 id={titleId} class="recado-title">Deixe um recado</h2>
				<button class="btn btn-tertiary recado-close" type="button" onclick={fechar}>Fechar</button>
			</header>
			{#if enviado}
				<Aviso kind="sucesso" titulo="Recado recebido." texto="Se precisar de resposta, usamos o e-mail que você informou." />
			{:else}
				<p class="help">
					Nome, e-mail e o que você quer dizer. Sugestões para melhorar o Busca Base são
					bem-vindas. Usamos isso só para responder.
				</p>
				{#if erroTitulo}
					<Aviso kind="erro" titulo={erroTitulo} texto={erroTexto} />
				{/if}
				<form class="recado-form" onsubmit={enviar}>
					<div class="field">
						<label for="recado-nome">Nome</label>
						<input
							id="recado-nome"
							name="nome"
							type="text"
							autocomplete="name"
							maxlength="120"
							required
							bind:value={nome}
							disabled={enviando}
						/>
					</div>
					<div class="field">
						<label for="recado-email">E-mail</label>
						<input
							id="recado-email"
							name="email"
							type="email"
							autocomplete="email"
							maxlength="254"
							required
							bind:value={email}
							disabled={enviando}
						/>
					</div>
					<div class="field">
						<label for="recado-mensagem">Mensagem</label>
						<textarea
							id="recado-mensagem"
							name="mensagem"
							maxlength="4000"
							required
							bind:value={mensagem}
							disabled={enviando}
						></textarea>
					</div>
					<button class="btn btn-primary" type="submit" disabled={enviando}>Enviar recado</button>
				</form>
			{/if}
		</div>
	{/if}
	<button
		bind:this={botao}
		class="btn recado-toggle"
		type="button"
		aria-expanded={aberto}
		aria-controls={aberto ? 'recado-painel' : undefined}
		onclick={alternar}
	>
		Deixe um recado
	</button>
</div>

<style>
	.recado-root {
		position: fixed;
		right: max(var(--space-4), env(safe-area-inset-right, 0px));
		bottom: max(var(--space-4), env(safe-area-inset-bottom, 0px));
		z-index: 30;
		display: grid;
		justify-items: end;
		gap: var(--space-3);
		width: min(22rem, calc(100vw - 2rem));
		pointer-events: none;
	}

	.recado-root > :global(*) {
		pointer-events: auto;
	}

	:global(body:has(.selection-bar)) .recado-root {
		bottom: max(calc(5rem + env(safe-area-inset-bottom, 0px)), var(--space-4));
	}

	@media (min-width: 48rem) {
		:global(body:has(.selection-bar)) .recado-root {
			bottom: max(var(--space-4), env(safe-area-inset-bottom, 0px));
		}
	}

	.recado-panel {
		width: 100%;
		padding: var(--space-5);
		display: grid;
		gap: var(--space-4);
		border: 2px solid var(--color-brand);
		background: var(--color-canary);
		color: var(--color-brand);
	}

	.recado-head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: var(--space-3);
	}

	.recado-title {
		font-family: var(--font-title);
		font-size: var(--text-xl);
		font-weight: 700;
		margin: 0;
	}

	.recado-close {
		flex-shrink: 0;
		color: var(--color-brand);
	}

	.recado-form {
		display: grid;
		gap: var(--space-4);
	}

	.recado-toggle {
		background: var(--color-canary);
		color: var(--color-brand);
		border: 2px solid var(--color-brand);
		font-weight: 700;
		white-space: nowrap;
	}

	.recado-toggle:hover:not(:disabled) {
		background: var(--color-canary);
		color: var(--color-brand);
		border-color: var(--color-brand);
	}
</style>
