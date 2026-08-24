<script lang="ts">
	import { page } from '$app/state';
	import Cabecalho from '$lib/components/Cabecalho.svelte';
	import Confete from '$lib/components/Confete.svelte';
	import Rodape from '$lib/components/Rodape.svelte';
	import WidgetDeRecado from '$lib/components/WidgetDeRecado.svelte';
	import { SITE_ORIGIN } from '$lib/social';
	import '$lib/styles/app.css';

	let { data, children } = $props();
	const isHome = $derived(page.url.pathname === '/');
	const mostrarRecado = $derived(!page.url.pathname.startsWith('/uso'));
</script>

<svelte:head>
	<meta property="og:site_name" content="Busca Base" />
	<link rel="canonical" href={`${SITE_ORIGIN}${page.url.pathname}`} />
</svelte:head>

<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
<Confete />
<div class="page">
	<Cabecalho home={isHome} />
	<main id="conteudo" class="site-main">
		{@render children()}
	</main>
	<Rodape recorte={data.recorte} perguntarAtivo={data.perguntar} />
</div>
{#if mostrarRecado}
	<WidgetDeRecado />
{/if}
