<script lang="ts">
	import { afterNavigate, goto } from '$app/navigation';
	import { page } from '$app/state';
	import { search } from '$lib/api';
	import BarraDeSelecao from '$lib/components/BarraDeSelecao.svelte';
	import CampoDeBusca from '$lib/components/CampoDeBusca.svelte';
	import CampoPorCodigo from '$lib/components/CampoPorCodigo.svelte';
	import CampoPorFiltros from '$lib/components/CampoPorFiltros.svelte';
	import CartaoDeAprendizagem from '$lib/components/CartaoDeAprendizagem.svelte';
	import RecortesInferidos from '$lib/components/RecortesInferidos.svelte';
	import EstadoDeEspera from '$lib/components/EstadoDeEspera.svelte';
	import FontesDaResposta from '$lib/components/FontesDaResposta.svelte';
	import TrechosDaBase from '$lib/components/TrechosDaBase.svelte';
	import ModalDeCompartilhar from '$lib/components/ModalDeCompartilhar.svelte';
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { normalizeCitations } from '$lib/answer';
	import RespostaGerada from '$lib/components/RespostaGerada.svelte';
	import SecaoPerguntar from '$lib/components/SecaoPerguntar.svelte';
	import Aviso from '$lib/components/Aviso.svelte';
	import AcoesDeResposta from '$lib/components/AcoesDeResposta.svelte';
	import { formatCount } from '$lib/format';
	import { stripInferredPhrase } from '$lib/inferred';
	import {
		conversationShareUrl,
		conversaFromHash,
		decodeConversation
	} from '$lib/conversation-share';
	import { conversationHistory } from '$lib/conversation-history';
	import {
		appliedChips,
		emptyFilterReason,
		hasFilterScope as selectionHasScope,
		pruneSelection
	} from '$lib/filters';
	import {
		parseSearchUrl,
		SEARCH_API_MAX_LIMIT,
		SEARCH_PAGE_SIZE,
		searchUrlEquals,
		serializeSearchUrl,
		visibleCount,
		type SearchUrlState
	} from '$lib/search-url';
	import { shareConversationText, shareSearchText } from '$lib/share';
	import {
		HOME_DESCRIPTION,
		HOME_TITLE,
		absoluteUrl,
		searchSharePreview
	} from '$lib/social';
	import type { CitedSource, Fonte, FonteProse, InferredChip, Item } from '$lib/types';

	let { data } = $props();

	type Mode = 'codigo' | 'filtros' | 'buscar' | 'perguntar';

	let focused = $state(false);
	let active = $state<Mode | null>(null);
	let codigo = $state('');
	let busca = $state('');
	let pergunta = $state('');
	let etapas = $state<string[]>([]);
	let anos = $state<string[]>([]);
	let componentes = $state<string[]>([]);
	let areas = $state<string[]>([]);
	let campos = $state<string[]>([]);
	let documentos = $state<string[]>([]);
	let tipos = $state<string[]>([]);
	let incluirRevogados = $state(false);
	let loading = $state('');
	let error = $state<{ titulo: string; texto: string } | null>(null);
	let codigoItem = $state<Item | null>(null);
	let resultados = $state<Item[]>([]);
	let trechos = $state<FonteProse[]>([]);
	let inferred = $state<InferredChip[]>([]);
	let total = $state(0);
	let selected = $state<Item[]>([]);
	type ConversationTurn = {
		role: 'user' | 'assistant';
		text: string;
		/** Fontes citadas na resposta final, com o número [n] usado no texto. */
		citedSources?: CitedSource[];
		incompleta?: boolean;
	};

	let conversation = $state<ConversationTurn[]>([]);
	let statusPergunta = $state('');
	let perguntarBusy = $state(false);
	let abort: AbortController | null = null;
	let live = $state('');
	let shareOpen = $state(false);
	let shareUrl = $state('');
	let shareKind = $state<'search' | 'conversa'>('search');
	let shareAviso = $state('');
	let searchGen = 0;
	let followUp = $state('');

	const MAX_USER_TURNS = 4;
	const MAX_FOLLOW_UPS = 3;

	const perguntarAtivo = $derived(data.perguntar !== false);
	const codigoAberto = $derived(active === null || active === 'codigo');
	const filtrosAberto = $derived(active === null || active === 'filtros');
	const buscarAberto = $derived(active === null || active === 'buscar');
	const perguntarAberto = $derived(active === null || active === 'perguntar');

	function filterSelection() {
		return {
			etapas,
			anos,
			componentes,
			areas,
			campos,
			documentos,
			tipos,
			incluirRevogados
		};
	}

	function hasFilterScope() {
		return selectionHasScope(filterSelection());
	}

	function filtrosShareState(n: number | null): Extract<SearchUrlState, { mode: 'filtros' }> {
		return { mode: 'filtros', ...filterSelection(), n };
	}

	function activate(mode: Mode) {
		if (active !== mode) active = mode;
	}

	function searchError(err: unknown) {
		const detail = (err as { detail?: { titulo?: string; texto?: string } }).detail;
		return {
			titulo: detail?.titulo || 'A conexão foi interrompida.',
			texto: detail?.texto || 'Sua busca foi preservada. Verifique a internet e tente novamente.'
		};
	}

	function paramsFromFilters() {
		const params = new URLSearchParams();
		for (const e of etapas) params.append('etapa', e);
		for (const a of anos) params.append('ano', a);
		for (const c of componentes) params.append('componente', c);
		for (const ar of areas) params.append('area', ar);
		for (const campo of campos) params.append('campo', campo);
		for (const doc of documentos) params.append('documento', doc);
		for (const t of tipos) params.append('tipo', t);
		if (incluirRevogados) params.set('incluir_revogados', 'true');
		return params;
	}

	function currentShareState(): SearchUrlState | null {
		if (active === 'codigo') {
			const q = codigo.trim();
			return q ? { mode: 'codigo', codigo: q } : null;
		}
		if (active === 'buscar') {
			const q = busca.trim();
			return q ? { mode: 'buscar', q, n: visibleCount(resultados.length) } : null;
		}
		if (active === 'filtros') {
			return filtrosShareState(visibleCount(resultados.length));
		}
		if (active === 'perguntar') {
			return { mode: 'perguntar', pergunta: pergunta.trim() };
		}
		return null;
	}

	function syncUrl(state: SearchUrlState) {
		if (searchUrlEquals(parseSearchUrl(page.url.searchParams), state)) return;
		goto(`/?${serializeSearchUrl(state).toString()}`, {
			keepFocus: true,
			noScroll: true,
			replaceState: false
		});
	}

	async function loadPagedSearch(base: URLSearchParams, offset: number, count: number) {
		const items: Item[] = [];
		let fetchedTrechos: FonteProse[] = [];
		let fetchedInferred: InferredChip[] = [];
		let fetchedTotal = 0;
		let loaded = 0;
		while (loaded < count) {
			const params = new URLSearchParams(base);
			const limit = Math.min(SEARCH_API_MAX_LIMIT, count - loaded);
			params.set('offset', String(offset + loaded));
			params.set('limit', String(limit));
			const dataSearch = await search(params);
			fetchedTotal = dataSearch.total;
			items.push(...dataSearch.items);
			if (offset + loaded === 0) {
				fetchedTrechos = dataSearch.trechos || [];
				fetchedInferred = dataSearch.inferred || [];
			}
			loaded += dataSearch.items.length;
			if (!dataSearch.items.length || offset + loaded >= fetchedTotal) break;
		}
		return { items, total: fetchedTotal, trechos: fetchedTrechos, inferred: fetchedInferred };
	}

	async function runBuscar(
		q: string,
		append = false,
		opts?: { writeUrl?: boolean; n?: number | null }
	) {
		const writeUrl = opts?.writeUrl !== false;
		focused = true;
		active = 'buscar';
		if (!q.trim()) {
			error = {
				titulo: 'Digite o que você procura.',
				texto: 'Na pesquisa simples, use um tema, um ano ou um componente.'
			};
			resultados = [];
			trechos = [];
			inferred = [];
			if (writeUrl) syncUrl({ mode: 'buscar', q, n: null });
			return;
		}
		error = null;
		if (!append) {
			resultados = [];
			trechos = [];
			inferred = [];
			selected = [];
			conversation = [];
		}
		loading = 'Buscando na Base…';
		const gen = ++searchGen;
		if (writeUrl && !append) syncUrl({ mode: 'buscar', q, n: null });
		try {
			const params = new URLSearchParams();
			params.set('q', q);
			const count = append ? SEARCH_PAGE_SIZE : (opts?.n ?? SEARCH_PAGE_SIZE);
			const offset = append ? resultados.length : 0;
			const dataSearch = await loadPagedSearch(params, offset, count);
			if (gen !== searchGen) return;
			resultados = append ? [...resultados, ...dataSearch.items] : dataSearch.items;
			if (!append) {
				trechos = dataSearch.trechos;
				inferred = dataSearch.inferred;
			}
			total = dataSearch.total;
			live = formatCount(total);
			if (writeUrl && append) {
				syncUrl({ mode: 'buscar', q, n: visibleCount(resultados.length) });
			}
		} catch (err) {
			if (gen !== searchGen) return;
			error = searchError(err);
		} finally {
			if (gen === searchGen) loading = '';
		}
	}

	async function runFiltros(append = false, opts?: { writeUrl?: boolean; n?: number | null }) {
		const writeUrl = opts?.writeUrl !== false;
		focused = true;
		active = 'filtros';
		error = null;
		if (!hasFilterScope()) {
			error = {
				titulo: 'Escolha ao menos um recorte.',
				texto: 'A pesquisa por filtros percorre a Base a partir da etapa, do ano, do componente, do campo ou do tipo que você marcar.'
			};
			resultados = [];
			if (writeUrl) {
				syncUrl(filtrosShareState(null));
			}
			return;
		}
		if (!append) {
			resultados = [];
			selected = [];
			conversation = [];
		}
		loading = 'Buscando na Base…';
		const gen = ++searchGen;
		if (writeUrl && !append) {
			syncUrl(filtrosShareState(null));
		}
		try {
			const count = append ? SEARCH_PAGE_SIZE : (opts?.n ?? SEARCH_PAGE_SIZE);
			const offset = append ? resultados.length : 0;
			const dataSearch = await loadPagedSearch(paramsFromFilters(), offset, count);
			if (gen !== searchGen) return;
			resultados = append ? [...resultados, ...dataSearch.items] : dataSearch.items;
			total = dataSearch.total;
			live = formatCount(total);
			if (writeUrl && append) {
				syncUrl(filtrosShareState(visibleCount(resultados.length)));
			}
		} catch (err) {
			if (gen !== searchGen) return;
			error = searchError(err);
		} finally {
			if (gen === searchGen) loading = '';
		}
	}

	function patchDraft(index: number, patch: Partial<ConversationTurn>) {
		const draft = conversation[index];
		if (!draft || draft.role !== 'assistant') return;
		conversation[index] = { ...draft, ...patch };
	}

	function goToFonte(turnIndex: number, n: number) {
		const el = document.getElementById(`fonte-${turnIndex}-${n}`);
		if (!el) return;
		if (el instanceof HTMLDetailsElement) el.open = true;
		el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
	}

	async function runPerguntar(q: string) {
		const trimmed = q.trim();
		const userTurns = conversation.filter((t) => t.role === 'user').length;
		if (!perguntarAtivo || !trimmed || perguntarBusy) return;
		if (userTurns >= MAX_USER_TURNS) return;
		focused = true;
		active = 'perguntar';
		error = null;
		selected = [];
		// Prior turns only — the question being sent is not in historico yet.
		const historico = conversationHistory(conversation);
		pergunta = '';
		followUp = '';
		conversation = [
			...conversation,
			{ role: 'user', text: trimmed },
			{ role: 'assistant', text: '', citedSources: [] }
		];
		const draftIndex = conversation.length - 1;
		perguntarBusy = true;
		statusPergunta = 'Procurando trechos na Base…';
		syncUrl({ mode: 'perguntar', pergunta: trimmed });
		abort?.abort();
		abort = new AbortController();
		try {
			const response = await fetch('/api/perguntar', {
				method: 'POST',
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify({
					pergunta: trimmed,
					historico
				}),
				signal: abort.signal
			});
			if (response.status === 503) {
				error = {
					titulo: 'Pesquisa conversacional está temporariamente indisponível.',
					texto: 'Você ainda pode encontrar e copiar itens usando Pesquisa por código, Pesquisa por filtros ou Pesquisa simples.'
				};
				conversation = conversation.slice(0, -2);
				pergunta = trimmed;
				statusPergunta = '';
				return;
			}
			if (response.status === 429) {
				error = {
					titulo: 'Você atingiu o limite de perguntas deste período.',
					texto: 'Pesquisa por código, Pesquisa por filtros e Pesquisa simples continuam disponíveis.'
				};
				conversation = conversation.slice(0, -2);
				pergunta = trimmed;
				statusPergunta = '';
				return;
			}
			const reader = response.body?.getReader();
			if (!reader) return;
			const decoder = new TextDecoder();
			let buffer = '';
			let answer = '';
			let sources: Fonte[] = [];
			let sawToken = false;
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;
				buffer += decoder.decode(value, { stream: true });
				const parts = buffer.split('\n\n');
				buffer = parts.pop() || '';
				for (const part of parts) {
					const event = part.match(/^event: (.+)$/m)?.[1];
					const payload = part.match(/^data: (.+)$/m)?.[1];
					if (!event || !payload) continue;
					const json = JSON.parse(payload);
					if (event === 'status') {
						if (!sawToken) statusPergunta = json.texto;
					}
					if (event === 'sources') {
						sources = json.sources || [];
					}
					if (event === 'token') {
						answer += json.text;
						sawToken = true;
						statusPergunta = '';
						patchDraft(draftIndex, { text: answer });
					}
					if (event === 'complete') {
						answer = json.resposta || answer;
						sources = json.sources || sources;
						const normalized = normalizeCitations(answer, sources);
						patchDraft(draftIndex, {
							text: normalized.text,
							citedSources: normalized.sources,
							incompleta: Boolean(json.incompleta)
						});
					}
					if (event === 'cancelled') {
						patchDraft(draftIndex, {
							text: json.resposta || answer,
							incompleta: true
						});
						statusPergunta =
							'Pergunta cancelada. O texto continua no campo para você editar ou tentar de novo.';
						pergunta = trimmed;
					}
					if (event === 'error') {
						if (json.resposta || answer) {
							patchDraft(draftIndex, {
								text: json.resposta || answer,
								incompleta: true
							});
						}
						error = {
							titulo: json.mensagem || 'Não foi possível concluir a busca agora.',
							texto: json.codigo_atendimento
								? `Código de atendimento: ${json.codigo_atendimento}`
								: 'Sua consulta foi preservada. Tente novamente.'
						};
					}
				}
			}
			live = 'Resposta concluída.';
		} catch (err) {
			if ((err as Error).name === 'AbortError') {
				patchDraft(draftIndex, { incompleta: true });
				statusPergunta =
					'Pergunta cancelada. O texto continua no campo para você editar ou tentar de novo.';
				pergunta = trimmed;
			} else {
				error = {
					titulo: 'A conexão foi interrompida.',
					texto: 'Sua busca foi preservada. Verifique a internet e tente novamente.'
				};
			}
		} finally {
			perguntarBusy = false;
			if (statusPergunta === 'Resposta em andamento') statusPergunta = '';
		}
	}

	function novaConsulta() {
		focused = false;
		active = null;
		error = null;
		codigoItem = null;
		resultados = [];
		trechos = [];
		inferred = [];
		selected = [];
		conversation = [];
		statusPergunta = '';
		perguntarBusy = false;
		followUp = '';
		live = '';
		shareOpen = false;
		shareUrl = '';
		shareKind = 'search';
		shareAviso = '';
		loading = '';
		searchGen += 1;
		abort?.abort();
		goto('/', { keepFocus: true, noScroll: true });
	}

	function sharedConversationEncoded(): string | null {
		if (typeof window === 'undefined') return null;
		return conversaFromHash(window.location.hash);
	}

	async function applySharedConversation(encoded: string) {
		const decoded = await decodeConversation(encoded);
		if (!decoded) return;
		focused = true;
		active = 'perguntar';
		error = null;
		codigoItem = null;
		resultados = [];
		trechos = [];
		inferred = [];
		selected = [];
		conversation = decoded.turns;
		statusPergunta = '';
		perguntarBusy = false;
		followUp = '';
		loading = '';
		live = '';
		abort?.abort();
	}

	function restoreFromUrl(state: SearchUrlState) {
		if (state.mode === 'perguntar') {
			pergunta = state.pergunta;
			focused = true;
			active = 'perguntar';
			error = null;
			codigoItem = null;
			resultados = [];
			selected = [];
			conversation = [];
			statusPergunta = '';
			perguntarBusy = false;
			followUp = '';
			loading = '';
			live = '';
			abort?.abort();
			return;
		}
		if (state.mode === 'codigo') {
			codigo = state.codigo;
			activate('codigo');
			return;
		}
		if (state.mode === 'buscar') {
			busca = state.q;
			void runBuscar(state.q, false, { writeUrl: false, n: state.n });
			return;
		}
		const restored = data.taxonomias ? pruneSelection(state, data.taxonomias) : state;
		etapas = restored.etapas;
		anos = restored.anos;
		componentes = restored.componentes;
		areas = restored.areas;
		campos = restored.campos;
		documentos = restored.documentos;
		tipos = restored.tipos;
		incluirRevogados = restored.incluirRevogados;
		void runFiltros(false, { writeUrl: false, n: state.n });
	}

	afterNavigate(() => {
		if (page.url.pathname !== '/') return;
		const encoded = sharedConversationEncoded();
		if (encoded) {
			void applySharedConversation(encoded);
			return;
		}
		const parsed = parseSearchUrl(page.url.searchParams);
		if (active === 'perguntar' && conversation.length && parsed?.mode === 'perguntar') {
			return;
		}
		if (searchUrlEquals(parsed, currentShareState())) return;
		if (!parsed) {
			if (focused || active) {
				focused = false;
				active = null;
				error = null;
				codigoItem = null;
				resultados = [];
				trechos = [];
				inferred = [];
				selected = [];
				conversation = [];
				statusPergunta = '';
				perguntarBusy = false;
				followUp = '';
				loading = '';
				live = '';
				shareOpen = false;
				shareUrl = '';
				shareAviso = '';
				searchGen += 1;
				abort?.abort();
			}
			return;
		}
		restoreFromUrl(parsed);
	});

	const SELECTION_LIMIT = 50;

	function toggleSelect(item: Item) {
		if (selected.some((s) => s.codigo === item.codigo)) {
			selected = selected.filter((s) => s.codigo !== item.codigo);
			return;
		}
		if (selected.length >= SELECTION_LIMIT) {
			live = 'O limite é de 50 itens.';
			return;
		}
		selected = [...selected, item];
	}

	function selectAll() {
		const codes = new Set(selected.map((s) => s.codigo));
		const remaining = resultados.filter((item) => !codes.has(item.codigo));
		const slots = SELECTION_LIMIT - selected.length;
		if (slots <= 0) {
			live = 'O limite é de 50 itens.';
			return;
		}
		const added = remaining.slice(0, slots);
		if (!added.length) return;
		selected = [...selected, ...added];
		if (remaining.length > added.length) {
			live = 'O limite é de 50 itens.';
			return;
		}
		live = selected.length === 1 ? '1 item selecionado.' : `${selected.length} itens selecionados.`;
	}

	function perguntarSobre(item: Item) {
		pergunta = `Explique ${item.codigo} em palavras mais simples`;
		active = 'perguntar';
		focused = true;
	}

	function moreResults() {
		if (active === 'filtros') runFiltros(true);
		else runBuscar(busca, true);
	}

	function removeInferred(chip: InferredChip) {
		const next = stripInferredPhrase(busca, chip.phrase);
		busca = next;
		if (!next) {
			resultados = [];
			trechos = [];
			inferred = [];
			total = 0;
			return;
		}
		runBuscar(next);
	}

	const mostrandoCodigo = $derived(Boolean(codigoItem && active === 'codigo'));
	const mostrandoBuscaVazia = $derived(
		!loading &&
			!error &&
			!resultados.length &&
			focused &&
			((active === 'buscar' && Boolean(busca)) || active === 'filtros')
	);
	const mostrandoLista = $derived(
		Boolean(resultados.length && (active === 'buscar' || active === 'filtros'))
	);
	const avisoFiltrosVazio = $derived(
		emptyFilterReason(filterSelection(), data.taxonomias || {
			etapas: [],
			anos: [],
			componentes: [],
			areas: [],
			campos: [],
			documentos: [],
			tipos: []
		})
	);
	const chipsFiltros = $derived(
		appliedChips({
			...filterSelection(),
			tax: {
				etapas: data.taxonomias?.etapas || [],
				anos: data.taxonomias?.anos || [],
				componentes: data.taxonomias?.componentes || [],
				areas: data.taxonomias?.areas || [],
				campos: data.taxonomias?.campos || [],
				documentos: data.taxonomias?.documentos || [],
				tipos: data.taxonomias?.tipos || []
			}
		})
	);

	function limparFiltros() {
		etapas = [];
		anos = [];
		componentes = [];
		areas = [];
		campos = [];
		documentos = [];
		tipos = [];
		incluirRevogados = false;
	}

	function retirarUltimoFiltro() {
		const last =
			[...chipsFiltros].reverse().find((chip) => chip.kind !== 'revogados') || chipsFiltros.at(-1);
		if (!last) {
			limparFiltros();
			return;
		}
		if (last.kind === 'etapa') etapas = etapas.filter((id) => id !== last.id);
		else if (last.kind === 'ano') anos = anos.filter((id) => id !== last.id);
		else if (last.kind === 'campo') campos = campos.filter((id) => id !== last.id);
		else if (last.kind === 'area') areas = areas.filter((id) => id !== last.id);
		else if (last.kind === 'componente') componentes = componentes.filter((id) => id !== last.id);
		else if (last.kind === 'documento') documentos = documentos.filter((id) => id !== last.id);
		else if (last.kind === 'tipo') tipos = tipos.filter((id) => id !== last.id);
		else incluirRevogados = false;
	}
	const userTurnCount = $derived(conversation.filter((t) => t.role === 'user').length);
	const followUpsLeft = $derived(Math.max(0, MAX_FOLLOW_UPS - Math.max(0, userTurnCount - 1)));
	const mostrandoPergunta = $derived(
		active === 'perguntar' && Boolean(statusPergunta || conversation.length || perguntarBusy)
	);
	const podeContinuarPergunta = $derived(
		active === 'perguntar' &&
			perguntarAtivo &&
			conversation.length > 0 &&
			!perguntarBusy &&
			userTurnCount < MAX_USER_TURNS
	);
	const conversaNoLimite = $derived(
		active === 'perguntar' && conversation.length > 0 && !perguntarBusy && userTurnCount >= MAX_USER_TURNS
	);
	const temConteudoResultados = $derived(
		Boolean(
			loading ||
				error ||
				selected.length ||
				mostrandoCodigo ||
				mostrandoBuscaVazia ||
				mostrandoLista ||
				(active === 'buscar' && trechos.length > 0) ||
				mostrandoPergunta
		)
	);
	const podeSelecionarTodos = $derived(
		mostrandoLista &&
			selected.length < SELECTION_LIMIT &&
			resultados.some((item) => !selected.some((s) => s.codigo === item.codigo))
	);
	const podeCompartilhar = $derived(
		!loading && (mostrandoCodigo || mostrandoLista || mostrandoBuscaVazia)
	);

	function abrirCompartilharResultados() {
		const state = currentShareState();
		if (!state || state.mode === 'perguntar') return;
		shareAviso = '';
		shareUrl = `${window.location.origin}/?${serializeSearchUrl(state).toString()}`;
		shareKind = 'search';
		shareOpen = true;
	}

	async function abrirCompartilharConversa() {
		shareKind = 'conversa';
		shareAviso = '';
		shareUrl = '';
		shareOpen = true;
		try {
			shareUrl = await conversationShareUrl(
				window.location.origin,
				$state.snapshot(conversation),
				data.recorte ?? null
			);
		} catch {
			shareAviso = 'Não foi possível montar o link. Copie a resposta com as fontes.';
		}
	}

	const shareState = $derived(parseSearchUrl(page.url.searchParams));
	const social = $derived(
		shareState
			? searchSharePreview(shareState)
			: { title: HOME_TITLE, description: HOME_DESCRIPTION }
	);
	const socialUrl = $derived(shareState ? absoluteUrl(`/${page.url.search}`) : absoluteUrl('/'));
