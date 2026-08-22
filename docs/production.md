# Produção do Busca Base

O Busca Base em produção é um recurso **Docker Compose** no Coolify já instalado numa CX23 Hetzner (2 vCPU partilhados, 4 GB RAM, ~38 GB de disco, IPv4 `46.225.211.244`). A mesma VM corre o Coolify e outros projetos. O preço da caixa está travado: rescale, rebuild ou mudança de localização perdem esse preço.

O ficheiro de composição é [`docker-compose.coolify.yml`](../docker-compose.coolify.yml). Não é o Compose local: em produção não há Caddy. O `coolify-proxy` (Traefik v3) já ocupa **80/443** e emite TLS. Toda a IA em consulta sai pela **OpenRouter**. Não há GPU nesta máquina.

Ingest e embeddings do corpus correm **fora da VM** (no notebook). Produção só restaura um dump Postgres e atende HTTP.

---

## Topologia

```
Internet
  └─ 46.225.211.244:80/443
       └─ coolify-proxy (Traefik)
            ├─ Host(www.buscabase.com.br) && PathPrefix(`/api`) → api:8000
            └─ Host(www.buscabase.com.br) && PathPrefix(`/`)    → web:3000
                 │
                 ├─ web  ──API_INTERNAL_URL──► api:8000
                 │                              │
                 │                              ├─ postgres (pgvector/pg16)
                 │                              └─ redis
                 └─ outros projetos (outros Host())
```

O dashboard Coolify escuta em `http://46.225.211.244:8000` (não publicar na internet). Postgres e Redis deste stack **não** têm porta no host.

| Peça | O que é |
|---|---|
| Recurso Coolify | Projeto **Busca Base**, ambiente `production`, UUID `d12mpboc5vw4n0nhd60z8mru` |
| Git | `rodrigohgpontes/buscabase`, branch `main`, build pack Docker Compose, ficheiro `docker-compose.coolify.yml` |
| Serviços | `postgres`, `redis`, `api`, `web`. `backup` existe só como profile e não sobe no deploy |
| Imagens | `pgvector/pgvector:pg16`, `redis:7-alpine`, Dockerfiles em `apps/api` e `apps/web` |

Os nomes dos contentores Coolify levam o UUID do recurso, p.ex. `api-d12mpboc5vw4n0nhd60z8mru-…`. O Postgres **deste** recurso não é o `coolify-db` nem o Postgres one-click de outros projetos.

---

## Por que Compose próprio, não Nixpacks nem Postgres one-click

Outros projetos nesta VM usam Nixpacks + o PostgreSQL one-click do Coolify (`postgres:18-alpine`). Esse banco **não tem pgvector**. O Busca Base precisa de `vector` (3072 dimensões, HNSW) e de quatro processos com redes internas. Por isso é um segundo recurso Compose, com o seu próprio `pgvector/pgvector:pg16` e `init.sql`.

`POSTGRES_HOST=postgres` resolve, no DNS Docker **deste** stack, para esse contentor. Não aponta para o banco de outro recurso nem para `coolify-db`.

---

## Redes Docker e Traefik

Coolify cria uma rede cujo nome é o UUID do recurso (`d12mpboc5vw4n0nhd60z8mru`) e liga o `coolify-proxy` a ela. O Compose declara ainda `internal` (Postgres, Redis, e o tráfego app→banco).

Há uma rede partilhada chamada `coolify`, onde vivem o proxy, o `coolify-db` e outros projetos. **`api` e `web` não entram nessa rede.** Nela o hostname `postgres` é o Postgres do próprio Coolify. Se a API resolver `postgres` aí, as credenciais falham contra o banco errado (sem pgvector, sem o recorte).

O Traefik, sem `traefik.docker.network`, escolhe uma das várias redes do contentor. Se escolher `internal` (onde o proxy não está), `GET /` fica em timeout enquanto `/api` ainda pode responder — o proxy alcançou a API por acaso na rede certa. O Compose fixa:

```yaml
labels:
  - traefik.docker.network=d12mpboc5vw4n0nhd60z8mru
```

