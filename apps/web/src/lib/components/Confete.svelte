<script lang="ts">
	import { onMount } from 'svelte';
	import { lancarRajada } from '$lib/confetti-burst';
	import { EVENTO_FOLIA } from '$lib/theme';

	let canvas = $state<HTMLCanvasElement | undefined>();
	let ativo = $state(false);
	let parar: (() => void) | undefined;

	function encerrar() {
		parar?.();
		parar = undefined;
		ativo = false;
	}

	function disparar() {
		if (!canvas) return;
		encerrar();
		ativo = true;
		parar = lancarRajada(canvas, encerrar);
	}

	onMount(() => {
		window.addEventListener(EVENTO_FOLIA, disparar);
		return () => {
			window.removeEventListener(EVENTO_FOLIA, disparar);
			encerrar();
		};
	});

	const pecas = [
		{ x: '4%', dx: '9vw', rot: '-18deg', t: '13s', d: '-1s', s: '0.38rem' },
		{ x: '19%', dx: '-11vw', rot: '24deg', t: '16s', d: '-4s', s: '0.45rem' },
		{ x: '29%', dx: '7vw', rot: '8deg', t: '12s', d: '-8s', s: '0.52rem' },
		{ x: '39%', dx: '-8vw', rot: '-32deg', t: '15s', d: '-2s', s: '0.6rem' },
		{ x: '50%', dx: '12vw', rot: '14deg', t: '18s', d: '-11s', s: '0.68rem' },
		{ x: '70%', dx: '-10vw', rot: '-8deg', t: '14s', d: '-6s', s: '0.42rem' },
		{ x: '81%', dx: '6vw', rot: '28deg', t: '17s', d: '-9s', s: '0.55rem' },
		{ x: '92%', dx: '-12vw', rot: '-22deg', t: '11s', d: '-14s', s: '0.48rem' },
		{ x: '2%', dx: '8vw', rot: '16deg', t: '15s', d: '-3s', s: '0.38rem' },
		{ x: '12%', dx: '-9vw', rot: '-4deg', t: '13s', d: '-10s', s: '0.45rem' },
		{ x: '31%', dx: '11vw', rot: '36deg', t: '16s', d: '-5s', s: '0.52rem' },
		{ x: '41%', dx: '-7vw', rot: '-28deg', t: '12s', d: '-13s', s: '0.6rem' },
		{ x: '52%', dx: '10vw', rot: '-18deg', t: '18s', d: '-7s', s: '0.68rem' },
		{ x: '63%', dx: '-11vw', rot: '24deg', t: '14s', d: '-1s', s: '0.42rem' },
		{ x: '83%', dx: '5vw', rot: '8deg', t: '17s', d: '-8s', s: '0.55rem' },
		{ x: '94%', dx: '-13vw', rot: '-32deg', t: '11s', d: '-4s', s: '0.48rem' },
		{ x: '8%', dx: '9vw', rot: '14deg', t: '13s', d: '-12s', s: '0.38rem' },
		{ x: '14%', dx: '-8vw', rot: '-8deg', t: '16s', d: '-6s', s: '0.45rem' },
		{ x: '24%', dx: '7vw', rot: '28deg', t: '12s', d: '-9s', s: '0.52rem' },
		{ x: '43%', dx: '-10vw', rot: '-22deg', t: '15s', d: '-15s', s: '0.6rem' },
		{ x: '54%', dx: '12vw', rot: '16deg', t: '18s', d: '-2s', s: '0.68rem' },
		{ x: '65%', dx: '-6vw', rot: '-4deg', t: '14s', d: '-11s', s: '0.42rem' },
		{ x: '76%', dx: '8vw', rot: '36deg', t: '17s', d: '-5s', s: '0.55rem' },
		{ x: '96%', dx: '-9vw', rot: '-28deg', t: '11s', d: '-13s', s: '0.48rem' },
		{ x: '6%', dx: '10vw', rot: '-18deg', t: '15s', d: '-7s', s: '0.38rem' },
		{ x: '16%', dx: '-12vw', rot: '24deg', t: '13s', d: '-3s', s: '0.45rem' },
		{ x: '26%', dx: '6vw', rot: '8deg', t: '16s', d: '-10s', s: '0.52rem' },
		{ x: '36%', dx: '-8vw', rot: '-32deg', t: '12s', d: '-1s', s: '0.6rem' },
		{ x: '56%', dx: '11vw', rot: '14deg', t: '18s', d: '-14s', s: '0.68rem' },
		{ x: '67%', dx: '-7vw', rot: '-8deg', t: '14s', d: '-6s', s: '0.42rem' },
		{ x: '78%', dx: '9vw', rot: '28deg', t: '17s', d: '-12s', s: '0.55rem' },
		{ x: '89%', dx: '-11vw', rot: '-22deg', t: '11s', d: '-8s', s: '0.48rem' },
		{ x: '10%', dx: '8vw', rot: '16deg', t: '13s', d: '-4s', s: '0.38rem' },
		{ x: '18%', dx: '-10vw', rot: '-4deg', t: '16s', d: '-9s', s: '0.45rem' },
		{ x: '28%', dx: '7vw', rot: '36deg', t: '12s', d: '-2s', s: '0.52rem' },
		{ x: '38%', dx: '-9vw', rot: '-28deg', t: '15s', d: '-11s', s: '0.6rem' },
		{ x: '49%', dx: '12vw', rot: '-18deg', t: '18s', d: '-5s', s: '0.68rem' },
		{ x: '69%', dx: '-6vw', rot: '24deg', t: '14s', d: '-13s', s: '0.42rem' },
		{ x: '80%', dx: '10vw', rot: '8deg', t: '17s', d: '-7s', s: '0.55rem' },
		{ x: '91%', dx: '-8vw', rot: '-32deg', t: '11s', d: '-3s', s: '0.48rem' },
		{ x: '5%', dx: '9vw', rot: '14deg', t: '15s', d: '-10s', s: '0.38rem' },
		{ x: '20%', dx: '-11vw', rot: '-8deg', t: '13s', d: '-6s', s: '0.45rem' },
		{ x: '30%', dx: '6vw', rot: '28deg', t: '16s', d: '-14s', s: '0.52rem' },
		{ x: '40%', dx: '-12vw', rot: '-22deg', t: '12s', d: '-1s', s: '0.6rem' },
		{ x: '51%', dx: '8vw', rot: '16deg', t: '18s', d: '-8s', s: '0.68rem' },
		{ x: '62%', dx: '-7vw', rot: '-4deg', t: '14s', d: '-12s', s: '0.42rem' },
		{ x: '82%', dx: '11vw', rot: '36deg', t: '17s', d: '-4s', s: '0.55rem' },
		{ x: '93%', dx: '-9vw', rot: '-28deg', t: '11s', d: '-9s', s: '0.48rem' }
	];
</script>

<canvas class={['confetti-burst', ativo && 'is-on']} bind:this={canvas} aria-hidden="true"></canvas>
<div class="confetti" aria-hidden="true">
	{#each pecas as peca, i (i)}
		<span
			class="confetti-piece"
			style="--x:{peca.x};--dx:{peca.dx};--rot:{peca.rot};--t:{peca.t};--d:{peca.d};--s:{peca.s}"
		>
			<span class="confetti-flake"></span>
		</span>
	{/each}
</div>
