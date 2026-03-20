# Fluo Proto

FastAPI + Jinja2 + SQLite prototype for orientation requests (demandes d'orientation).

## Architecture

This is a clickable prototype — no auth, no real API, just enough to demonstrate the UX of receiving and processing orientation requests.

- **app.py** — all routes (list, detail, accept/refuse, messages, orienteur reply)
- **db.py** — SQLite schema + query helpers, file-based `data.db`
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
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8002
```

## Seed / reset database

```bash
rm -f data.db && uv run python seed.py
```

## Deploy to Scaleway (STARDUST1-S)

Instance: `163.172.180.4` (fluo-proto-stardust)
URL: http://163.172.180.4:8002/

```bash
# Sync files
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' --exclude='data.db' --exclude='.DS_Store' --exclude='docs/' --exclude='.superpowers/' ./ root@163.172.180.4:/opt/fluo-proto/

# Re-seed and restart
ssh root@163.172.180.4 "cd /opt/fluo-proto && rm -f data.db && /root/.local/bin/uv run python seed.py && systemctl restart fluo-proto"
```

Full setup on a fresh instance:
```bash
apt-get update -qq && apt-get install -yqq python3 python3-venv curl
curl -LsSf https://astral.sh/uv/install.sh | sh
mkdir -p /opt/fluo-proto
# rsync files (see above)
cd /opt/fluo-proto && /root/.local/bin/uv sync && /root/.local/bin/uv run python seed.py
# create /etc/systemd/system/fluo-proto.service then:
systemctl daemon-reload && systemctl enable --now fluo-proto
```