</script>

<svelte:head>
	<title>{social.title}</title>
	<meta name="description" content={social.description} />
	{#if page.url.searchParams.has('modo')}
		<meta name="robots" content="noindex,nofollow" />
	{/if}
	{@html `<script type="application/ld+json">${JSON.stringify({
		'@context': 'https://schema.org',
		'@type': 'WebSite',
		name: 'Busca Base',
		url: 'https://www.buscabase.com.br',
		inLanguage: 'pt-BR'
	})}</script>`}
</svelte:head>

<MetasSociais title={social.title} description={social.description} url={socialUrl} />

<div class="wrap home">
	{#if focused}
		<div class="home-tools">
			<button class="btn btn-tertiary" type="button" onclick={novaConsulta}>Nova consulta</button>
		</div>
	{:else}
		<div class="home-intro">
			<h1>
				Encontre o que você precisa na <br>
				<span class="accent">Base Nacional Comum Curricular</span>
			</h1>
			<p class="lede">
				Busque por código, por filtros ou por tema. Se quiser, também pode perguntar.
			</p>
		</div>
	{/if}

	<CampoPorCodigo
		bind:value={codigo}
		open={codigoAberto}
		onexpand={() => activate('codigo')}
		onactivate={() => activate('codigo')}
	/>
	<CampoPorFiltros
		open={filtrosAberto}
		compact={focused && active === 'filtros'}
		taxonomias={data.taxonomias}
		bind:etapas
		bind:anos
		bind:componentes
		bind:areas
		bind:campos
		bind:documentos
		bind:tipos
		bind:incluirRevogados
		onexpand={() => activate('filtros')}
		onactivate={() => activate('filtros')}
		onsubmit={runFiltros}
	/>
	<CampoDeBusca
		bind:value={busca}
		open={buscarAberto}
		compact={focused && active === 'buscar'}
		onexpand={() => activate('buscar')}
		onactivate={() => activate('buscar')}
		onsubmit={runBuscar}
	/>
	<SecaoPerguntar
		open={perguntarAberto}
		bind:value={pergunta}
		compact={focused && active === 'perguntar'}
		disabled={!perguntarAtivo}
		busy={perguntarBusy}
		threadActive={conversation.length > 0}
		onexpand={() => activate('perguntar')}
		onactivate={() => activate('perguntar')}
		onsubmit={runPerguntar}
	/>

	<p class="live" aria-live="polite">{live}</p>

	<section class="results-region" aria-labelledby="titulo-resultados">
		<div class="results-head">
			<h2 id="titulo-resultados" class="results-title">Resultados</h2>
			{#if mostrandoLista}
				<p class="results-count">{formatCount(total)}</p>
				{#if active === 'buscar'}
					<RecortesInferidos chips={inferred} onremove={removeInferred} />
				{/if}
			{/if}
			{#if podeSelecionarTodos || podeCompartilhar}
				<div class="results-actions">
					{#if podeSelecionarTodos}
						<button class="btn btn-secondary" type="button" onclick={selectAll}
							>Selecionar todos</button
						>
					{/if}
					{#if podeCompartilhar}
						<button
							class="btn btn-secondary"
							type="button"
							onclick={abrirCompartilharResultados}
							>Compartilhar resultados</button
						>
					{/if}
				</div>
			{:else if !temConteudoResultados}
				<p class="results-lead">Os itens encontrados aparecem aqui.</p>
			{/if}
		</div>

		{#if selected.length}
			<BarraDeSelecao items={selected} onClear={() => (selected = [])} />
		{/if}

		{#if loading}
			<EstadoDeEspera texto={loading} />
		{/if}
		{#if error}
			<Aviso kind="erro" titulo={error.titulo} texto={error.texto} />
		{/if}

		{#if mostrandoCodigo && codigoItem}
			<CartaoDeAprendizagem
				item={codigoItem}
				detail
				perguntarAtivo={perguntarAtivo}
				onPerguntar={perguntarSobre}
			/>
		{/if}

		{#if mostrandoBuscaVazia}
			{#if active === 'filtros'}
				<Aviso
					kind="atencao"
					titulo={avisoFiltrosVazio.titulo}
					texto={avisoFiltrosVazio.texto}
					acao={chipsFiltros.length > 1 ? 'Retirar última escolha' : 'Limpar recorte'}
					onAcao={chipsFiltros.length > 1 ? retirarUltimoFiltro : limparFiltros}
				/>
			{:else}
				<Aviso
					kind="atencao"
					titulo={`Não encontramos resultados para “${busca}”.`}
					texto="Tente outras palavras ou um recorte na pesquisa por filtros."
				/>
			{/if}
		{/if}

		{#if mostrandoLista}
			<div class="results">
				{#each resultados as item (item.codigo)}
					<CartaoDeAprendizagem
						{item}
						selectable
						selected={selected.some((s) => s.codigo === item.codigo)}
						onToggle={() => toggleSelect(item)}
						perguntarAtivo={perguntarAtivo}
						onPerguntar={perguntarSobre}
					/>
				{/each}
				{#if total > resultados.length}
					<button class="btn btn-secondary" type="button" onclick={moreResults}
						>Mostrar mais resultados</button
					>
				{/if}
			</div>
		{/if}

		{#if active === 'buscar' && trechos.length}
			<TrechosDaBase {trechos} />
		{/if}

		{#if active === 'perguntar'}
			{#if statusPergunta && perguntarBusy}
				<EstadoDeEspera texto={statusPergunta} onCancel={() => abort?.abort()} />
			{:else if statusPergunta}
				<p class="status-line" role="status">{statusPergunta}</p>
			{/if}
			{#if conversation.length}
				<div class="results conversation">
					{#each conversation as turn, turnIndex (turnIndex)}
						{#if turn.role === 'user'}
							<p class="prompt">{turn.text}</p>
						{:else}
							<article class="generated">
								<header class="generated-chrome">
									<p class="generated-label">Explicação do Busca Base</p>
									<p class="generated-notice">
										Resposta gerada a partir dos trechos encontrados na Base.
									</p>
									{#if turn.incompleta}
										<p class="generated-notice">Resposta incompleta.</p>
									{/if}
								</header>
								<div class="generated-answer">
									{#if turn.text}
										<RespostaGerada
											text={turn.text}
											onCite={turn.citedSources?.length
												? (n) => goToFonte(turnIndex, n)
												: undefined}
										/>
									{:else if perguntarBusy && turnIndex === conversation.length - 1}
										<p class="generated-notice">Preparando a resposta…</p>
									{/if}
								</div>
								{#if turn.text && !(perguntarBusy && turnIndex === conversation.length - 1)}
									<AcoesDeResposta
										answerText={turn.text}
										citedSources={turn.citedSources || []}
										onShare={abrirCompartilharConversa}
									/>
								{/if}
								{#if turn.citedSources?.length}
									<FontesDaResposta
										sources={turn.citedSources}
										idPrefix={`fonte-${turnIndex}`}
									/>
								{/if}
							</article>
						{/if}
					{/each}
				</div>
			{/if}
			{#if podeContinuarPergunta}
				<form
					class="follow-up"
					onsubmit={(event) => {
						event.preventDefault();
						runPerguntar(followUp);
					}}
				>
					<div class="field">
						<label for="campo-continuar">Continuar esta conversa</label>
						<p id="ajuda-continuar" class="help">
							{followUpsLeft === 1
								? 'A continuação parte dos códigos já citados. Você pode fazer mais 1 pergunta nesta conversa.'
								: `A continuação parte dos códigos já citados. Você pode fazer mais ${followUpsLeft} perguntas nesta conversa.`}
						</p>
						<p id="priv-continuar" class="help">
							Não inclua nomes ou outros dados pessoais de estudantes.
						</p>
						<textarea
							id="campo-continuar"
							bind:value={followUp}
							placeholder="Ex.: e no 6º ano, o que muda?"
							aria-describedby="ajuda-continuar priv-continuar"
						></textarea>
					</div>
					<button class="btn btn-primary" type="submit" disabled={!followUp.trim()}
						>Perguntar</button
					>
				</form>
			{:else if conversaNoLimite}
				<p class="follow-up-limit">
					Esta conversa chegou ao limite de {MAX_FOLLOW_UPS} continuações. Use Nova consulta para
					começar outra.
				</p>
			{/if}
		{/if}

		{#if !temConteudoResultados}
			<p class="results-placeholder">
				Faça uma pesquisa por código, por filtros, por tema ou uma pergunta. O que for encontrado
				aparece nesta área.
			</p>
		{/if}
	</section>
</div>

{#if shareOpen}
	<ModalDeCompartilhar
		bind:open={shareOpen}
		url={shareUrl}
		aviso={shareAviso}
		titulo={shareKind === 'conversa' ? 'Compartilhar conversa' : 'Compartilhar resultados'}
		texto={shareKind === 'conversa' ? shareConversationText() : shareSearchText()}
		mode={shareKind === 'conversa' ? 'perguntar' : 'buscar'}
	/>
{/if}