Hosts HTTP não colidem: cada projeto tem o seu `Host()`. O que colide é o **nome Docker** `postgres` na rede `coolify`.

---

## Domínios, TLS e prefixo `/api`

| Serviço | Regra Traefik | Porta do contentor |
|---|---|---|
| `web` | `Host(www.buscabase.com.br) && PathPrefix(/)` | 3000 |
| `api` | `Host(www.buscabase.com.br) && PathPrefix(/api)` | 8000 |

Coolify gera as labels. No domínio da API o formato que o Coolify entende é `https://www.buscabase.com.br:8000/api` (porta e path). `https://host/api:8000` é interpretado como path `/api:8000` e parte os routers.

Para paths, o Coolify liga **Strip Prefix**. O FastAPI monta as rotas em `/api/…`. Sem o prefixo, o pedido chega como `/codigos/…` e dá 404. A API restaura o prefixo em middleware (`restore_stripped_api_prefix` em `apps/api/app/main.py`), de modo que tanto o healthcheck interno (`/api/health`) como o tráfego público (já sem `/api`) funcionam.

O certificado Let's Encrypt exige um A **público** de `www.buscabase.com.br` → `46.225.211.244` (visível em `dig @8.8.8.8`). Sem isso o ACME devolve NXDOMAIN, o Traefik serve o certificado default, e falhas repetidas disparam rate limit da Let's Encrypt. Outros projetos no mesmo IP usam outros hostnames, cada um com o seu certificado.

HTTP:80 redireciona para HTTPS. Firewall da cloud: 80 e 443 abertos; 22 e 8000 só no IP do operador; 5432 fechado.

---

## Serviços e healthchecks

**postgres** — `pgvector/pgvector:pg16`, user/db `buscabase`. O volume `postgres_data` guarda o recorte. A password no ambiente do contentor só vale no **primeiro** init do volume; depois disso `ALTER USER` (via `psql` no socket local, que não pede password) é o que alinha o role com o `POSTGRES_PASSWORD` da API. `DATABASE_URL` não se define à mão: o Compose monta a partir de `POSTGRES_*`.

**redis** — cache HMAC das consultas (até 7 dias). Sem ele a app sobe, mas o cache some.

**api** — FastAPI/uvicorn :8000. Healthcheck: `GET http://127.0.0.1:8000/api/health`. Esse handler lê a tabela `snapshots`. Banco vazio ou sem migrações → 500 → contentor `unhealthy` → o `web` (depends_on healthy) não arranca. O dump tem de estar restaurado para o deploy Compose completar; um restore a quente + restart da API também serve. No arranque a API corre `alembic upgrade head` (tabela `usage_events` e outras migrações aditivas).

`/uso` (e `GET /api/uso`) só existe com `USO_PASSWORD` no ambiente do `api` e do `web`. No Coolify, no recurso Compose, acrescente:

```
USO_USER=uso
USO_PASSWORD=<openssl rand -base64 24>
```

Redeploy. Não precisa rebuild da imagem. Abra `https://www.buscabase.com.br/uso` com o usuário `uso`. Sem a variável, a rota fica 404. A senha de produção não vai para o Git.

**web** — SvelteKit adapter-node :3000. `PUBLIC_ORIGIN` e `API_INTERNAL_URL` entram no **build** da imagem. No browser `apiBase()` é `''` (mesmo origin `/api/…`); no SSR usa `API_INTERNAL_URL` (`http://api:8000`). O prerender em produção corre sem `catalog.json` (`handleUnseenRoutes: 'ignore'`); as páginas de habilidade/índice são SSR.

Swap de 1 GB em `/swapfile` (a CX23 não traz swap). Coolify + outros projetos já ocupam ~2 GB; o Busca Base cabe em tráfego baixo. Build, restore ou pico nas duas apps podem OOM. Disco ~38 GB: `docker image prune` de vez em quando; dumps não ficam em `/tmp`.

---

## Dados: ingest no notebook, dump na VM

