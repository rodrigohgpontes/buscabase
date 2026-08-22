<script lang="ts">
	import { page } from '$app/state';
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { absoluteUrl } from '$lib/social';

	let { data } = $props();
	const title = $derived(`Habilidades da BNCC para o ${data.nome} | Busca Base`);
	const description = $derived(`Consulte itens da BNCC para ${data.nome}.`);
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
		<a href="/indices#anos">Anos e faixas</a>
		<span aria-hidden="true">›</span>
		<span>{data.nome}</span>
	</nav>
	<p><a class="btn btn-primary" href={`/?modo=buscar`}>Buscar na Base</a></p>
	<h1>Habilidades da BNCC para o {data.nome}</h1>
	<p>Recorte {data.recorte}.</p>
	{#if data.items.length}
		<ul>
			{#each data.items as item}
				<li><a href={item.url_path}>{item.codigo}</a> — {item.componente ?? item.tipo_label}</li>
			{/each}
		</ul>
	{:else}
		<p>Nenhum item neste recorte.</p>
	{/if}
	<p><a href="/">Fazer outra busca</a></p>
</div>
