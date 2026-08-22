<script lang="ts">
	import CartaoDeAprendizagem from '$lib/components/CartaoDeAprendizagem.svelte';
	import MetasSociais from '$lib/components/MetasSociais.svelte';

	let { data } = $props();
	const item = $derived(data.item);
	const title = $derived(
		`${item.codigo}: habilidade de ${item.componente ?? 'a Base'}${item.anos_label ? ` do ${item.anos_label}` : ''} | Busca Base`
	);
	const description = $derived(
		`Consulte o texto da habilidade ${item.codigo}, seu contexto em ${item.metadados_linha} e a fonte na BNCC.`
	);
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
	{@html `<script type="application/ld+json">${JSON.stringify({
		'@context': 'https://schema.org',
		'@type': 'DefinedTerm',
		name: item.codigo,
		description: item.texto,
		url: item.permalink,
		inDefinedTermSet: 'BNCC'
	})}</script>`}
</svelte:head>

<MetasSociais {title} {description} url={item.permalink} />

<div class="wrap reading">
	<nav class="breadcrumbs" aria-label="Trilha">
		<a href="/">Busca Base</a>
		<span aria-hidden="true">›</span>
		<a href="/indices">Índices</a>
		<span aria-hidden="true">›</span>
		<span>{item.codigo}</span>
	</nav>
	<p><a class="btn btn-primary" href={`/?modo=buscar&q=${item.codigo}`}>Buscar esta habilidade na Base</a></p>
	<h1>{item.codigo}: {item.anos_label ? item.anos_label : item.tipo_label}</h1>
	<CartaoDeAprendizagem {item} detail />
	{#if item.relacionados?.length}
		<h2>Itens relacionados</h2>
		<ul>
			{#each item.relacionados as rel}
				<li><a href={rel.url_path}>{rel.codigo}</a> — {rel.tipo_label}</li>
			{/each}
		</ul>
	{/if}
	<p><a href="/">Fazer outra busca</a></p>
</div>