O corpus é o recorte `BNCC_DADOS_TAG` (hoje `dados-2026.07.1`). `make ingest` no notebook baixa o snapshot bncc-dados, aplica Alembic, carrega taxonomias/itens e pede embeddings à OpenRouter (`google/gemini-embedding-001`, 3072d). Produção **não** corre ingest: a VM não tem a chave para isso como caminho feliz, e o recorte cabe num dump.

O dump é `pg_dump` gzip (~29 MB com vetores). Restaura-se no contentor Postgres **deste** recurso:

```bash
gunzip -c buscabase-latest.sql.gz | docker exec -i NOME_DO_POSTGRES \
  psql -U buscabase -d buscabase
```

Não é o `coolify-db` nem o Postgres one-click de outro projeto. Recorte novo = ingest no notebook + dump novo + `DROP DATABASE` / `CREATE DATABASE` só neste banco. Schema major incompatível: não restaurar.

Backup operacional: `pg_dump` deste Postgres, copiado para fora da VM. Backups one-click do Coolify noutros recursos **não** cobrem este volume.

---

## Ambiente e modelos

Os **nomes** das variáveis são os mesmos do `.env` local. Valores de produção (recurso Coolify):

| Variável | Papel |
|---|---|
| `ORIGIN`, `PUBLIC_ORIGIN` | `https://www.buscabase.com.br` |
| `API_INTERNAL_URL` | `http://api:8000` (SSR) |
| `POSTGRES_*` | user/db `buscabase`, host `postgres`, password longa (volume já inicializado) |
| `CACHE_HMAC_SECRET` | ≥32 caracteres; giro = só redeploy, o cache antigo expira |
| `USO_USER` | usuário HTTP Basic de `/uso` (omissão: `uso`) |
| `USO_PASSWORD` | senha de `/uso` e `/api/uso`; vazia = as rotas respondem 404 |
| `OPENROUTER_API_KEY` | obrigatória em consulta (embed de query, rerank, geração) |
| `EMBEDDING_API_KEY`, `RERANK_API_KEY`, `GENERATION_API_KEY` | vazias → cai na chave OpenRouter |
| `PERGUNTAR_ENABLED` | `true`; `false` desliga só Perguntar, sem redeploy de dados |
| `BNCC_DADOS_TAG` | recorte publicado (`dados-2026.07.1`) |

Modelos (vêm no Compose; não se mudam em silêncio):

| Uso | Modelo |
|---|---|
| Embeddings (ingest local + query) | `google/gemini-embedding-001` (3072d) |
| Rerank (Buscar e Perguntar) | `jina/jina-reranker-v3.5` |
| Geração (Perguntar) | `deepseek/deepseek-v4-flash`, thinking desligado |

OpenRouter fora: Pesquisa por código e FTS continuam; some a semântica de query e o rerank. Sem Postgres o site para. `/api/health` expõe `"perguntar"`, recorte e `item_count`.

---

## O que o site deve mostrar

Com o recorte restaurado: home com Pesquisa por código, Pesquisa por filtros e Pesquisa simples abertos e Pesquisa conversacional fechada por omissão; título **Encontre o que você precisa na BNCC | Busca Base**; `/api/codigos/EF05MA03` devolve texto oficial; `/XYZ` → 400; `/EF05MA99` → 404; busca “frações no 5º ano” devolve itens; `/robots.txt` e `/sitemap.xml` existem; rodapé com recorte e aviso de que o site não é do MEC; nenhum resultado aponta para bncc.dev. Outros projetos no mesmo IP continuam a responder nos seus hostnames.

`ORIGIN=https://www.buscabase.com.br make smoke` no notebook, quando o DNS público e o TLS já estiverem certos.

---

## Limites e destino acoplado

Coolify, outros projetos e o Busca Base partilham IP, RAM e disco. OOM, disco cheio ou reboot afetam todos. Não reinstalar o Coolify nem recriar a CX23 por causa deste app. Rollback de código = redeploy do commit anterior no Coolify; rollback de dados = o dump. Não ingerir na VM.

Uso alto de Perguntar: [high-usage.md](./high-usage.md).
