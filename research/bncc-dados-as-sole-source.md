# Single data source: bncc-dados, and how we follow their updates

**Status:** research, pass 3  
**Date:** 2026-08-20  
**Depends on:** [bncc-dev-reuse-and-search-modes.md](./bncc-dev-reuse-and-search-modes.md)  
**Decision:** we do **not** extract BNCC (or Arte, or future complements) ourselves. The only curricular source is [bncc-dev/bncc-dados](https://github.com/bncc-dev/bncc-dados). We index, search, and converse on top of whatever snapshot they publish.

---

## 1. Will they add Arte 2026?

**Yes, that is the bet to make — and it is a good one.** We should wait for them rather than start a second pipeline.

Reasons it is likely, not just hopeful:

1. **The schema already has a slot for it.** Their versioning policy names this event type explicitly: *“Novo ato ou complemento”* → new `documento_curricular` linked with `derivado_de`, **without rewriting existing rows**. Computação 2022 was the first proof of that design (`dados/computacao-2022/`). Arte (Parecer CNE/CEB nº 2/2026) is the same shape of object.
2. **It is the job they exist to do.** [bncc.dev/sobre](https://bncc.dev/sobre/) frames the project as “resolver a fundação uma vez, em público.” A CNE complement that is missing is an incomplete foundation. Leaving Arte out indefinitely would contradict that.
3. **They already absorbed one complement years after the parecer.** Computação is Resolução CNE/CEB 1/2022; it shipped in their first public dataset in July 2026. So “they add complements” is observed behaviour, not a roadmap slide. Arte’s parecer is March 2026; the org now exists, so the lag should be **shorter** than Computação’s, but it is still measured in weeks-to-months of careful extraction, not days.
4. **They version content separately from schema.** A new document can land as `dados-2026.MM` with `schema-v1.x` if the model is additive. Our loader should be “every `documento_curricular` in the snapshot,” not “hard-code BNCC 2018 + CO.” Then Arte arrives as more rows.

What we should **not** assume:

- **Date.** There is no public issue/milestone for Arte in the repos we saw. Do not promise Arte in our UI until `data_version` contains it.
- **Identical modelling.** Arte may need new organization types (they insist on “honestidade estrutural”). If that needs `schema-v2`, our updater must stop and get a human, not invent fields.
- **Intro essays / estaduais.** Those are still out of scope unless they publish them. We still do not scrape MEC ourselves.

Optional, cheap, **not a pipeline:** a monthly glance at CNE/MEC “normas da BNCC” only to know if *we* are behind *them*. If CNE published something and `bncc-dados` has no new `dados-*` tag in 90 days, that is a product note (“a Base oficial tem um complemento que ainda não entrou no recorte”), not a reason to write `extrair_arte.py`.

---

## 2. Only their dataset — what that means in practice

| We do | We do not |
|---|---|
| Consume **immutable GitHub releases** tagged `dados-YYYY.MM` / `dados-YYYY.MM.N` | Clone `main` and hope |
| Keep a pinned `data_version` in our DB and in the UI (“recorte dados-2026.07.1”) | Float with PyPI/npm (`bncc==0.2.1` is a **package** version, already lagged the dataset patch) |
| Re-embed rows whose `texto` or metadata changed | Re-parse PDFs, re-decide spreadsheet vs homologated PDF |
| Honour `vigencia` (never delete; hide `revogado` from default Buscar) | Invent codes, dummy enunciados, “fix” official texts, or merge Arte from another source |
| Attribute CC BY 4.0 on Sobre/footer | Runtime calls to `api.bncc.dev` / MCP for serving users |

Canonical files they tell consumers to use: **JSON in the tagged tree**. Release assets also include `bncc.sqlite` and `bncc-csv.zip` ([dados-2026.07.1](https://github.com/bncc-dev/bncc-dados/releases/tag/dados-2026.07.1)). JSON is the source of truth for ingest; SQLite is a convenience if it stays in lockstep (their CI generates it). Prefer JSON + their schemas so a schema bump is visible.

Their own rule for consumers ([docs/versionamento.md](https://github.com/bncc-dev/bncc-dados/blob/main/docs/versionamento.md)):

> Fixe a data-version que você validou; atualize deliberadamente lendo o changelog.

“Deliberately” does **not** mean a human copies files by hand. It means: **do not silently track `main`**. Detect a new *tag*, read CHANGELOG category, validate, then apply.

Zenodo ([10.5281/zenodo.21625233](https://doi.org/10.5281/zenodo.21625233)) is their long-term archive (concept DOI always points at latest). Good as a **backup if GitHub is down**, bad as the primary trigger (deposits are still partly manual).

---

## 3. Smarter than a dumb daily full pull

A daily cron that `git clone`s the whole repo is wasteful but would work: they release on the order of **once a month or less** so far (2026-07-27, then patch 2026-08-11). BNCC does not change daily. The smart version is **conditional poll of releases, not of files**.

We cannot attach a webhook to their repo. GitHub Watch is for humans. So the machine-side “push” does not exist unless they add one later. **Polling GitHub Releases with HTTP caching is the right consumer protocol.**

### 3.1 Signal (cheap)

GitHub Action in **our** repo, cron `0 0 1 * *` (once a month is enough; they release on the order of once a month or less):

```http
GET https://api.github.com/repos/bncc-dev/bncc-dados/releases
If-None-Match: "<etag-we-stored>"
Accept: application/vnd.github+json
```

- `304 Not Modified` → stop. No download, no embed, no deploy.
- `200` → keep new ETag; consider only releases whose `tag_name` matches `^dados-` (ignore `schema-v*` and leftover `v1.0.0` aliases unless we also track schema).
- Compare `tag_name` to our pinned version (semver-ish: `dados-2026.08` > `dados-2026.07.1` by date, then patch).

Equivalent human/debug channel: [releases.atom](https://github.com/bncc-dev/bncc-dados/releases.atom). Same information; the REST API is easier to parse and already supports ETag.

**Do not use as the primary signal:**

| Channel | Why not |
|---|---|
| `main` commits | Unreleased work; CI might be red; tags are the contract |
| PyPI `bncc` / npm `@bncc/dados` | Separate repo, own semver, sync script can lag; 1.0.0 of packages is still waiting on their “dados-v1.0.0” naming |
| `GET api.bncc.dev/v1/estatisticas` → `data_version` | Useful as a *secondary* check, but we refused their API as a serving dependency; it can lag GitHub or hit rate limits |
| Zenodo | Manual deposit today; extra hop |

If we want a belt: after a GitHub hit, confirm `data_version` in the downloaded JSON matches the tag.

### 3.2 Fetch (only on new tag)

Download the **immutable** zipball or the release assets of that tag, never `HEAD`:

`https://github.com/bncc-dev/bncc-dados/archive/refs/tags/dados-2026.07.1.tar.gz`

or `…/releases/download/dados-2026.07.1/bncc.sqlite`.

Verify checksum if GitHub provides `digest` on assets (they already publish sha256 on the sqlite/csv assets).

### 3.3 Apply (our job, not theirs)

1. Validate JSON against the schemas **shipped in that same tag** (if `schema` major jumps, **halt**).
2. Diff against current DB: new codes, changed `texto`, changed metadata, new `vigencia.ate`.
3. Re-embed **only changed/new** rows (cloud embedder; 1.721 rows even full reindex is cheap).
4. Rebuild FTS. Reranker has no index to rebuild.
5. Invalidate answer cache for any cited code that changed.
6. Bump `data_version` shown in the UI.

Loader rule so Arte is free later: iterate **all documents in the snapshot**, do not whitelist `bncc-2018` and `computacao-2022`.

### 3.4 How automatic vs how deliberate

Match their changelog categories:

| Their category | Example | Our automation |
|---|---|---|
| `correcao` | 11 texts in `dados-2026.07.1` | Auto-apply after CI green. Same schema, same codes, better text. |
| `normativa` | Computação; **Arte when it comes** | Auto-detect, open a PR (or a staging ingest) with the CHANGELOG blurb. Auto-merge if schema still 1.x **and** the loader already accepts unknown `documento_curricular` IDs. Otherwise wait for a human. |
| `schema` minor | New optional field | Auto-apply; ignore unknown fields until we use them. |
| `schema` major | Breaking rename | **Stop.** Notify. Do not ingest. |
| `editorial` | Docs only | Ignore (no `dados-*` tag anyway). |

That is the spirit of “update deliberately”: machines apply patches; humans glance at new complements and schema breaks. Daily cron without this gate would still be safe *most* of the time, but a schema major on a Sunday should not silently empty Matemática.

### 3.5 Failure modes

- **They skip a GitHub Release and only push `main`.** Then we lag until they tag. That is correct. Ping them; do not track `main`.
- **Packages update, git tags do not (or the reverse).** Git tags win.
- **Arte lands with a new code grammar.** Decoder tests fail → halt, then extend decoder from *their* `pipeline/codigos.py` (MIT) in the same tag, still no PDF pipeline.
- **We are down during a release.** Next cron picks it up. Releases are immutable.

---

## 4. Recommended shape in our repo

Keep it small. The watch job and the ingest job run against the **same** Postgres Compose used to serve users. No parallel “import into SQLite for now.”

```
vendor/bncc-dados/          # optional git subtree or just a VERSION file
  VERSION                   # dados-2026.07.1
  ETAG                      # last GitHub releases ETag
scripts/check_bncc_release.py
scripts/ingest_bncc_snapshot.py
.github/workflows/bncc-dados-watch.yml   # cron + workflow_dispatch
```

A **git submodule pinned to the tag**, with the watch workflow opening a PR that bumps the submodule, is the cleanest “single source” story: `git diff` is their commit, review is our CHANGELOG read, merge runs ingest. Slightly nicer than copying JSON into our tree, and still not a parallel extractor.

Watching their repo as a GitHub user (Releases only) is the human backup if Actions is misconfigured.

---

## 5. Decisions for this pass

| Topic | Decision |
|---|---|
| Parallel PDF/spreadsheet pipeline | **No.** Not for Arte, not for errata. |
| Arte 2026 | Wait for a `dados-*` release that includes it. Model ingest as “all documents in the snapshot.” |
| Serving source | Our DB, filled from their **tagged** snapshot. |
| Update signal | GitHub Releases API + ETag, cron 1–2×/day. Not PyPI, not `main`, not their live API. |
| Auto-apply | `correcao` and additive `normativa`/`schema` minor. Halt on schema major. |
| UI | Always show the pinned recorte. If CNE is ahead of bncc-dados, optional Sobre note — still no homemade data. |

---

## 6. Sources

- [Versionamento · bncc-dados](https://github.com/bncc-dev/bncc-dados/blob/main/docs/versionamento.md)
- [Releases](https://github.com/bncc-dev/bncc-dados/releases) and [releases.atom](https://github.com/bncc-dev/bncc-dados/releases.atom)
- [Latest release API](https://api.github.com/repos/bncc-dev/bncc-dados/releases/latest) (`tag_name`: `dados-2026.07.1`)
- [Modelo de dados](https://github.com/bncc-dev/bncc-dados/blob/main/docs/modelo-de-dados.md) (multi-document, `derivado_de`)
- [bncc-pacotes](https://github.com/bncc-dev/bncc-pacotes) (packages sync from a pinned commit; not the dataset SoT)
