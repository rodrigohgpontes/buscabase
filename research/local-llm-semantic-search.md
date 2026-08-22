# Busca semântica na BNCC

**Status:** decisão de implementação  
**Date:** 2026-08-20  
**Corpus:** Base Nacional Comum Curricular (BNCC)

Não há pilha “de notebook” e pilha “de produção”. Local e produção usam o mesmo Compose (Postgres/pgvector, app). Local termina em Caddy; produção no Coolify termina no Traefik (`coolify-proxy`). Embeddings, rerank e geração saem pela OpenRouter; as camadas continuam configuráveis (`EMBEDDING_*`, `RERANK_*`, `GENERATION_*`).

---

## 1. Decisão

Arquitetura **busca híbrida + rerank dedicado + geração opcional e fundamentada**. Os quatro modos do produto (Pesquisa por código, Pesquisa por filtros, Pesquisa simples, Pesquisa conversacional) compartilham o mesmo índice.

| Camada | O que usar | Por quê |
|---|---|---|
| Embeddings (ingest e consulta) | OpenRouter → **Google `google/gemini-embedding-001`**, 3072 dimensões | Melhor qualidade multilingual disponível por API; o corpus é pequeno, o custo irrelevante |
| Busca lexical | FTS / Postgres, match exato de código | Professores buscam por `EF05MA03` tanto quanto por sentido |
| Vetores | PostgreSQL + pgvector | A BNCC é pequena. Banco vetorial à parte é prematuro |
| Rerank | OpenRouter → **Jina `jina/jina-reranker-v3.5`** | Reranker dedicado multilingual; não usar o chat como juiz |
| Geração (Perguntar) | OpenRouter → **DeepSeek `deepseek/deepseek-v4-flash`**, thinking **desligado** | Barato no início, OpenAI-compatível, suficiente para RAG com citação. `deepseek/deepseek-v4-pro` só se o eval de pt-BR e códigos exigir |
| App | FastAPI + SvelteKit | Pipeline curto; sem LangChain no caminho da requisição |
| Hospedagem | **Coolify** na CX23 partilhada com outros projetos. Ingest no notebook; Traefik já faz TLS. Sem GPU até a conta de geração justificar | Ver [docs/production.md](../docs/production.md) e [docs/high-usage.md](../docs/high-usage.md) |

**Não gere parágrafo em toda busca.** O padrão é **Buscar**. **Perguntar** é conversa com fontes, desligável.

Trocar de fornecedor: `EMBEDDING_*`, `RERANK_*` ou `GENERATION_*` (URL, modelo, chave, `GENERATION_EXTRA_BODY`). Mudar o embedder exige reindexar.

---

## 2. O que o produto é

A BNCC é um catálogo hierárquico com códigos estáveis (`EI03EO01`, `EF05MA03`, `EM13CNT101`). Consultas típicas:

1. Código: “o que é EF67EF01?”
2. Semântica: “habilidades de frações no 5º ano”
3. Planejamento: “sequência para artigo de opinião no 8º ano”

Só cosine similarity falha em (1) e é medíocre em (3). Híbrido + metadados importam mais que o gerador.

Fonte curricular: releases `dados-*` de [bncc-dev/bncc-dados](https://github.com/bncc-dev/bncc-dados). Primeiro recorte: `dados-2026.07.1`. Milhares de linhas, não milhões. pgvector + FTS bastam. O custo que escala é **geração**, não recuperação.

---

## 3. Pipeline

```
                    ┌─────────────────────────────────────────┐
                    │  Web + API (Coolify / Traefik, CPU)     │
                    │  busca, limites, cache HMAC             │
                    └───────────────┬─────────────────────────┘
                                    ▼
                    ┌─────────────────────────────────────────┐
                    │  1. código vs linguagem natural         │
                    │  2. híbrido FTS + kNN                   │
                    │  3. rerank (API)                        │
                    │  4. geração opcional (API)              │
                    └───────────────┬─────────────────────────┘
            ┌───────────────┬───────┴───────┬────────────────┐
            ▼               ▼               ▼                ▼
     OpenRouter embed   Postgres        OpenRouter      OpenRouter
     gemini-embedding   pgvector+FTS    jina rerank     deepseek-v4-flash
```

Rerank: 80 candidatos, top 10. Instrução em português no produto (equivalência pedagógica, código igual = altamente relevante).

Geração: só trechos recuperados; códigos inseridos dos metadados e revalidados; thinking off; recusar o que a Base não diz.

---

## 4. Custo

Embeddings de 1M consultas: ordem de poucos dólares. Irrelevante ao lado de Perguntar.

`deepseek/deepseek-v4-flash` (~2k in + ~400 out): dezenas de milhares de respostas/mês cabem em dezenas de dólares. GPU 24 GB (RunPod 3090) só entra por volta de **200–300 mil gerações/mês** ou se residência dos prompts exigir. Plano: [docs/high-usage.md](../docs/high-usage.md).

---

## 5. Stack

O Compose **é** o sistema. Sem segundo toolkit “quando crescer”.

| Peça | Escolha |
|---|---|
| App | FastAPI + SvelteKit |
| Índice | Postgres 16 + pgvector + FTS + trigram |
| Cache / fila | Redis |
| Embed / rerank / generate | HTTP configurável |
| TLS | Caddy no notebook; Traefik (Coolify) em produção |

Não: Ollama, Chroma, BNCC de fixture no request path, LangChain como orquestrador.

---

## 6. Riscos

1. **Alucinação de código** — P0. Códigos vêm das linhas recuperadas, não dos tokens.
2. **Versão** — guardar recorte em todo item.
3. **Introduções** — down-weight `tipo=introducao`.
4. **Filtros** — “frações no 2º ano” não devolve 6º.
5. **LGPD** — consultas de Perguntar e Buscar saem para a OpenRouter (e daí para o modelo de cada camada). Sem log local do texto; aviso em Privacidade; não treinar com queries nossas.
6. **Acessibilidade** — site público em 4G barato.
7. **Institucional** — recuperar o texto oficial, não editorializar.

---

## 7. Sequência

1. Ingerir `dados-2026.07.1` no notebook e restaurar o dump no Postgres do recurso Coolify.
2. Por código (400 vs 404).
3. Buscar: lexical, embeddings Gemini via OpenRouter, RRF, Jina via OpenRouter.
4. Perguntar: DeepSeek flash via OpenRouter, thinking off, limites e flag desde o primeiro deploy.
5. Medir Recall@10 e nDCG no recorte real.
6. Se a fatura de geração passar do limiar de [docs/high-usage.md](../docs/high-usage.md), apontar `GENERATION_*` para vLLM numa 3090 — o app não muda.
