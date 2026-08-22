# Busca Base

Site público para encontrar, conferir e reutilizar o texto da Base Nacional Comum Curricular (BNCC).

**Encontre o que você precisa na Base Nacional Comum Curricular.** Busque por código, por filtros ou por tema. Se quiser, também pode perguntar.

No ar: [www.buscabase.com.br](https://www.buscabase.com.br)

Projeto independente, em português brasileiro. Não é um site oficial do MEC.

## O que o site faz

A home concentra a consulta. Há quatro modos:

| Modo | Quando usar | O que acontece |
|---|---|---|
| **Pesquisa por código** | Você sabe o código, ou o começo dele | Abre o item (`EF05MA03`). Só Postgres. Sempre no ar. |
| **Pesquisa por filtros** | Você quer recortar etapa, ano, componente ou documento | Lista os itens do recorte, sem parágrafo gerado. |
| **Pesquisa simples** | Você tem um tema, não o código | Recuperação híbrida (texto + vetores + rerank). Perguntas mais amplas também podem devolver trechos do PDF oficial. |
| **Pesquisa conversacional** | Você quer entender ou comparar | Resposta com fontes, em cima da mesma recuperação. Dá para desligar com `PERGUNTAR_ENABLED=false`. |

Além da home, o recorte vira páginas estáveis e indexáveis: [índices](https://www.buscabase.com.br/indices), habilidades, etapas, anos, áreas, componentes, competências e documentos. Os documentos oficiais também aparecem reconstruídos a partir dos PDFs (BNCC 2018, complemento de Computação e parecer de Arte).

O arquivo homologado no MEC ou no CNE prevalece.

## Como funciona

Uma só pilha local e em produção: mesmos serviços, mesmos nomes de variáveis, mesmo recorte de dados. Só mudam hosts, segredos e chaves.

```
navegador
  └─ apps/web   SvelteKit 5 (adapter-node)
       └─ /api  apps/api   FastAPI
            ├─ Postgres 16 + pgvector   itens, FTS, vetores, prosa
            ├─ Redis                    cache HMAC (7 dias) e limite da conversa
            └─ OpenRouter               embeddings, rerank e geração
```

Localmente o TLS fica no Caddy. Em produção, no Traefik do Coolify. Não há GPU na máquina da aplicação. Não há chamada a `api.bncc.dev` em tempo de execução. Não há BNCC fictícia nem modelos simulados no caminho da requisição.

A pesquisa simples junta busca lexical e vetorial (RRF) e, com chave configurada, passa pelo rerank. A conversa usa os mesmos trechos e cita as fontes. Códigos que não existem no recorte são recusados: o modelo não inventa identificador.

Consultas ficam gravadas neste servidor (texto, filtros, códigos), sem cookie e sem IP na mesma linha. Detalhe em [Privacidade](https://www.buscabase.com.br/privacidade).

| Camada | Gateway | Modelo inicial |
|---|---|---|
| Embeddings (ingest e busca) | OpenRouter | `google/gemini-embedding-001` (3072d) |
| Rerank | OpenRouter | `jina/jina-reranker-v3.5` |
| Geração (conversa) | OpenRouter | `deepseek/deepseek-v4-flash`, thinking desligado |

Trocar de modelo ou apontar uma camada para outro endpoint (por exemplo geração numa GPU) é editar URL, modelo e chave. Ver [docs/high-usage.md](./docs/high-usage.md).

## Dados

Fonte curricular única: releases etiquetadas de [bncc-dev/bncc-dados](https://github.com/bncc-dev/bncc-dados). Recorte atual: **`dados-2026.07.1`**.

Dados estruturados da BNCC por [bncc.dev](https://bncc.dev) (CC BY 4.0), a partir dos documentos oficiais do MEC e do CNE. Adaptações: indexação, busca, prosa extraída dos PDFs e interface próprias.

A atribuição aparece em Sobre e no rodapé. A busca não envia ninguém ao bncc.dev.

## Repositório

```
apps/web      interface (SvelteKit)
apps/api      API, ingestão, recuperação e conversa
scripts/prose extração dos PDFs oficiais
tests/evals   regressão de códigos inexistentes (bncc-benchmark)
docs/         produção, acessibilidade, custo de geração
research/     decisões de produto e escrita
```

## Subir localmente

Requisitos: Docker e Compose. Para a busca por tema e a conversa, uma chave da [OpenRouter](https://openrouter.ai/keys). Sem ela, código, filtros e busca lexical funcionam; a semântica fica incompleta e a conversa não abre.

```bash
cp .env.example .env
# cole OPENROUTER_API_KEY

make up
make ingest
make extract-prose
make smoke
```

`make ingest` baixa o tarball do tag `BNCC_DADOS_TAG`, carrega o snapshot e gera embeddings só das linhas novas ou alteradas. `make extract-prose` reconstrói os PDFs oficiais e indexa a prosa.

`make up` empacota API e frontend como em produção: mudar um `.svelte` ou `.py` exige rebuild. Para gravar e ver na hora:

```bash
make dev
```

A API usa `uvicorn --reload`; o site usa Vite. Continua em [http://localhost](http://localhost). A primeira subida instala `node_modules` no contentor e demora um pouco.

Os nomes das variáveis são os mesmos em produção. O essencial:

| Variável | Função |
|---|---|
| `OPENROUTER_API_KEY` | embeddings, rerank e geração |
| `BNCC_DADOS_TAG` | recorte pinado (`dados-2026.07.1`) |
| `PERGUNTAR_ENABLED` | desliga só a conversa |
| `EMBEDDING_*` / `RERANK_*` / `GENERATION_*` | trocam uma camada sem mudar o app |

`EMBEDDING_API_KEY`, `RERANK_API_KEY` e `GENERATION_API_KEY` são opcionais: vazias, cada camada usa a chave da OpenRouter.

## Testes

```bash
make test
cd apps/web && npm install && npm test -- --run
```

CI em [`.github/workflows/ci.yml`](./.github/workflows/ci.yml): decodificador de códigos, evals de recusa, testes e typecheck do frontend, e validação do Compose.

Testes de busca usam o recorte real quando `DATABASE_URL` aponta para um Postgres ingerido. Entradas sintéticas cobrem só formato inválido e lacunas oficiais de numeração.

TalkBack, NVDA e VoiceOver são tarefa humana: [docs/a11y-manual.md](./docs/a11y-manual.md).

## Produção

A instância pública corre no Coolify, a partir de [`docker-compose.coolify.yml`](./docker-compose.coolify.yml). Ingestão e embeddings do corpus acontecem fora da VM; produção restaura um dump e atende HTTP. Montagem: [docs/production.md](./docs/production.md).

## Licença

Código: [MIT](./LICENSE). Dados reutilizados: CC BY 4.0 ([bncc-dados](https://github.com/bncc-dev/bncc-dados)).

## Quem fez

[Rodrigo Pontes](https://www.linkedin.com/in/rodrigohgpontes). Contato: [contato@rodrigopontes.com.br](mailto:contato@rodrigopontes.com.br).
