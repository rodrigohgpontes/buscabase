<script lang="ts">
	import { page } from '$app/state';

	let { children } = $props();

	const recados = $derived(page.url.pathname.startsWith('/uso/recados'));
</script>

<div class="wrap reading uso">
	<h1>Uso</h1>
	<p class="lede">Página restrita. Consultas e recados ficam gravados neste servidor.</p>
	<nav class="uso-nav" aria-label="Seções de uso">
		<a href="/uso" aria-current={recados ? undefined : 'page'}>Uso</a>
		<span aria-hidden="true">·</span>
		<a href="/uso/recados" aria-current={recados ? 'page' : undefined}>Recados</a>
	</nav>
	{@render children()}
</div>

<style>
	.uso {
		display: grid;
		gap: var(--space-4);
	}

	.lede {
		margin-bottom: 0;
	}

	.uso-nav {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
		align-items: baseline;
	}

	.uso-nav a {
		text-decoration: underline;
	}

	.uso-nav a[aria-current='page'] {
		font-weight: 700;
		text-decoration: none;
		color: var(--color-text);
	}
</style>
