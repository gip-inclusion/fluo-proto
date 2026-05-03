# flux

A design-time tool for prototyping a re-architecture of [les-emplois](https://github.com/gip-inclusion/les-emplois). Flux turns a YAML description of actors, flows, screens, tabs, blocks and edges into a clickable, production-fidelity prototype rendered with the live itou theme.

Audience: product / design / engineering reviewing the re-arch. **Not** for end users.

## Run locally

```bash
make dev flux             # http://localhost:8002
```

Flux has no database — `docker compose up -d` is a no-op for this proto, and uvicorn serves directly from the YAML in `flows/`.

Edit any file under `flows/`; the model reloads and the browser refreshes automatically (SSE).

## Deploy

```bash
make deploy flux
```

## Layout

```
prototypes/flux/
├── flows/                    # authored YAML — the only thing you edit day-to-day
│   ├── flux.yaml             # actors + list of flow files
│   └── employer.yaml         # one file per flow
└── web/
    ├── app.py                # FastAPI lifespan: load + watch flows/
    ├── config.py
    ├── dsl/
    │   ├── models.py         # Pydantic models for the whole DSL
    │   ├── loader.py         # YAML → FluxModel, captures errors as Diagnostics
    │   ├── validate.py       # edge resolution (every `to:` / `opens:` etc.)
    │   └── graph.py          # Mermaid emitter
    ├── routes/
    │   ├── render.py         # GET /<flow>/<screen>
    │   ├── graph.py          # GET /_graph[/<flow>]
    │   └── diagnostics.py    # GET /_diagnostics
    ├── static/css/flux.css   # minimal flux-only overrides
    └── templates/
        ├── base.html
        ├── archetypes/       # page, modal, dashboard
        ├── blocks/           # search, kpi_row, card_*, box, table, filterbar
        └── partials/         # menu_*, tabs, actions, prevstep, diagnostics_banner
```

## DSL — quick reference

Top-level (`flows/flux.yaml`):

```yaml
actors:
  employer:    { label: Employeur, org: "Une nouvelle chance (ETTI)" }
flows:
  - employer.yaml
```

Per flow (`flows/<name>.yaml`):

```yaml
flow:
  id: employer_hire
  actor: employer
  entry: dashboard
  menu:
    - { id: dashboard, label: Tableau de bord, icon: ri-dashboard-line }

screens:
  dashboard:
    kind: dashboard            # page | modal | dashboard
    title: Tableau de bord
    nav_item: dashboard
    blocks:
      - kpi_row:
          tiles:
            - { label: "À traiter", value: 12, to: candidatures_list }
      - card:
          title: Dernières candidatures
          to: candidatures_list

  candidatures_list:
    kind: page
    title: Candidatures reçues
    body:
      - filter_bar: { filters: [status, date_range] }
      - table: { count: 12, rows_to: candidature_detail }
```

See `../../PROTOTYPE.md` for the les-emplois CSS conventions used by all flux templates, and `flows/employer.yaml` for a worked example covering every block, tabs and a modal.

## URLs

- `/<flow>/<screen>` — render a screen
- `/_graph` — all flows as Mermaid diagrams
- `/_graph/<flow>` — single flow
- `/_diagnostics` — schema + edge errors
