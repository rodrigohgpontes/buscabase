<script lang="ts">
	import { page } from '$app/state';
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { absoluteUrl } from '$lib/social';

	const ingles = /^(Not Found|Internal Error|Internal Server Error|Forbidden|Unauthorized)$/i;

	const titulo = $derived(
		page.error?.titulo ||
			(page.status === 404 ? 'Página não encontrada' : 'Não foi possível concluir agora')
	);
	const texto = $derived(
		page.error?.texto ||
			(page.error?.message && !ingles.test(page.error.message)
				? page.error.message
				: 'Sua consulta foi preservada. Tente novamente ou volte à busca.')
	);
	const title = $derived(`${titulo} | Busca Base`);
	const description = $derived(
		page.status === 404
			? 'Essa página não existe no Busca Base. Volte à busca para encontrar um item da BNCC.'
			: 'Não foi possível concluir agora. Tente de novo ou volte à busca.'
	);
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
</svelte:head>

<MetasSociais {title} {description} url={absoluteUrl(page.url.pathname)} noindex />

<div class="wrap reading">
	<h1>{titulo}</h1>
	<p>{texto}</p>
	<p><a class="btn btn-primary" href="/">Buscar na Base</a></p>
</div>
