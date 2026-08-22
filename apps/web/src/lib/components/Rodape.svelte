<script lang="ts">
	import { getHealth } from '$lib/api';
	import { onMount } from 'svelte';

	let { recorte, perguntarAtivo = true }: { recorte?: string | null; perguntarAtivo?: boolean } =
		$props();
	let recorteCarregado = $state<string | null | undefined>(undefined);
	let perguntarCarregado = $state<boolean | undefined>(undefined);
	const recorteExibido = $derived(recorteCarregado !== undefined ? recorteCarregado : recorte);
	const perguntar = $derived(perguntarCarregado !== undefined ? perguntarCarregado : perguntarAtivo);

	onMount(async () => {
		if (recorte != null) return;
		try {
			const health = await getHealth();
			recorteCarregado = health.recorte;
			perguntarCarregado = health.perguntar;
		} catch {
			/* keep fallback */
		}
	});
</script>

<footer class="site-footer">
	<div class="wrap footer-grid">
		<section>
			<h2>Projeto</h2>
			<ul>
				<li><a href="/sobre">Sobre</a></li>
				<li><a href="/privacidade">Privacidade</a></li>
				<li><a href="/acessibilidade">Acessibilidade</a></li>
			</ul>
		</section>
		<section>
			<h2>Índices da Base</h2>
			<ul>
				<li><a href="/indices">Todos os índices</a></li>
				<li><a href="/indices#habilidades">Habilidades</a></li>
				<li><a href="/indices#etapas">Etapas</a></li>
				<li><a href="/indices#anos">Anos e faixas</a></li>
				<li><a href="/indices#areas">Áreas do conhecimento</a></li>
				<li><a href="/indices#componentes">Componentes curriculares</a></li>
				<li><a href="/indices#competencias">Competências</a></li>
				<li><a href="/indices#documentos">Documentos</a></li>
			</ul>
		</section>
		<section>
			<h2>Transparência</h2>
			<p>
				Recorte dos dados: {recorteExibido ?? 'ainda não carregado'}.
			</p>
			<p>
				Dados estruturados da BNCC por <a href="https://bncc.dev">bncc.dev</a> (CC BY 4.0), a partir
				dos documentos oficiais do MEC e do CNE. Recorte
				<code>{recorteExibido ?? '—'}</code>. Adaptações: indexação, busca e interface próprias.
			</p>
			<p>O Busca Base é um projeto independente e não é um site oficial do MEC.</p>
			{#if !perguntar}
				<p>
					Pesquisa conversacional está temporariamente indisponível. Pesquisa por código, Pesquisa
					por filtros e Pesquisa simples continuam disponíveis.
				</p>
			{/if}
		</section>
	</div>
</footer>
