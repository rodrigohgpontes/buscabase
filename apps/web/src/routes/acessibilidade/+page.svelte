<script lang="ts">
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { absoluteUrl } from '$lib/social';

	const title = 'Acessibilidade | Busca Base';
	const description =
		'Compromisso de acessibilidade do Busca Base, meta WCAG 2.2 nível AA e canal para relatar barreiras.';
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
</svelte:head>

<MetasSociais {title} {description} url={absoluteUrl('/acessibilidade')} />

<div class="wrap reading">
	<nav class="breadcrumbs" aria-label="Trilha">
		<a href="/">Busca Base</a>
		<span aria-hidden="true">›</span>
		<span>Acessibilidade</span>
	</nav>
	<h1>Acessibilidade</h1>
	<p>
		A meta do Busca Base é atender WCAG 2.2 nível AA, com atenção a celular, teclado e tecnologias
		assistivas.
	</p>
	<h2>O que já está no site</h2>
	<ul>
		<li>HTML semântico e rótulos visíveis;</li>
		<li>link para pular ao conteúdo;</li>
		<li>foco visível;</li>
		<li>contraste de texto e controles;</li>
		<li>respeito a movimento reduzido;</li>
		<li>páginas públicas úteis sem JavaScript.</li>
	</ul>
	<h2>Relatar uma barreira</h2>
	<p>
		Se algo impedir o uso, escreva para a equipe pelo repositório público do projeto no GitHub,
		descrevendo a página, o aparelho e o que aconteceu.
	</p>
	<p><a class="btn btn-primary" href="/">Buscar na Base</a></p>
</div>
