<script lang="ts">
	import { onMount } from 'svelte';
	import { aplicarTema, lerTemaDoDocumento, TEMAS, TEMA_ROTULOS, type Tema } from '$lib/theme';

	let atual = $state<Tema>('calma');

	onMount(() => {
		atual = lerTemaDoDocumento();
	});

	function escolher(tema: Tema) {
		atual = tema;
		aplicarTema(tema);
	}
</script>

<div class="theme-toggle" role="group" aria-label="Aparência">
	{#each TEMAS as tema (tema)}
		<button
			type="button"
			class={['theme-option', atual === tema && 'is-selected']}
			aria-pressed={atual === tema}
			onclick={() => escolher(tema)}
		>
			{TEMA_ROTULOS[tema]}
		</button>
	{/each}
</div>
