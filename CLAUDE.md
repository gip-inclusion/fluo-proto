# Fluo Proto

FastAPI + Jinja2 + PostgreSQL prototype for orientation requests (demandes d'orientation).

## Architecture

This is a clickable prototype — no auth, no real API, just enough to demonstrate the UX of receiving and processing orientation requests.

- **app.py** — all routes (list, detail, accept/refuse, messages, orienteur reply)
- **db.py** — PostgreSQL queries via psycopg, connects via `DATABASE_URL` env var
- **seed.py** — 5 mock orientations with diagnostic data, history events, messages
- **templates/** — Jinja2 templates, `base.html` + page templates + `includes/` partials
- **static/** — vendored CSS/JS/fonts (not in git, see below)

Two user views without auth:
- `/` and `/orientation/{id}` — the receiving service (PLIE Lille Avenir) processes incoming orientations
- `/orientation/{id}/orienteur` — the sender can view status and exchange messages

Status flow: `nouvelle` → `acceptee` / `refusee`

## Relation to les-emplois

This prototype reproduces the look and UX of [les-emplois](https://github.com/gip-inclusion/les-emplois) (the "Candidatures reçues" / candidature detail pages), repurposed for orientation requests.

The design system comes from les-emplois via `theme-inclusion`. Static assets are copied from les-emplois into `static/vendor/`:
- `theme-inclusion/` — CSS (`app.css`), fonts (Marianne, Remix Icons), images, JS
- `bootstrap/` — Bootstrap 5 JS + Popper
- `jquery/` — jQuery (required by some theme-inclusion components)

`static/css/itou.css` is a copy of les-emplois custom styles needed on top of theme-inclusion.

All of `static/vendor/` and `static/css/itou.css` are gitignored. To restore them, copy from les-emplois:
```bash
cp -r /path/to/les-emplois/itou/static/vendor/theme-inclusion static/vendor/
cp -r /path/to/les-emplois/node_modules/bootstrap/dist/js/{bootstrap.min.js,bootstrap.min.js.map} static/vendor/bootstrap/
cp -r /path/to/les-emplois/node_modules/@popperjs/core/dist/umd/{popper.min.js,popper.min.js.map} static/vendor/bootstrap/
cp /path/to/les-emplois/itou/static/vendor/jquery/jquery.min.js static/vendor/jquery/
cp /path/to/les-emplois/itou/static/css/itou.css static/css/
```

## Design system gotchas

- **CSS class prefixes**: sections use `s-` (`s-section`, `s-title-02`, `s-header-authenticated`), components use `c-` (`c-box`, `c-title`, `c-prevstep`). Always wrap content in the expected `__container` / `__row` / `__col` nesting or spacing breaks.
- **c-box variants**: `c-box--action` (dark action bar), `c-box--note` (light note card). Plain `c-box` is a white card with shadow.
- **list-data / list-note / list-step**: specific `<ul>` patterns from les-emplois for key-value info, notes, and timeline steps. They expect exact markup structure — check les-emplois source if something looks off.
- **Remix Icons**: loaded via `app.css` (compiled in), not a separate CSS file. Use `ri-*` classes. `fw-medium` after the icon class for consistent weight.
- **Badge sizes**: `badge-sm` for small (in tables), `badge-base` for normal (in titles). Both need `rounded-pill text-nowrap`.
- **Bootstrap tabs**: use standard BS5 tab markup (`nav-tabs`, `data-bs-toggle="tab"`, `tab-pane`). The theme overrides styling but the JS API is standard.
- **Offcanvas sidebar**: the left nav uses Bootstrap's offcanvas. The `l-authenticated` body class triggers the layout that shows it permanently on large screens.
- **btn-dropdown-filter**: the filter bar dropdown pattern. Needs `btn-dropdown-filter-group` wrapper, `dropdown` inside a `<form>`, checkboxes with `onchange="this.form.submit()"`.
- **Diagnostic section**: renders JSON from France Travail's Diagnostic Argumenté v4 API. Each category (projet pro, contraintes, pouvoir d'agir, autonomie numérique) is a `c-box` with a colored `border-start border-4`.

## Dev server

```bash
DATABASE_URL="postgresql://fluo:Fl4o-pR0t0-2026x@REDACTED_DB_ENDPOINT/fluo" uv run uvicorn app:app --reload --host 0.0.0.0 --port 8002
```

## Seed / reset database

```bash
DATABASE_URL="postgresql://fluo:Fl4o-pR0t0-2026x@REDACTED_DB_ENDPOINT/fluo" uv run python seed.py
```

To reset, drop and recreate tables manually or drop/recreate the database via `scw rdb`.

## Deploy

**Push to main → auto-deploys** via GitHub Actions (`.github/workflows/deploy.yml`).

The action builds a Docker image (linux/amd64), pushes to the Scaleway container registry, and redeploys the serverless container.

### Infrastructure

- **Database**: Scaleway Managed PostgreSQL DB-DEV-S `proto-db` (shared across prototypes)
  - Instance ID: `REDACTED_DB_INSTANCE_ID`
  - Endpoint: `REDACTED_DB_ENDPOINT`
  - Database: `fluo`, user: `fluo` (separate DB per prototype)
  - Admin creds: `~/.config/scw/proto-db.env`
- **Container**: Scaleway Serverless Container (140 mVCPU / 256 MB)
  - Container ID: `REDACTED_CONTAINER_ID`
  - URL: https://REDACTED_CONTAINER_URL
  - Namespace: `nova` (`REDACTED_NAMESPACE_ID`)
- **Registry**: `REDACTED_REGISTRY`
- **GitHub Secrets**: `SCW_ACCESS_KEY`, `SCW_SECRET_KEY`, `SCW_CONTAINER_ID`, `DATABASE_URL`

### Manual deploy

```bash
docker buildx build --platform linux/amd64 -t REDACTED_REGISTRY:latest . --push
scw container container deploy REDACTED_CONTAINER_ID region=fr-par
```

### Adding a new prototype to the shared DB

```bash
scw rdb database create instance-id=REDACTED_DB_INSTANCE_ID name=<proto_name>
scw rdb user create instance-id=REDACTED_DB_INSTANCE_ID name=<proto_name> password=<password>
scw rdb privilege set instance-id=REDACTED_DB_INSTANCE_ID database-name=<proto_name> user-name=<proto_name> permission=all
```

### Gotcha: static assets not in git

`static/vendor/` and `static/css/itou.css` are gitignored (too large). They are baked into the Docker image at build time. If they're missing locally, copy from les-emplois (see "Relation to les-emplois" above).
