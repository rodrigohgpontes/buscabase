# bncc.dev reuse and three search modes

**Status:** research, pass 2  
**Date:** 2026-08-20  
**Depends on:** [local-llm-semantic-search.md](./local-llm-semantic-search.md)  
**External source reviewed:** [bncc.dev/desenvolve](https://bncc.dev/desenvolve/), [api.bncc.dev](https://api.bncc.dev/v1/openapi.json), [github.com/bncc-dev](https://github.com/bncc-dev)

Product constraint from this pass: **users must never be sent to bncc.dev** (no result links, no “abrir no site deles”, no MCP/API of theirs in the user-facing path). Attribution required by the data license stays in **Sobre / rodapé**, not in the search journey.

---

## 1. What bncc.dev actually is

[bncc.dev](https://bncc.dev/desenvolve/) is an open dataset and developer platform maintained by Profy. It is **not** a semantic-search product. Their public `/buscar` and API `/v1/busca` are **normalized lexical search** over enunciados (accents/case folded), with structured filters. That is Mode 1-adjacent, not our Mode 2.

They already did the painful part of BNCC engineering: turning PDFs and MEC spreadsheets into **1.721 verified aprendizagens**, with provenance on every row.

| Asset | Where | License | Version seen |
|---|---|---|---|
| Canonical JSON + SQLite + CSV | [bncc-dev/bncc-dados](https://github.com/bncc-dev/bncc-dados) | **CC BY 4.0** (data), **MIT** (pipeline) | `dados-2026.07.1` (2026-08-10) |
| npm `@bncc/dados`, PyPI `bncc`, MCP `@bncc/mcp` | [bncc-dev/bncc-pacotes](https://github.com/bncc-dev/bncc-pacotes) | MIT | PyPI `bncc==0.2.1` |
| Hosted REST | [api.bncc.dev](https://api.bncc.dev/v1/openapi.json) | same data license; IP rate limit | OpenAPI 3.1, `1.0.0-beta` |
| Hosted MCP | [mcp.bncc.dev/mcp](https://bncc.dev/mcp/) | 60 req/min/IP | 7 tools |
| Hallucination benchmark | [bncc-dev/bncc-benchmark](https://github.com/bncc-dev/bncc-benchmark) | CC BY 4.0 items, MIT harness | v0.2.0, rodada `oficial-seca-2026-08` |

Coverage of `dados-2026.07.1`:

- 93 objetivos (Educação Infantil)
- 1.304 habilidades (Ensino Fundamental)
- 183 habilidades (Ensino Médio)
- 141 aprendizagens of **Computação 2022** (complemento, codes `CO`)
- 10 competências gerais + 105 específicas
- 32 alinhamentos EI (progressão oficial between age bands)
- 20 marcos legais (URLs gov.br, no full text)
- JSON Schemas, `DECISOES.md`, character-level PDF verification (1.580/1.580 BNCC 2018 after the 2026-08-10 fix; 141/141 Computação)

A real record (API, names resolved) looks like this — this **is** the chunk we wanted:

```json
{
  "codigo": "EF05MA03",
  "etapa": "EF",
  "texto": "Identificar e representar frações …",
  "anos": [5],
  "componente": { "id": "ef-comp-ma", "nome": "Matemática" },
  "organizacao": { "tipo": "unidade_tematica", "nomes": { "unidadeTematica": "Números" } },
  "objetosConhecimento": [{ "nome": "Representação fracionária dos números racionais: …" }],
  "vigencia": { "status": "vigente", "desde": "dados-2026.07" },
  "fonte": {
    "arquivo": "BNCC_Ensino Fundamental.xlsx",
    "localizador_pdf": "Base-Nacional-Comum-Curricular-BNCC.pdf, página PDF 297"
  }
}
```

They model **four code grammars** honestly (not one generic type with nulls): EI, EF, EM, Computação. Decoder example: `EF67LP08` → etapa EF, anos 6–7, componente LP, sequência 8. Official numbering has **legitimate gaps**; a well-formed code can 404. That fact is gold for anti-hallucination.

---

## 2. What to take (and how), without sending users there

Principle: **vendor the data, own the UX, cite in the footer.** Do not wrap their live API/MCP as our backend.

### 2.1 Take: the dataset (highest value)

Copy `dados/` (and optionally `schema/`, `DECISOES.md`) from [bncc-dados](https://github.com/bncc-dev/bncc-dados) into this repo, **pin `dados-2026.07.1`**.

Why copy, not `curl api.bncc.dev` at runtime:

- Users never touch their domain, even indirectly via our server.
- No 60 req/min ceiling, no CORS/uptime coupling.
- We can add embeddings and our IDs. New complements (Arte, etc.) wait for their next `dados-*` release — no parallel extractor (pass 3).
- CC BY 4.0 allows commercial and non-commercial reuse, including products.

How to ingest:

1. Snapshot JSON (canonical) — not only the PyPI wheel, so we control updates.
2. Load into Postgres: one row per aprendizagem + tables for competências, estrutura, objetos de conhecimento.
3. Keep their `codigo` as primary key. Keep `fonte.localizador_pdf` for our own citation UI (“PDF oficial, p. 297”), pointing at **MEC PDF or our hosted copy**, never `bncc.dev/habilidade/EF05MA03`.
4. Record `data_version` on every row so answers can say “BNCC 2018, recorte dados-2026.07.1”.

The app always reads **our** Postgres. Decoder, progressão EI, and filters are implemented in our service (MIT `pipeline/codigos.py` and their schemas are fair to copy). Do not call PyPI/npm/`api.bncc.dev` at runtime — locally or in prod.

MIT pieces we can copy or reimplement:

- Code grammar / `decodificar` ([docs/modelo-de-dados.md](https://github.com/bncc-dev/bncc-dados/blob/main/docs/modelo-de-dados.md), `pipeline/codigos.py`)
- JSON Schemas for validation in CI
- EI `progressao_ei` / alinhamentos (official, easy to lose if we parsed the PDF ourselves)

### 2.2 Take: the hallucination benchmark (eval, not UX)

[bncc-benchmark](https://github.com/bncc-dev/bncc-benchmark) measured 19 models × 900 items = **17.100** ungounded answers (August 2026). Headline: **54%** of transcriptions invented or swapped text; **27%** of real codes were denied. Even the best closed model still accepted a large share of plausible fake codes.

Reuse:

- Public item bank as a **regression suite** for our three modes (especially “refuse unknown codes” in Por código and Perguntar).
- Tasks A–D (lookup, existence, open generation, inverse lookup) map directly to product tests.
- Do **not** scrape their held-out set (unpublished on purpose).
- CC BY 4.0: cite the benchmark in research/eval docs, not in the teacher UI.

This is independent confirmation of the previous research note: **never let the LLM emit a code that was not in retrieved rows.**

### 2.3 Take conceptually, not as a dependency

| Their thing | Use as | Do not use as |
|---|---|---|
| `/v1/aprendizagens/{codigo}` | Spec of the record we must show | Live lookup in production |
| `/v1/busca` | Proof that lexical + filters already work | Our “Buscar” |
| `/v1/decodificar/{codigo}` | Grammar tests | User-facing third-party call |
| `/v1/estrutura` | Taxonomy for our filters | Remote schema |
| MCP 7 tools (`bncc_lookup`, `bncc_buscar`, `bncc_listar`, `bncc_decodificar`, `bncc_progressao_ei`, `bncc_estrutura`, `bncc_estatisticas`) | Checklist of queries power users will type | Our chat backend |
| `llms.txt` / per-code `.md` pages | Idea: every aprendizagem should have a stable URL **on our domain** | Deep links to theirs |
| Attribution copy they publish | Footer/Sobre text | Result cards |

### 2.4 Attribution without hijacking the UX

CC BY 4.0 requires: credit, license link, indication of changes. Their suggested line is fine **on Sobre and a small footer**, not on each result:

> Dados estruturados da BNCC por [bncc.dev](https://bncc.dev) (CC BY 4.0), a partir dos documentos oficiais do MEC e do CNE. Recorte `dados-2026.07.1`. Adaptações: indexação semântica e interface próprias.

That is a legal citation, not a product redirect. Rules:

- Result permalinks: `nossodominio/habilidade/EF05MA03` (or equivalent), never theirs.
- “Fonte” on a card: **documento oficial + página do PDF**, optionally “planilha MEC”, not “ver no bncc.dev”.
- No “powered by bncc.dev” in the search header.
- If we change texts (we should not) or add complements they lack, say so in Sobre.

BNCC normative wording itself is an official act, not copyrighted (Lei 9.610/98 art. 8º). Their license covers **compilation, structure, and curation**.

### 2.5 What they do **not** give us (gaps we still own)

- **Semantic search, rerank, embeddings, conversation.** Out of scope for them.
- **Complemento de Arte (Parecer CNE/CEB nº 2/2026).** Not in `dados-2026.07.1`. Track as a future ingest.
- BNCC **introductions / essays** (competência as a concept, implementation notes). They have competências as records; they do not dump the 600-page prose.
- Official **examples / descritores** of the Computação annex (they flag this as future).
- Invented **progressão EF** (they correctly refuse). Mode 3 may *suggest* sequences; that is our risk, not their data.
- Currículos estaduais, DCNs, cadernos de implementação.

Do not re-parse the 2018 PDF from scratch. Their CI already lost months on hyphenation, truncations, and spreadsheet↔PDF fights (see changelog: EF69LP46 was missing ~448 characters). Fork their pipeline later if we add Arte; do not compete with it for the core Base.

---

## 3. Three user-visible search modes

All three are first-class. The user always sees them. Default for a first visit: **Buscar** (cheap, useful). **Perguntar** can be feature-flagged off later without deleting the UI contract — hide or disable the third control, keep the other two.

Do not name modes after models, GPUs, or “IA”. Teachers already have words: código, buscar, perguntar.

### 3.1 Recommended names (pt-BR)

| # | Nome na UI | Nome interno | O que o usuário pensa | Custo |
|---|---|---|---|---|
| 1 | **Por código** | `codigo` | “Eu já tenho o código da habilidade.” | CPU only |
| 2 | **Buscar** | `buscar` | “Quero achar habilidades por tema / ano / componente.” | Embed + rerank |
| 3 | **Perguntar** | `perguntar` | “Quero conversar, comparar, montar uma sequência.” | Same as 2 + gerador |

Short helper lines (not UI design, just copy we can reuse):

1. **Por código** — Abre o enunciado oficial a partir do código (ex.: `EF05MA03`).
2. **Buscar** — Encontra habilidades por tema, etapa, ano e componente.
3. **Perguntar** — Conversa com a Base: explica, compara e sugere percursos com citação.

Why this trio:

- Parallel and short (one/two words).
- No false synonym: “Buscar” is not “Perguntar”.
- “Por código” matches how coordenadores speak.
- “Perguntar” signals dialogue without “chatbot” or “assistente de IA” (those age badly and scare schools).
- Power users still understand immediately; beginners are not asked to pick a model.

**Rejected** (and why):

| Candidate | Problem |
|---|---|
| Consulta / Pesquisa / Exploração | Three vague synonyms; user cannot tell cost or behaviour |
| Simples / Avançado / Pro | Shames the default; “Pro” sounds paid |
| Lexical / Semântico / RAG | Engineer-speak |
| Lookup / Search / Ask | English on a Brazilian education site |
| Assistente | Sounds like a product inside the product; implies always-on AI |
| Planejar | Undersells lookup/compare; oversells didactics we may refuse |
| Conversar | Fine as synonym of Perguntar; slightly more casual. Keep as alt label |

**Alt set** if we want even more “power user” flavour later: **Código · Busca · Conversa**. Same mapping. Prefer **Por código · Buscar · Perguntar** as the frozen vocabulary in code (`mode=codigo|buscar|perguntar`).

### 3.2 Mode 1 — Por código

**Input:** a code (paste or type). Tolerate spaces/case: `ef05ma03`, `EF 05 MA 03`.

**Pipeline:**

1. Normalize + `decodificar` (grammar).
2. If ill-formed → error with the grammar (“isso não é um código da BNCC”), suggest **Buscar**.
3. If well-formed but missing → **404 honesto** (“código bem formado, mas não existe na Base; a numeração oficial tem lacunas”). Never ask the LLM. Their API already distinguishes 400 vs 404; copy that behaviour.
4. If hit → full record: texto, etapa, anos, componente, organização, objetos, vigência, página do PDF. Offer EI progressão when `EI*`. Offer Computação vs BNCC-2018 as `documento`.

**Also in this mode (no generation):**

- Prefix / partial code? Optional later (`EF05MA` → list). Not required for v1; can be a typeahead on the same field.
- Decoder shown as secondary info (“6º e 7º ano · Língua Portuguesa · seq. 08”), not as the main result.

**Capacity:** Postgres primary key. This is the mode we keep even if we shut **Perguntar** and even **Buscar** embeddings.

### 3.3 Mode 2 — Buscar

This is the “simpler/cheaper search” from pass 1, now named.

**Input:** natural language and/or filters (etapa, ano, componente, área, documento BNCC vs Computação).

**Pipeline:**

1. If the query *is* a single well-formed code, optionally jump to Por código (or show that hit first). Do not punish people who stay in Buscar with a code.
2. Lexical: Postgres FTS / BM25 on `texto` + `objetosConhecimento` + unidade temática + código.
3. Dense: cloud embedding of the query vs embedded records (1.721 rows — trivial).
4. Metadata pre-filter (ano, componente, …).
5. RRF merge, then **`jina/jina-reranker-v3.5`** via OpenRouter.
6. Return a **ranked list of aprendizagens**, our permalinks, snippets. No generated paragraph.

Their `buscar('frações', etapa='EF', ano=5)` already returns `[EF05MA03, EF05MA04]` lexically. We must beat that on paraphrase (“parte-todo no 5º ano”, “números racionais em fração”) and on cross-component queries. If we cannot beat lexical+filters on a 100-query eval, we have no right to spend generation tokens on Mode 3.

**Capacity:** embed ~50 tokens + rerank top 50–100 pairs. Safe default for “high usage in Brazil”.

### 3.4 Mode 3 — Perguntar (power user, build fully)

A **grounded conversation** on top of Mode 2 retrieval. Same corpus, same reranker, **one** generator. This is the power option. Build the whole product surface; protect the bill with policy, not by shipping a weaker half-chat.

**What “fully” means (features, not extra models):**

| Feature | How | Extra generator? |
|---|---|---|
| Multi-turn | Keep last N user turns + the **codes already cited**; re-retrieve when the topic shifts | No |
| Explicar uma habilidade | Retrieve that code + neighbours (same objeto de conhecimento / alinhamento EI) | No |
| Comparar códigos | User pastes 2–N codes, or asks “diferença 5º vs 6º em frações” → retrieve set, generate table | No |
| Percurso / sequência | Retrieve a handful, generate an **order among retrieved codes only**, with a disclaimer that the BNCC does not define progressão no EF | No |
| Filtros persistentes | “Só EF, Matemática, 6º ano” as conversation constraints, same as Buscar filters | No |
| Recusar o que a Base não diz | Template + missing retrieval → “a BNCC não trata metodologia de TDAH”; do not improvise didactics | No |
| Citar só metadados | Codes inserted from rows, not from tokens (constrained decoding or post-validate) | No |
| Streaming | OpenAI-compatible stream; UX feel, not a second model | No |
| Cache | (pergunta normalizada + filtros + top-k hashes) → resposta | Saves tokens |
| Export | List of códigos citados for the teacher’s planejamento | No |

**What “fully” does *not* mean (capacity we will not buy):**

- A second generator in parallel (“smart” vs “fast”) on the request path.
- Agent loops with 7 MCP-style tools calling the model ten times per question (their MCP is for *external* agents; we already have the database).
- Thinking/chain-of-thought on every answer.
- Indexing currículos estaduais on day one.
- Image/multimodal.
- Fine-tune before the Mode 2 eval is green.

**Generator:** one configured model via OpenRouter. Start with **DeepSeek `deepseek/deepseek-v4-flash`**, thinking off. Promote to `deepseek/deepseek-v4-pro` only if eval demands it — still one model, not a hidden lite chat.

**Retrieval for Perguntar is Mode 2.** The chat never answers from parametric memory. If Buscar would have returned nothing useful, Perguntar must say so.

**Rate and degradation (so we can disable later without lying):**

- Per-IP / per-session cap on Perguntar.
- Global queue; on saturation, **disable only Perguntar** (grey the control: “temporariamente indisponível”) and leave Por código + Buscar.
- Feature flag `PERGUNTAR_ENABLED=false` is an explicit product requirement.

### 3.5 How the three modes share infrastructure

```
                 ┌──────────── Por código ────────────┐
                 │  decode → PK lookup → record UI    │  Postgres
                 └────────────────────────────────────┘
Query ── mode ─► ┌──────────── Buscar ────────────────┐
                 │  FTS + kNN + filters → RRF → Jina  │  OpenRouter embed + rerank
                 └──────────────┬─────────────────────┘
                                │ top-k rows
                 ┌──────────────▼── Perguntar ────────┐
                 │  generate + cite + optional        │  OpenRouter → DeepSeek flash
                 │  multi-turn, compare, percurso     │
                 └────────────────────────────────────┘
```

One index, one reranker, one generator. Modes are **policies** on that stack, not three products.

---

## 4. Capacity envelope (do not overshoot)

Corpus size after vendoring: **~1.7k aprendizagens + ~100 competências + estrutura**. Embedding the whole Base is a one-shot job measured in minutes.

| Mode | Per request | Notes |
|---|---|---|
| Por código | <10 ms DB | Always on |
| Buscar | embed + ~50–100 rerank pairs | Default public traffic; cheap APIs |
| Perguntar | Buscar + ~200–600 output tokens | **the** scarce resource (token bill) |

Treat Perguntar as opt-in generations, not as search QPS. Design:

- Default landing = Buscar.
- Perguntar is visible but not the empty-state.
- Cache aggressively (school queries repeat).
- No speculative multi-model routing.

If Brazil-scale traffic arrives, scale **Buscar** (still cheap) and **queue or pause Perguntar**. That is the kill switch. If the generation bill stays high, point `GENERATION_*` at a GPU later ([docs/high-usage.md](../docs/high-usage.md)).

---

## 5. Implementation sequence (updated)

Pass 1 said “parse the BNCC JSON ourselves first”. Replace that with:

1. **Ingest `dados-2026.07.1` into the production Postgres** (full snapshot, same Compose as prod). Attribution on Sobre/footer only.
2. **Por código** (400 vs 404, decoder, PDF page as our citation).
3. **Buscar** lexical + filters, then Gemini embeddings + Jina rerank via OpenRouter — same services that will face users.
4. **Perguntar** on that retrieve path via OpenRouter (`deepseek/deepseek-v4-flash`); constrain codes; bncc-benchmark-style tasks A–D **with grounding**.
5. Cache, rate limit, flag to disable Perguntar — present from the first deploy.

---

## 6. Decisions for this pass

| Topic | Decision |
|---|---|
| Runtime use of api.bncc.dev / MCP | **No.** Not locally, not in prod. Ingest tagged snapshots only. |
| User links to bncc.dev | **No** in search/results/chat. **Yes** only as CC BY credit on Sobre/footer. |
| Data | Vendor their **tagged** snapshot, pin `data_version`, own URLs. Updates: GitHub Releases + ETag (pass 3). |
| Mode names | Interface: **Pesquisa por código**, **Pesquisa por filtros**, **Pesquisa simples**, **Pesquisa conversacional**. Params: `modo=codigo|filtros|buscar|perguntar`. |
| Default | Pesquisa por código, Pesquisa por filtros e Pesquisa simples abertos; Pesquisa conversacional fechada. |
| Power mode | Pesquisa conversacional, fully built (multi-turn, compare, percurso), one generator, flaggable. |
| Extra models for “power” | None. |
| Next corpus gap | Whatever they publish next (likely Arte 2026). No homemade complements. |

---

## 7. Sources

- [Para quem desenvolve · bncc.dev](https://bncc.dev/desenvolve/)
- [OpenAPI](https://api.bncc.dev/v1/openapi.json), sample [EF05MA03](https://api.bncc.dev/v1/aprendizagens/EF05MA03), [estatísticas](https://api.bncc.dev/v1/estatisticas)
- [bncc-dados README](https://github.com/bncc-dev/bncc-dados), [modelo de dados](https://raw.githubusercontent.com/bncc-dev/bncc-dados/main/docs/modelo-de-dados.md), [changelog](https://raw.githubusercontent.com/bncc-dev/bncc-dados/main/CHANGELOG.md)
- [MCP · 7 tools](https://bncc.dev/mcp/)
- [PyPI bncc 0.2.1](https://pypi.org/project/bncc/)
- [bncc-benchmark](https://github.com/bncc-dev/bncc-benchmark)
- [llms.txt](https://bncc.dev/llms.txt)
