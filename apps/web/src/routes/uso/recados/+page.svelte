<script lang="ts">
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { absoluteUrl } from '$lib/social';

	let { data } = $props();

	const title = 'Recados | Uso | Busca Base';
	const description = 'Recados enviados pelo site. Página restrita.';

	function quando(iso: string): string {
		const date = new Date(iso);
		if (Number.isNaN(date.getTime())) return iso;
		return date.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
	}
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
	<meta name="robots" content="noindex,nofollow" />
</svelte:head>

<MetasSociais {title} {description} url={absoluteUrl('/uso/recados')} noindex />

<section class="recados" aria-labelledby="recados-titulo">
	<h2 id="recados-titulo">Recados</h2>
	{#if !data.recados.length}
		<p class="help">Nenhum recado ainda.</p>
	{:else}
		<ul class="recado-lista">
			{#each data.recados as recado (recado.id)}
				<li>
					<article class="recado-item">
						<header>
							<p>
								<time datetime={recado.created_at}>{quando(recado.created_at)}</time>
								· {recado.nome}
								· <a href={`mailto:${recado.email}`}>{recado.email}</a>
							</p>
							{#if recado.pagina}
								<p class="help">{recado.pagina}</p>
							{/if}
						</header>
						<p class="recado-texto">{recado.mensagem}</p>
					</article>
				</li>
			{/each}
		</ul>
	{/if}
</section>

<style>
	.recados {
		display: grid;
		gap: var(--space-4);
	}

	.recado-lista {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		gap: var(--space-6);
	}

	.recado-item {
		display: grid;
		gap: var(--space-3);
		padding: var(--space-5);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
	}

	.recado-item header p {
		margin: 0;
	}

	.recado-texto {
		margin: 0;
		white-space: pre-wrap;
		overflow-wrap: anywhere;
	}
</style>
