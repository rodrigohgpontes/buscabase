<script lang="ts">
	import logo from '$lib/assets/logo.png';
	// Temporário: seletor Calma/Folia oculto até o lançamento do tema.
	// import SeletorDeTema from '$lib/components/SeletorDeTema.svelte';

	let { home = true }: { home?: boolean } = $props();
</script>

<header class="site-header wrap">
	<a class="brand" href="/">
		<img class="brand-mark" src={logo} alt="" width="48" height="48" />
		Busca Base
	</a>
	<div class="header-tools">
		<!-- <SeletorDeTema /> -->
		{#if !home}
			<a class="btn btn-primary" href="/">Buscar na Base</a>
		{/if}
	</div>
</header>
