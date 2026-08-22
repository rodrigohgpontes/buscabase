<script lang="ts">
	import { snippetText } from '$lib/answer';
	import type { FonteProse } from '$lib/types';

	let { trechos }: { trechos: FonteProse[] } = $props();
</script>

{#if trechos.length}
	<section class="trechos-da-base" aria-labelledby="trechos-da-base-titulo">
		<h2 id="trechos-da-base-titulo">Trechos da Base</h2>
		<p class="help">Passagens do documento oficial que também falam disso.</p>
		<ul>
			{#each trechos as trecho (trecho.block_id)}
				<li>
					<article class="trecho-card">
						<p class="meta card-label"><strong>Texto oficial (reconstrução)</strong></p>
						<p class="snip">{snippetText(trecho.texto)}</p>
						<p class="ctx">{trecho.documento}, p. {trecho.page}</p>
						<p>
							<a href={trecho.url_path}>Abrir na reconstrução</a>
						</p>
					</article>
				</li>
			{/each}
		</ul>
	</section>
{/if}
