<script lang="ts">
	import Aviso from '$lib/components/Aviso.svelte';
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { absoluteUrl } from '$lib/social';
	import type { TaxOption } from '$lib/types';

	let { data } = $props();
	const tax = $derived(data.taxonomias);
	const gerais = $derived((tax?.competencias || []).filter((c) => c.tipo === 'competencia_geral'));
	const especificas = $derived(
		(tax?.competencias || []).filter((c) => c.tipo === 'competencia_especifica')
	);

	function resumo(texto: string, max = 90) {
		if (texto.length <= max) return texto;
		return `${texto.slice(0, max - 1).trimEnd()}…`;
	}

	function listaVazia(items: TaxOption[] | undefined) {
		return !items?.length;
	}
</script>

<svelte:head>
	<title>Índices da BNCC | Busca Base</title>
	<meta
		name="description"
		content="Acesso às páginas estáveis de habilidades, etapas, anos, áreas, componentes, competências e documentos da BNCC no Busca Base."
	/>
</svelte:head>

<MetasSociais
	title="Índices da BNCC | Busca Base"
	description="Acesso às páginas estáveis de habilidades, etapas, anos, áreas, componentes, competências e documentos da BNCC no Busca Base."
	url={absoluteUrl('/indices')}
/>

<div class="wrap reading">
	<nav class="breadcrumbs" aria-label="Trilha">
		<a href="/">Busca Base</a>
		<span aria-hidden="true">›</span>
		<span>Índices</span>
	</nav>
	<p><a class="btn btn-primary" href="/">Buscar na Base</a></p>
	<h1>Índices da Base</h1>
	<p>Recorte {data.tag ?? 'ainda não carregado'}.</p>

	{#if !tax}
		<Aviso
			kind="atencao"
			titulo="Os índices ainda não puderam ser carregados."
			texto="O recorte pode estar em ingestão. Tente de novo em instantes ou volte à busca."
		/>
	{/if}

	<section id="etapas">
		<h2>Etapas</h2>
		{#if listaVazia(tax?.etapas)}
			<p>Nenhuma etapa neste recorte.</p>
		{:else}
			<ul>
				{#each tax?.etapas || [] as etapa}
					<li><a href={`/etapa/${etapa.slug}`}>{etapa.nome}</a></li>
				{/each}
			</ul>
		{/if}
	</section>
	<section id="anos">
		<h2>Anos e faixas</h2>
		{#if listaVazia(tax?.anos)}
			<p>Nenhum ano ou faixa neste recorte.</p>
		{:else}
			<ul>
				{#each tax?.anos || [] as ano}
					<li><a href={`/ano/${ano.slug}`}>{ano.nome}</a></li>
				{/each}
			</ul>
		{/if}
	</section>
	<section id="areas">
		<h2>Áreas do conhecimento</h2>
		{#if listaVazia(tax?.areas)}
			<p>Nenhuma área neste recorte.</p>
		{:else}
			<ul>
				{#each tax?.areas || [] as area}
					<li><a href={`/area/${area.slug}`}>{area.nome}</a></li>
				{/each}
			</ul>
		{/if}
	</section>
	<section id="componentes">
		<h2>Componentes curriculares</h2>
		{#if listaVazia(tax?.componentes)}
			<p>Nenhum componente neste recorte.</p>
		{:else}
			<ul>
				{#each tax?.componentes || [] as comp}
					<li><a href={`/componente/${comp.slug}`}>{comp.nome}</a></li>
				{/each}
			</ul>
		{/if}
	</section>
	<section id="documentos">
		<h2>Documentos</h2>
		{#if listaVazia(tax?.documentos)}
			<p>Nenhum documento neste recorte.</p>
		{:else}
			<ul>
				{#each tax?.documentos || [] as doc}
					<li><a href={`/documento/${doc.slug}`}>{doc.nome}</a></li>
				{/each}
			</ul>
		{/if}
	</section>
	<section id="competencias">
		<h2>Competências</h2>
		<h3>Competências gerais da BNCC</h3>
		{#if listaVazia(gerais)}
			<p>Nenhuma competência geral neste recorte.</p>
		{:else}
			<ul>
				{#each gerais as comp}
					<li>
						<a href={`/competencia/${comp.id}`}>{comp.id}</a>
						— {resumo(comp.nome)}
					</li>
				{/each}
			</ul>
		{/if}
		<h3>Competências específicas</h3>
		{#if listaVazia(especificas)}
			<p>Nenhuma competência específica neste recorte.</p>
		{:else}
			<ul>
				{#each especificas as comp}
					<li>
						<a href={`/competencia/${comp.id}`}>{comp.id}</a>
						— {resumo(comp.nome)}
					</li>
				{/each}
			</ul>
		{/if}
	</section>
	<section id="habilidades">
		<h2>Habilidades</h2>
		<p>Abra um código na home ou use os índices de ano e componente.</p>
	</section>
	<p><a href="/">Fazer outra busca</a></p>
</div>
