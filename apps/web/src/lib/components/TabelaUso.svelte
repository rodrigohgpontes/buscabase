<script lang="ts">
	type Row = { valor: string | number; n: number };

	let {
		rows,
		rotulo,
		rotuloValor
	}: {
		rows: Row[] | null | undefined;
		rotulo: string;
		rotuloValor?: (valor: string | number) => string;
	} = $props();

	function vezes(n: number): string {
		return n.toLocaleString('pt-BR');
	}
</script>

{#if !rows?.length}
	<p class="help">Nada neste período.</p>
{:else}
	<table class="prose-table">
		<thead>
			<tr>
				<th scope="col">{rotulo}</th>
				<th scope="col">Vezes</th>
			</tr>
		</thead>
		<tbody>
			{#each rows as row (String(row.valor))}
				<tr>
					<td>{rotuloValor ? rotuloValor(row.valor) : String(row.valor)}</td>
					<td>{vezes(row.n)}</td>
				</tr>
			{/each}
		</tbody>
	</table>
{/if}
