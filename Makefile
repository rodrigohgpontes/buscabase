.PHONY: help env up dev down logs ingest migrate extract-prose test api-shell web-shell backup health smoke

COMPOSE ?= docker compose
COMPOSE_DEV = $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml
ENV_FILE ?= .env

help:
	@echo "Busca Base — a mesma pilha local e em produção"
	@echo "  make env       copia .env.example se .env não existir"
	@echo "  make up        sobe postgres redis api web caddy (imagens de produção)"
	@echo "  make dev       igual, com reload da API e Vite no frontend"
	@echo "  make ingest    baixa o recorte dados-* e carrega no Postgres"
	@echo "  make extract-prose  extrai PDFs oficiais para JSON e carrega prosa no Postgres"
	@echo "  make migrate   aplica migrações Alembic"
	@echo "  make test      testes da API e do frontend"
	@echo "  make down      para os serviços"
	@echo "  make backup    dump do Postgres"
	@echo "  make smoke     checagens rápidas de saúde"

env:
	@test -f $(ENV_FILE) || cp .env.example $(ENV_FILE)
	@echo "Ambiente em $(ENV_FILE). Edite segredos antes de produção."

up: env
	$(COMPOSE) up -d --build postgres redis api web caddy

dev: env
	$(COMPOSE_DEV) --profile edge up -d --build postgres redis api web caddy
	@echo "Reload local em http://localhost — make logs para acompanhar"

down:
	$(COMPOSE) --profile ingest --profile backup down

logs:
	$(COMPOSE) logs -f api web caddy

migrate: env
	$(COMPOSE) run --rm api alembic upgrade head

ingest: env
	$(COMPOSE) --profile ingest build ingest
	$(COMPOSE) --profile ingest run --rm ingest

# Re-embute só blocos novos ou com texto alterado. Para o primeiro backfill, suba EMBEDDING_BATCH_SIZE para 16–32.
extract-prose: env
	@mkdir -p data/prose/pdfs
	PYTHONPATH=. python3 -m pip install -q 'pymupdf>=1.25'
	BNCC_SNAPSHOT_DIR=$${BNCC_SNAPSHOT_DIR:-$(CURDIR)/data/snapshots} \
	BNCC_PROSE_DIR=$(CURDIR)/data/prose \
	BNCC_PROSE_PDF_DIR=$(CURDIR)/data/prose/pdfs \
	PYTHONPATH=. python3 -m scripts.prose --out data/prose
	$(COMPOSE) run --rm api python -m app.prose_load

backup: env
	$(COMPOSE) --profile backup run --rm backup

api-shell:
	$(COMPOSE) exec api bash

web-shell:
	$(COMPOSE) exec web sh

health:
	curl -fsS $${ORIGIN:-http://localhost}/api/health | python3 -m json.tool

smoke:
	@ORIGIN=$${ORIGIN:-http://localhost}; \
	echo "== health =="; curl -fsS $$ORIGIN/api/health; echo; \
	echo "== codigo EF05MA03 =="; curl -fsS $$ORIGIN/api/codigos/EF05MA03 | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('codigo'), d.get('tipo'))"; \
	echo "== 404 honesto =="; curl -s -o /dev/null -w "%{http_code}\n" $$ORIGIN/api/codigos/EF05MA99; \
	echo "== 400 formato =="; curl -s -o /dev/null -w "%{http_code}\n" $$ORIGIN/api/codigos/XYZ; \
	echo "== buscar =="; curl -fsSG "$$ORIGIN/api/buscar" --data-urlencode "q=frações no 5º ano" | python3 -c "import json,sys; d=json.load(sys.stdin); n=d.get('total') or 0; print(n, 'resultados'); raise SystemExit(n < 1)"; \
	echo "== home =="; curl -fsS -o /dev/null -w "%{http_code}\n" $$ORIGIN/; \
	echo "== robots =="; curl -fsS $$ORIGIN/robots.txt | head -n 5

test-prose:
	PYTHONPATH=. python3 -m pytest -q scripts/prose/tests

test-api:
	$(COMPOSE) run --rm api pytest -q

test-web:
	$(COMPOSE) run --rm web npm test -- --run

test: test-prose test-api
	@echo "Testes da API concluídos. Frontend: cd apps/web && npm test"

ci-local:
	$(COMPOSE) run --rm api pytest -q
	cd apps/web && npm ci && npm run check && npm test -- --run
