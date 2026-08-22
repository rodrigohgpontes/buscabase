<script lang="ts">
	import { afterNavigate, goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { getProseDocument, getProsePage } from '$lib/api';
	import Aviso from '$lib/components/Aviso.svelte';
	import DocumentoReconstruido from '$lib/components/DocumentoReconstruido.svelte';
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { officialDocumentLinks } from '$lib/document-links';
	import { blockIdFromHash, pageFromSearchParams, parseProseBlockId } from '$lib/document-hash';
	import { absoluteUrl } from '$lib/social';
	import type { ProseDocumentMeta, ProsePagePayload } from '$lib/types';

	let { data } = $props();
	const title = $derived(`${data.nome} | Busca Base`);
	const description = $derived(`Consulte o texto oficial de ${data.nome} no Busca Base.`);
	const url = $derived(absoluteUrl(`/documento/${data.slug}`));
	const payload = $derived((data.payload || {}) as Record<string, unknown>);
	const isArte = $derived(data.id === 'arte-2026' || data.slug === 'arte-2026');
	const linksOficiais = $derived(officialDocumentLinks(data.id));
	const tituloLinks = $derived(
		linksOficiais.length === 1 ? 'Documento oficial' : 'Documentos oficiais'
	);

	let proseMeta = $state<ProseDocumentMeta | null>(null);
	let pageData = $state<ProsePagePayload | null>(null);
	let currentPage = $state(1);
	let loadingProse = $state(true);
	let proseError = $state('');
	let alvoId = $state<string | null>(null);
	let pageField = $state('1');
	let prefetching = $state<number | null>(null);

	function targetFromUrl(): { page: number; blockId: string | null } {
		const hashId = blockIdFromHash(page.url.hash);
		if (hashId) {
			const parsed = parseProseBlockId(hashId);
			if (parsed) return { page: parsed.page, blockId: hashId };
		}
		return { page: pageFromSearchParams(page.url.searchParams), blockId: null };
	}

	async function loadPage(n: number, blockId: string | null) {
		loadingProse = true;
		proseError = '';
		try {
			pageData = await getProsePage(data.id, n);
			currentPage = n;
			pageField = String(n);
			alvoId = blockId;
		} catch {
			proseError = 'Não foi possível carregar a reconstrução.';
			pageData = null;
		} finally {
			loadingProse = false;
		}
	}

	async function ensureMeta() {
		if (proseMeta) return proseMeta;
		try {
			proseMeta = await getProseDocument(data.id);
			return proseMeta;
		} catch {
			proseMeta = null;
			loadingProse = false;
			return null;
		}
	}

	async function syncFromUrl() {
		const meta = await ensureMeta();
		if (!meta) return;
		const target = targetFromUrl();
		const next = Math.min(Math.max(target.page, 1), meta.page_count);
		if (pageData && currentPage === next && alvoId === target.blockId) return;
		await loadPage(next, target.blockId);
	}

	onMount(() => {
		void syncFromUrl();
	});

	afterNavigate(() => {
		void syncFromUrl();
	});

	$effect(() => {
		if (!alvoId || !pageData) return;
		const el = document.getElementById(alvoId);
		if (!el) return;
		const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
		el.classList.add('alvo');
		const timer = setTimeout(() => el.classList.remove('alvo'), 1600);
		return () => clearTimeout(timer);
	});

	$effect(() => {
		if (!proseMeta || currentPage >= proseMeta.page_count) return;
		const next = currentPage + 1;
		if (prefetching === next) return;
		prefetching = next;
		void getProsePage(data.id, next).catch(() => {});
	});

	function goPage(n: number) {
		if (!proseMeta || n < 1 || n > proseMeta.page_count || n === currentPage) return;
		const next = new URL(page.url);
		next.searchParams.set('pagina', String(n));
		void goto(`${next.pathname}${next.search}`, { noScroll: true, keepFocus: true });
	}

	function submitPage(event: Event) {
		event.preventDefault();
		const n = Number(pageField);
		if (!Number.isFinite(n)) return;
		goPage(Math.floor(n));
	}
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
	{@html `<script type="application/ld+json">${JSON.stringify({
		'@context': 'https://schema.org',
		'@type': 'Dataset',
		name: data.nome,
		url
	})}</script>`}
</svelte:head>

<MetasSociais {title} {description} {url} />

<div class="wrap reading">
	<nav class="atalhos-documento" aria-label="Atalhos desta página">
		{#if linksOficiais.length}
			<a href="#documento-oficial">Ir para o PDF oficial</a>
		{/if}
		{#if proseMeta}
			<a href="#reconstrucao">Ir para a reconstrução</a>
		{/if}
	</nav>
	<nav class="breadcrumbs" aria-label="Trilha">
		<a href="/">Busca Base</a>
		<span aria-hidden="true">›</span>
		<a href="/indices#documentos">Documentos</a>
		<span aria-hidden="true">›</span>
		<span>{data.nome}</span>
	</nav>
	<p><a class="btn btn-primary" href="/">Buscar na Base</a></p>
	<h1>{data.nome}</h1>
	<p>Recorte {data.recorte}.</p>
	{#if data.tipo}
		<p>Tipo: {data.tipo}{data.derivado_de ? ` · derivado de ${data.derivado_de}` : ''}.</p>
	{/if}
	{#if payload.parecer || payload.page_count}
		<p>
			{#if payload.parecer}{payload.parecer}.{/if}
			{#if payload.homologacao} Homologação: {payload.homologacao}.{/if}
			{#if payload.page_count} {payload.page_count} páginas no PDF oficial.{/if}
		</p>
	{/if}
	{#if linksOficiais.length}
		<section id="documento-oficial">
			<h2>{tituloLinks}</h2>
			<ul>
				{#each linksOficiais as link (link.href)}
					<li>
						<a href={link.href} target="_blank" rel="noopener noreferrer">
							{link.label}
							<span class="visually-hidden"> (abre em outra aba)</span>
						</a>
					</li>
				{/each}
			</ul>
		</section>
	{/if}

	{#if isArte && !data.items.length}
		<p>
			As habilidades e objetivos de Arte com código continuam os da BNCC 2018. O parecer aparece
			abaixo como reconstrução do PDF oficial.
		</p>
	{/if}

	{#if proseMeta}
		<section id="reconstrucao" class="reconstrucao">
			<h2>Reconstrução do PDF oficial</h2>
			<Aviso
				kind="atencao"
				titulo="Reconstrução não oficial"
				texto="Este texto reconstrói o PDF oficial para consulta. Pode estar desatualizado ou incompleto em relação ao arquivo homologado. Vale o ato oficial."
			/>
			<nav class="reconstrucao-nav" aria-label="Páginas da reconstrução">
				<p>Página {currentPage} de {proseMeta.page_count}</p>
				<div class="reconstrucao-acoes">
					<button
						class="btn btn-secondary"
						type="button"
						disabled={currentPage <= 1}
						onclick={() => goPage(currentPage - 1)}>Página anterior</button
					>
					<button
						class="btn btn-secondary"
						type="button"
						disabled={currentPage >= proseMeta.page_count}
						onclick={() => goPage(currentPage + 1)}>Próxima página</button
					>
				</div>
				<form class="ir-para-pagina" onsubmit={submitPage}>
					<label for="campo-pagina">Ir para a página</label>
					<input
						id="campo-pagina"
						name="pagina"
						type="number"
						min="1"
						max={proseMeta.page_count}
						bind:value={pageField}
					/>
					<button class="btn btn-secondary" type="submit">Ir</button>
				</form>
			</nav>
			{#if loadingProse && !pageData}
				<p role="status">Carregando a reconstrução…</p>
			{:else if proseError}
				<p role="status">{proseError}</p>
			{:else if pageData}
				<DocumentoReconstruido page={pageData} />
			{/if}
		</section>
	{/if}

	{#if data.items.length}
		<h2>Itens com código neste documento</h2>
		<ul>
			{#each data.items as item (item.codigo)}
				<li><a href={item.url_path}>{item.codigo}</a></li>
			{/each}
		</ul>
	{:else if !isArte}
		<p>Nenhum item neste recorte.</p>
	{/if}
	<p><a href="/">Fazer outra busca</a></p>
</div>
