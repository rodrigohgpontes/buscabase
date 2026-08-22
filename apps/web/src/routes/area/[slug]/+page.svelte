<script lang="ts">
	import { page } from '$app/state';
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { absoluteUrl } from '$lib/social';

	let { data } = $props();
	const title = $derived(`${data.nome} na BNCC | Busca Base`);
	const description = $derived(`Itens de ${data.nome} na BNCC.`);
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
</svelte:head>

<MetasSociais {title} {description} url={absoluteUrl(page.url.pathname)} />

<div class="wrap reading">
	<nav class="breadcrumbs" aria-label="Trilha">
		<a href="/">Busca Base</a>
		<span aria-hidden="true">›</span>
		<a href="/indices#areas">Áreas</a>
		<span aria-hidden="true">›</span>
		<span>{data.nome}</span>
	</nav>
	<p><a class="btn btn-primary" href="/">Buscar na Base</a></p>
	<h1>{data.nome}</h1>
	{#if data.items.length}
		<ul>
			{#each data.items as item}
				<li><a href={item.url_path}>{item.codigo}</a></li>
			{/each}
		</ul>
	{:else}
		<p>Nenhum item neste recorte.</p>
	{/if}
	<p><a href="/">Fazer outra busca</a></p>
</div>
