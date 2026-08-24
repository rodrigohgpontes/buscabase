<script lang="ts">
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import TabelaUso from '$lib/components/TabelaUso.svelte';
	import { absoluteUrl } from '$lib/social';

	let { data } = $props();

	const title = 'Uso | Busca Base';
	const description = 'Resumo de uso do Busca Base. Página restrita.';

	const resumo = $derived(data.resumo);
	const visitas = $derived(resumo.visitas);
	const consultas = $derived(resumo.consultas);
	const como = $derived(resumo.como);
	const levar = $derived(resumo.levar);
	const origem = $derived(resumo.origem);
	const cachePct = $derived(
		consultas.cache_total
			? `${Math.round((consultas.cache_hits / consultas.cache_total) * 100)}%`
			: '—'
	);

	function vezes(n: number): string {
		return n.toLocaleString('pt-BR');
	}

	function rotuloModo(valor: string | number): string {
		const map: Record<string, string> = {
			codigo: 'Pesquisa por código',
			filtros: 'Pesquisa por filtros',
			buscar: 'Pesquisa simples',
			perguntar: 'Pesquisa conversacional',
			home: 'Início',
			home_consulta: 'Início com consulta',
			habilidade: 'Habilidade',
			indices: 'Índices',
			documento: 'Documento',
			dimensao: 'Dimensão',
			institucional: 'Institucional',
			outro: 'Outro',
			texto: 'Texto',
			texto_e_referencia: 'Texto e referência',
			link: 'Link',
			txt: '.txt',
			csv: '.csv',
			mobile: 'Celular',
			desktop: 'Computador'
		};
		return map[String(valor)] ?? String(valor);
	}
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
	<meta name="robots" content="noindex,nofollow" />
</svelte:head>

<MetasSociais {title} {description} url={absoluteUrl('/uso')} noindex />

<div class="uso-dashboard">
	<p class="help">
		Últimos {data.dias} dias. Visitantes do dia são estimados sem cookie.
	</p>
	<p class="help">
		Período:
		{#if data.dias === 7}
			7 dias · <a href="/uso?dias=30">30 dias</a>
		{:else}
			<a href="/uso?dias=7">7 dias</a> · 30 dias
		{/if}
	</p>

	<section>
		<h2>Neste período</h2>
		<table class="prose-table">
			<tbody>
				<tr>
					<th scope="row">Visitantes no dia</th>
					<td>{vezes(visitas.unicos)}</td>
				</tr>
				<tr>
					<th scope="row">Páginas</th>
					<td>{vezes(visitas.paginas)}</td>
				</tr>
				<tr>
					<th scope="row">Consultas</th>
					<td>{vezes(consultas.total)}</td>
				</tr>
				<tr>
					<th scope="row">Tempo (mediana / 95%)</th>
					<td>
						{consultas.p50_ms == null ? '—' : `${consultas.p50_ms} ms`} /
						{consultas.p95_ms == null ? '—' : `${consultas.p95_ms} ms`}
					</td>
				</tr>
				<tr>
					<th scope="row">Cache</th>
					<td
						>{cachePct} ({vezes(consultas.cache_hits)} de {vezes(consultas.cache_total)})</td
					>
				</tr>
				<tr>
					<th scope="row">Tokens de Perguntar</th>
					<td>{vezes(consultas.tokens_in)} entrada / {vezes(consultas.tokens_out)} saída</td>
				</tr>
				<tr>
					<th scope="row">Perguntar 429 / 503</th>
					<td>{vezes(consultas.perguntar_429)} / {vezes(consultas.perguntar_503)}</td>
				</tr>
			</tbody>
		</table>
	</section>

	<section>
		<h2>Como buscam</h2>
		<h3>Modos</h3>
		<TabelaUso rows={consultas.por_modo} rotulo="Modo" rotuloValor={rotuloModo} />
		<h3>Consultas mais feitas</h3>
		<TabelaUso rows={como.top_consultas} rotulo="Consulta" />
		<h3>Códigos encontrados</h3>
		<TabelaUso rows={como.top_codigos} rotulo="Código" />
		<h3>Sem resultado</h3>
		<TabelaUso rows={como.vazias} rotulo="Consulta" />
		<h3>Código inexistente</h3>
		<TabelaUso rows={como.codigo_404} rotulo="Código" />
		<h3>Código inválido</h3>
		<TabelaUso rows={como.codigo_400} rotulo="Código" />
		<h3>Filtros usados</h3>
		<TabelaUso rows={como.filtros.chaves} rotulo="Dimensão" />
		<TabelaUso rows={como.filtros.valores} rotulo="Valor" />
		<h3>Turnos de Perguntar</h3>
		<TabelaUso rows={como.perguntar_turnos} rotulo="Turno" />
	</section>

	<section>
		<h2>O que levam</h2>
		<table class="prose-table">
			<tbody>
				<tr>
					<th scope="row">Cópias</th>
					<td>{vezes(levar.copias)}</td>
				</tr>
				<tr>
					<th scope="row">Exportações</th>
					<td>{vezes(levar.exportacoes)}</td>
				</tr>
				<tr>
					<th scope="row">Compartilhamentos</th>
					<td>{vezes(levar.compartilhamentos)}</td>
				</tr>
			</tbody>
		</table>
		<TabelaUso rows={levar.por_copia} rotulo="Tipo de cópia" rotuloValor={rotuloModo} />
		<TabelaUso rows={levar.por_formato} rotulo="Formato" rotuloValor={rotuloModo} />
		<h3>Códigos exportados</h3>
		<TabelaUso rows={levar.top_exportados} rotulo="Código" />
	</section>

	<section>
		<h2>De onde vêm</h2>
		<TabelaUso rows={origem.referers} rotulo="Origem" />
		<TabelaUso rows={origem.landings} rotulo="Página" rotuloValor={rotuloModo} />
		<TabelaUso rows={origem.dispositivos} rotulo="Aparelho" rotuloValor={rotuloModo} />
	</section>
</div>

<style>
	.uso-dashboard {
		display: grid;
		gap: var(--space-8);
	}

	.uso-dashboard section {
		display: grid;
		gap: var(--space-4);
	}

	.uso-dashboard h3 {
		margin-top: var(--space-4);
	}
</style>
