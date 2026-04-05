# Fluo Proto Factory

Monorepo that produces throwaway prototypes for product design, user testing, and fast iteration. Each prototype lives under `prototypes/<name>/` as a self-contained FastAPI + Jinja2 + PostgreSQL app visually identical to [les-emplois](https://github.com/gip-inclusion/les-emplois).

"Fluo" is the overall endeavour. Individual protos are named after what they explore (e.g., `demandes` for orientation requests, `recs` for recommendations).

## Layout

```
fluo-proto-factory/
├── _template/            — the scaffold (copied into each new proto by copier)
├── prototypes/           — one subdirectory per proto, fully self-contained
│   └── demandes/         — orientation requests for PLIE Lille Avenir
├── Makefile              — operator commands (make help lists them)
├── copier.yml            — copier config for `make new`
├── ruff.toml             — shared lint config
├── scripts/              — provision.sh, fetch-assets.sh
├── .githooks/pre-commit  — lint + URL guard
├── PROTOTYPE.md          — the guide for building a new proto (read this)
└── .github/workflows/    — CI (lint) and deploy (per-proto)
```

## Isolation

- Each proto has its own `Dockerfile`, `pyproject.toml`, `uv.lock`, `docker-compose.yml`, and PostgreSQL database. Nothing shared at runtime.
- Static assets (~4 MB) are duplicated per proto — frozen at creation time.
- Editing `_template/` has zero effect on existing protos. No propagation.
- Each proto has its own database on the shared Scaleway RDB instance.

## Creating a new proto

See `PROTOTYPE.md`. TL;DR:

```bash
make new recs              # scaffold from _template/
make provision recs        # create Scaleway container + DB
make dev recs              # run locally with hot reload
```

## Local dev

```bash
make dev <proto>           # hot reload on localhost:8002
make reseed <proto>        # drop + re-seed local DB
make lint                  # ruff check
make fmt                   # ruff format
```

## Deploy

Push to `main` → GitHub Actions detects which protos changed and runs `make deploy <proto>` for each. Manual: `make deploy <proto>` from a laptop (requires `scw` CLI, docker login, `SCW_REGISTRY` from `~/.config/scw/proto-db.env`).

## Infrastructure

- **Database**: Scaleway Managed PostgreSQL `proto-db` (shared instance, one database per proto).
- **Containers**: Scaleway Serverless Containers (one per proto, 256 MB / 140 mVCPU / min-scale=1 / privacy=public).
- **Registry**: Scaleway Container Registry (one image per proto, tagged by proto name). `SCW_REGISTRY` is the namespace path only (e.g. `rg.fr-par.scw.cloud/nova-container-registry`); per-proto images live at `$SCW_REGISTRY/<proto>:latest`.
- **Secrets**: factory-level GitHub secrets cover all protos (`SCW_ACCESS_KEY`, `SCW_SECRET_KEY`, `SCW_REGISTRY`, `SCW_PROJECT_ID`, `SCW_ORG_ID`). Operator credentials live in `~/.config/scw/proto-db.env` (never in the repo).
- **DATABASE_URL** is set on each Scaleway container at provision time, never in the repo.
- **Container lookup**: `make deploy` finds containers by name (`scw container container list name=<proto>`), no IDs stored in the repo.

## URL privacy

Public proto URLs are **not** stored in the repo. The pre-commit hook blocks any attempt to commit a `*.functions.fnc.fr-par.scw.cloud` URL. Use `make urls` to list all current URLs locally.

## Design system (applies to every proto)

- **CSS class prefixes**: `s-` sections, `c-` components. Always use `__container` / `__row` / `__col` BEM nesting.
- **c-box variants**: `c-box--action` (dark), `c-box--note` (light). Plain `c-box` = white card.
- **list-data / list-note / list-step**: expect exact markup structure from les-emplois.
- **Remix Icons**: `ri-*` classes, loaded via app.css. Use `fw-medium` after icon class.
- **Badges**: `badge-sm` (tables), `badge-base` (titles). Both need `rounded-pill text-nowrap`.
- **Body class**: `l-authenticated` triggers permanent sidebar on xl+ screens.

See `PROTOTYPE.md` for the full design-system reference, template patterns, and common pitfalls.

## Commit rules

- Atomic, one-line commits.
- No "co-authored by Claude" trailers.
