<script lang="ts">
	import AcoesDeResultado from '$lib/components/AcoesDeResultado.svelte';
	import type { Item } from '$lib/types';

	let {
		item,
		selectable = false,
		selected = false,
		onToggle,
		perguntarAtivo = true,
		onPerguntar,
		detail = false
	}: {
		item: Item;
		selectable?: boolean;
		selected?: boolean;
		onToggle?: () => void;
		perguntarAtivo?: boolean;
		onPerguntar?: (item: Item) => void;
		detail?: boolean;
	} = $props();
</script>

<article class={['card', selected && 'selected']} aria-labelledby={`item-${item.codigo}`}>
	<header class="card-head">
		{#if selectable}
			<label class={['select-item', selected && 'is-checked']}>
				<input
					class="visually-hidden"
					type="checkbox"
					checked={selected}
					onchange={onToggle}
					aria-label={`Selecionar ${item.codigo}`}
				/>
				<span class="select-box" aria-hidden="true"></span>
				<span class="select-label">{selected ? 'Selecionado' : 'Selecionar'}</span>
			</label>
		{/if}
		<div>
			<p class="code" id={`item-${item.codigo}`}>
				<span class="visually-hidden">{item.tipo_label} </span>{item.codigo}
			</p>
			<p class="meta">{item.tipo_label}</p>
		</div>
	</header>
	<p class="meta card-label"><strong>Texto da BNCC</strong></p>
	<p class="oficial">{item.texto}</p>
	<p class="meta">{item.metadados_linha}</p>
	{#if detail && item.objetos?.length}
		<p class="meta">
			Objeto de conhecimento: {item.objetos.map((o) => o.nome).filter(Boolean).join('; ')}
		</p>
	{/if}
	<p class="meta">
		Fonte: {item.documento}{item.pagina_pdf ? `, ${item.pagina_pdf}` : ''}. Vigência: {item.vigencia
			.status}. Recorte {item.recorte}.
	</p>
	<AcoesDeResultado {item} {perguntarAtivo} {onPerguntar} />
	<p><a href={item.url_path}>Link permanente de {item.codigo}</a></p>
</article>
