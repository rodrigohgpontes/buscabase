<script lang="ts">
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { absoluteUrl } from '$lib/social';

	let { data } = $props();
</script>

<svelte:head>
	<title>Sobre o Busca Base | Busca Base</title>
	<meta
		name="description"
		content="O Busca Base é um projeto independente para encontrar, entender e reutilizar o texto da Base Nacional Comum Curricular (BNCC)."
	/>
	{@html `<script type="application/ld+json">${JSON.stringify({
		'@context': 'https://schema.org',
		'@type': 'Organization',
		name: 'Busca Base',
		url: 'https://www.buscabase.com.br'
	})}</script>`}
</svelte:head>

<MetasSociais
	title="Sobre o Busca Base | Busca Base"
	description="O Busca Base é um projeto independente para encontrar, entender e reutilizar o texto da Base Nacional Comum Curricular (BNCC)."
	url={absoluteUrl('/sobre')}
/>

<div class="wrap reading">
	<nav class="breadcrumbs" aria-label="Trilha">
		<a href="/">Busca Base</a>
		<span aria-hidden="true">›</span>
		<span>Sobre</span>
	</nav>
	<h1>Sobre o Busca Base</h1>
	<p>
		O Busca Base ajuda a encontrar, entender, conferir e reutilizar o que a Base Nacional Comum
		Curricular (BNCC) diz. É um site público e gratuito, em português brasileiro.
	</p>
	<p>O Busca Base é um projeto independente e não é um site oficial do MEC.</p>
	<h2>O que o site faz</h2>
	<ul>
		<li>abre um item pelo código, como EF05MA03;</li>
		<li>busca habilidades e outros itens por tema, etapa, ano e componente;</li>
		<li>quando disponível, explica e compara com respostas sustentadas por fontes.</li>
	</ul>
	<h2>Fonte dos dados</h2>
	<p>
		O único conjunto curricular é um recorte fixado do projeto bncc-dados. Recorte atual:
		<strong>{data.recorte ?? 'não informado'}</strong>.
	</p>
	<p>
		Dados estruturados da BNCC por <a href="https://bncc.dev">bncc.dev</a> (CC BY 4.0), a partir dos
		documentos oficiais do MEC e do CNE. Recorte <code>{data.recorte ?? '—'}</code>. Adaptações:
		indexação, busca e interface próprias.
	</p>
	<p>
		O recorte também inclui o complemento de Arte (Parecer CNE/CEB nº 2/2026), a partir do PDF
		oficial local. As habilidades e objetivos de Arte com código continuam os da BNCC 2018.
	</p>
	<p>
		O site reconstrói o texto de três PDFs oficiais para consulta: a BNCC 2018, o complemento de
		Computação e o parecer de Arte. O Perguntar pode usar esses trechos. O arquivo homologado no
		MEC ou no CNE prevalece.
	</p>
	<h2>Limites</h2>
	<p>
		A BNCC define aprendizagens essenciais. Ela não é um plano de aula nem um manual de metodologia.
		O Busca Base não inventa códigos e não altera o texto oficial.
	</p>
	<h2>Quem fez</h2>
	<p>O Busca Base foi feito por Rodrigo Pontes.</p>
	<p>
		<a href="https://www.linkedin.com/in/rodrigohgpontes">Perfil de Rodrigo Pontes no LinkedIn <em>(me contrate!)</em></a>.
	</p>
	<p>
		Contato: <a href="mailto:contato@rodrigopontes.com.br">contato@rodrigopontes.com.br</a>.
	</p>
	<p>
		O código é aberto:
		<a href="https://github.com/rodrigohgpontes/buscabase">repositório do Busca Base no GitHub</a>.
	</p>
	<p><a class="btn btn-primary" href="/">Buscar na Base</a></p>
</div>
