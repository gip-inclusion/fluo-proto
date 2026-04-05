# demandes

Prototype for processing orientation requests (demandes d'orientation) at PLIE Lille Avenir.

## What it demonstrates

Two user views without auth, sharing the same fictitious data:

- **PLIE side** (`/plie/...`) — the receiving service processes incoming orientations: list, detail, accept/refuse, exchange messages, view history.
- **Prescripteur side** (`/prescripteur/...`) — the sender views status and replies to messages.

Status flow: `nouvelle` → `acceptee` / `refusee`.

## Seed data

5 mock orientations with diagnostic data, seeded by `web/seed.py`. See `web/config.py` for the label dictionaries.

## Run locally

From the factory root:

```bash
make dev demandes
```

This starts the local PostgreSQL via docker-compose and runs uvicorn with `--reload` on port 8002.

First run only — seed the database:

```bash
cd prototypes/demandes
DATABASE_URL=postgresql+psycopg://demandes:demandes@localhost:5432/demandes uv run python -m web.seed
```

After any local schema change, reseed: `make reseed demandes` from the factory root.

## Deploy

From the factory root:

```bash
make deploy demandes
```

Deploys to the existing Scaleway Serverless Container. Push to `main` triggers the same flow via GitHub Actions.

## Auth

This proto has no auth — the fictitious-data banner + obscure Scaleway URL are the only protection. See `../../PROTOTYPE.md` for the auth recipe if needed.
