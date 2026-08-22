<script lang="ts">
	import CartaoDeAprendizagem from '$lib/components/CartaoDeAprendizagem.svelte';
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { truncateText } from '$lib/social';

	let { data } = $props();
	const item = $derived(data.item);
	const title = $derived(`${item.tipo_label} ${item.codigo} na BNCC | Busca Base`);
	const description = $derived(truncateText(item.texto, 158));
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
		<a href="/indices#competencias">Competências</a>
		<span aria-hidden="true">›</span>
		<span>{item.codigo}</span>
	</nav>
	<p><a class="btn btn-primary" href="/">Buscar na Base</a></p>
	<h1>{item.tipo_label}</h1>
	<CartaoDeAprendizagem {item} detail />
	<p><a href="/">Fazer outra busca</a></p>
</div>
