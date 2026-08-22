<script lang="ts">
	import CartaoDeAprendizagem from '$lib/components/CartaoDeAprendizagem.svelte';
	import MetasSociais from '$lib/components/MetasSociais.svelte';

	let { data } = $props();
	const item = $derived(data.item);
	const title = $derived(
		item.metadados_linha
			? `${item.codigo}: ${item.tipo_label} — ${item.metadados_linha} | Busca Base`
			: `${item.codigo}: ${item.tipo_label} | Busca Base`
	);
	const description = $derived(
		item.metadados_linha
			? `Consulte o texto oficial de ${item.codigo} na BNCC. Contexto: ${item.metadados_linha}.`
			: `Consulte o texto oficial de ${item.codigo} na BNCC.`
	);
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
</svelte:head>

<MetasSociais {title} {description} url={item.permalink} />

<div class="wrap reading">
	<nav class="breadcrumbs" aria-label="Trilha">
		<a href="/">Busca Base</a>
		<span aria-hidden="true">›</span>
		<span>{item.codigo}</span>
	</nav>
	<p><a class="btn btn-primary" href={`/?modo=buscar&q=${item.codigo}`}>Buscar esta habilidade na Base</a></p>
	<h1>{item.codigo}</h1>
	<CartaoDeAprendizagem {item} detail />
	<p><a href="/">Fazer outra busca</a></p>
</div>
