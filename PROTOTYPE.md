# Building a les-emplois-like prototype

Guide for an agent building a visually identical prototype to [les-emplois](https://github.com/gip-inclusion/les-emplois), with variant features and modular tab-based layouts. This documents the approach used for fluo-proto and can be followed step-by-step.

## Overview

The goal is to produce a clickable prototype that looks indistinguishable from les-emplois but implements different domain logic. No auth, no real API — just FastAPI + Jinja2 + PostgreSQL (via SQLModel) with vendored static assets from les-emplois.

## Step 1: Extract the design system from les-emplois

The visual identity lives in three layers. You need all three.

### Layer 1: theme-inclusion (the design system)

This is the shared CSS/JS/fonts/images package used by all Plateforme de l'inclusion products. Copy the essential files:

```bash
# Use the provided script
./scripts/fetch-assets.sh /path/to/les-emplois
```

This gives you:
- `stylesheets/app.css` — the compiled CSS (Bootstrap 5 + custom theme)
- `fonts/marianne/` — the Marianne typeface (French government)
- `fonts/remixicon/` — Remix Icons (`remixicon.woff2` + `.woff` only — browsers don't need the other formats)
- `images/` — logos, pictos, illustrations
- `javascripts/app.js` — theme JS

### Layer 2: Bootstrap + jQuery (JS dependencies)

```bash
mkdir -p static/vendor/bootstrap static/vendor/jquery
cp /path/to/les-emplois/node_modules/bootstrap/dist/js/bootstrap.min.js static/vendor/bootstrap/
cp /path/to/les-emplois/node_modules/bootstrap/dist/js/bootstrap.min.js.map static/vendor/bootstrap/
cp /path/to/les-emplois/node_modules/@popperjs/core/dist/umd/popper.min.js static/vendor/bootstrap/
cp /path/to/les-emplois/node_modules/@popperjs/core/dist/umd/popper.min.js.map static/vendor/bootstrap/
cp /path/to/les-emplois/itou/static/vendor/jquery/jquery.min.js static/vendor/jquery/
```

### Layer 3: itou.css (les-emplois custom styles)

On top of theme-inclusion, les-emplois has its own CSS for components like `list-data`, `list-note`, `list-step`, `c-box`, `c-prevstep`, etc. Without this file, many layout patterns won't render correctly.

```bash
mkdir -p static/css
cp /path/to/les-emplois/itou/static/css/itou.css static/css/
```

### Assets are committed to git

Static assets are trimmed (~4MB) and committed to git. This ensures CI builds produce complete Docker images. To refresh assets after a design system update, run `scripts/fetch-assets.sh` and commit the result.

## Step 2: Prototype banner

Every prototype **must** display a prominent red banner stating it uses fictitious data. This is a non-negotiable part of the methodology — it prevents any confusion with the real application.

les-emplois uses this pattern on its demo/staging environments (`DEMO - Données fictives`). We reproduce it with the text "PROTOTYPE" instead.

Add this between `</header>` and `<main>` in your base template:

```html
<div class="global-messages-container">
    <div class="alert alert-danger alert-dismissible fade show" role="status">
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fermer"></button>
        <strong>PROTOTYPE – Données fictives</strong>
    </div>
</div>
```

This renders a full-width red bar at the top of every page. It uses Bootstrap's `alert alert-danger` classes (styled by theme-inclusion) and the `global-messages-container` wrapper from les-emplois.

## Step 3: Base template

The base template establishes the authenticated layout. Key elements:

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <link rel="stylesheet" href="/static/vendor/theme-inclusion/stylesheets/app.css">
    <link rel="stylesheet" href="/static/css/itou.css">
</head>
<body class="l-authenticated">
    <header><!-- see below --></header>
    <main id="main" role="main" class="s-main">
        {% block content %}{% endblock %}
    </main>
    <script src="/static/vendor/jquery/jquery.min.js"></script>
    <script src="/static/vendor/bootstrap/popper.min.js"></script>
    <script src="/static/vendor/bootstrap/bootstrap.min.js"></script>
</body>
</html>
```

**Critical**: the `l-authenticated` body class activates the sidebar layout on large screens.

### Header structure

The header has three parts:

1. **Logo column** — links to home, uses a Plateforme de l'inclusion logo
2. **Nav column** — "Mon espace" dropdown (right-aligned), only visible on `sm+`
3. **Burger column** — triggers the offcanvas sidebar

### Offcanvas sidebar

The left navigation uses Bootstrap's offcanvas component. On large screens (`xl+`), `l-authenticated` makes it permanently visible. On smaller screens, the burger button opens it.

```html
<div class="offcanvas" id="offcanvasNav">
    <div class="offcanvas-header offcanvas-header--organization">
        <!-- Organization name -->
    </div>
    <div class="offcanvas-body d-flex flex-column">
        <nav>
            <ul class="nav nav-tabs flex-column mb-3">
                <li class="nav-item">
                    <a href="/" class="nav-link active">
                        <i class="ri-compass-line fw-medium" aria-hidden="true"></i>
                        <span>Orientations</span>
                    </a>
                </li>
                <!-- more nav items -->
            </ul>
        </nav>
    </div>
</div>
```

## Step 4: The page section pattern

Every page in les-emplois follows this nesting:

```html
<section class="s-title-02">
    <div class="s-title-02__container container">
        <div class="s-title-02__row row">
            <div class="s-title-02__col col-12">
                <!-- title, breadcrumb, action bar, tabs -->
            </div>
        </div>
    </div>
</section>

<section class="s-section">
    <div class="s-section__container container">
        <div class="s-section__row row">
            <div class="s-section__col col-12 col-xxl-8">
                <!-- main content -->
            </div>
        </div>
    </div>
</section>
```

**Always** use the `__container` / `__row` / `__col` BEM suffixes. The theme applies margins, padding, and max-widths on these. If you skip them, spacing breaks.

## Step 5: Component patterns

### c-title (page title)

The standard page title wrapper:

```html
<div class="c-title">
    <div class="c-title__main">
        <h1>
            Page Title
            <span class="badge rounded-pill text-nowrap badge-base bg-info">Status</span>
        </h1>
    </div>
</div>
```

### c-prevstep (back link)

The standard "back" link placed above the title on detail pages:

```html
<div class="c-prevstep">
    <a href="/" class="btn btn-ico btn-link ps-0">
        <i class="ri-arrow-drop-left-line ri-xl fw-medium" aria-hidden="true"></i>
        <span>Retour à la liste</span>
    </a>
</div>
```

### c-box (card)

The basic content card. All info sections live inside these.

```html
<div class="c-box mb-3 mb-md-4">
    <h3>Section title</h3>
    <!-- content -->
</div>
```

Variants:
- `c-box--action` — dark background, used for the accept/refuse action bar
- `c-box--note` — lighter background, used for the message quick-compose sidebar

### c-box with header row (card with action button)

A c-box with a title and a disabled action button aligned right:

```html
<div class="c-box mb-3 mb-md-4">
    <div class="row mb-3">
        <div class="col-12 col-sm">
            <h3 class="mb-0">Section Title</h3>
        </div>
        <div class="col-12 col-sm-auto mt-2 mt-sm-0 d-flex align-items-center">
            <span class="btn btn-ico btn-outline-primary disabled">
                <i class="ri-pencil-line fw-medium" aria-hidden="true"></i>
                <span>Modifier</span>
            </span>
        </div>
    </div>
    <!-- content -->
</div>
```

### c-box--action (action bar)

The dark action bar used for accept/refuse/dropdown actions on detail pages. Placed inside `s-title-02`, after the title, before the tabs.

When actions are available (status == "nouvelle"):
```html
<div class="c-box c-box--action">
    <h2 class="visually-hidden">Actions rapides</h2>
    <div class="form-row align-items-center gx-3">
        <div class="form-group col-12 col-lg-auto">
            <form method="post" action="/orientation/{{ o.id }}/accept">
                <button type="submit"
                        class="btn btn-lg btn-link-white btn-block btn-ico justify-content-center">
                    <i class="ri-check-line fw-medium" aria-hidden="true"></i>
                    <span>Accepter</span>
                </button>
            </form>
        </div>
        <div class="form-group col-12 col-lg-auto">
            <form method="post" action="/orientation/{{ o.id }}/refuse">
                <button type="submit"
                        class="btn btn-lg btn-link-white btn-block btn-ico">
                    <i class="ri-close-line fw-medium" aria-hidden="true"></i>
                    <span>Refuser</span>
                </button>
            </form>
        </div>
        <div class="form-group col-12 col-lg d-lg-flex justify-content-lg-end">
            <div class="dropdown">
                <button class="btn btn-lg btn-link-white btn-block w-lg-auto dropdown-toggle"
                        type="button" data-bs-toggle="dropdown">
                    Autres actions
                </button>
                <div class="dropdown-menu w-100">
                    <span class="dropdown-item text-muted">Aucune action disponible</span>
                </div>
            </div>
        </div>
    </div>
</div>
```

When already resolved (status badge only):
```html
<div class="c-box c-box--action">
    <div class="d-flex align-items-center gap-3 px-3 py-2">
        <span class="badge rounded-pill {{ status_class }} text-white">
            {{ status_label }}
        </span>
    </div>
</div>
```

### list-data (key-value pairs)

The main pattern for displaying structured info (person details, sender info, etc.):

```html
<ul class="list-data mb-3">
    <li>
        <small>Label</small>
        <strong>Value</strong>
    </li>
    <li>
        <small>Another label</small>
        <strong>Another value</strong>
    </li>
</ul>
```

For empty values: `<i class="text-disabled">Non renseigné</i>`

For long-form text (messages, blockquotes) in a list-data item, add `class="has-forced-line-break"` on the `<li>`:

```html
<ul class="list-data mb-3">
    <li class="has-forced-line-break">
        <small>Message</small>
        <blockquote class="blockquote mt-2 mb-0">
            <p>Long text here...</p>
        </blockquote>
    </li>
</ul>
```

### list-note (messages / notes)

Used for message lists and threaded conversations:

```html
<ul class="list-note">
    <li>
        <div>
            <time class="fs-xs text-muted">2025-03-12 à 10:30</time>
            <strong class="d-block">Author Name</strong>
            <blockquote class="blockquote mt-1 mb-0">
                <p>Message content here</p>
            </blockquote>
        </div>
    </li>
</ul>
```

Add `class="is-current-user"` on `<li>` for the current user's messages. Add `(vous)` after the author name.

### list-step (timeline / history)

```html
<ul class="list-step">
    <li>
        <time datetime="2025-03-12T10:30:00">Le 2025-03-12 à 10:30</time>
        <span>Event description</span>
    </li>
</ul>
```

### Badges

```html
<!-- Small badge (in tables) -->
<span class="badge rounded-pill text-nowrap badge-sm bg-info">Label</span>

<!-- Normal badge (in titles) -->
<span class="badge rounded-pill text-nowrap badge-base bg-success">Label</span>

<!-- Extra-small badge (inline annotations) -->
<span class="badge badge-xs rounded-pill bg-warning">Label</span>
```

Status colors: `bg-info` (blue, new), `bg-success` (green, accepted), `bg-danger` (red, refused), `bg-secondary` (grey, unknown), `bg-warning` (yellow, annotations like "Prescripteur habilité").

Lighter variants for inline status indicators: `bg-info-lighter text-info`, `bg-success-lighter text-success`.

### Buttons with icons

```html
<button class="btn btn-lg btn-link-white btn-block btn-ico">
    <i class="ri-check-line fw-medium" aria-hidden="true"></i>
    <span>Accepter</span>
</button>
```

Always add `fw-medium` after the Remix Icon class for consistent weight. Always set `aria-hidden="true"` on decorative icons.

Button variants used in the prototype:
- `btn-primary` — main actions (submit forms)
- `btn-outline-primary` — secondary actions, icon buttons
- `btn-link-white` — action bar buttons (on dark `c-box--action` background)
- `btn-link` — text-style links (back links, table row links)
- `btn-ico` — button with icon + text
- `btn-ico-only` — icon-only button (use `visually-hidden` span for label)
- `btn-dropdown-filter` — filter bar dropdown trigger

Size modifiers: `btn-sm`, `btn-lg`. Layout: `btn-block` (full-width).

### Icons (Remix Icon)

Icons use the `ri-*` class from Remix Icon. Common icons:

| Icon | Class | Usage |
|------|-------|-------|
| Check | `ri-check-line` | Accept action |
| Close | `ri-close-line` | Refuse action, dismiss |
| Arrow left | `ri-arrow-drop-left-line ri-xl` | Back link (prevstep) |
| Arrow right | `ri-arrow-drop-right-line fs-lg` | Table row "view" link |
| Pencil | `ri-pencil-line` | Edit button |
| Building | `ri-building-line` | Organization |
| Home | `ri-home-line` | Dashboard nav |
| Compass | `ri-compass-line` | Orientations nav |
| Group | `ri-group-line` | Beneficiaries nav |
| Home smile | `ri-home-smile-2-line` | Prescripteur type |
| Community | `ri-community-line` | Other sender type |
| Account | `ri-account-circle-line` | User menu |
| Menu | `ri-menu-line` | Mobile burger |
| Eraser | `ri-eraser-line` | Clear filters |

### Forms

#### Full form (messages tab, orienteur reply)

```html
<div class="c-form mb-3 mb-md-4">
    <form method="post" action="/orientation/{{ o.id }}/message">
        <input type="hidden" name="author_name" value="{{ service_name }}">
        <input type="hidden" name="redirect_to" value="/orientation/{{ o.id }}#messages">
        <div class="form-group">
            <label class="form-label" for="tab-message">Label</label>
            <textarea name="content" id="tab-message" rows="4"
                      class="form-control" required></textarea>
            <div class="form-text">Helper text below the field.</div>
        </div>
        <div class="row">
            <div class="col-12">
                <hr class="mb-3">
                <div class="form-row align-items-center justify-content-end gx-3">
                    <div class="form-group col col-lg-auto">
                        <button type="submit" class="btn btn-block btn-primary">
                            <span>Envoyer</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </form>
</div>
```

#### Compact form (sidebar)

```html
<div class="c-box c-box--note mb-3 mb-md-4">
    <form method="post" action="/orientation/{{ o.id }}/message">
        <input type="hidden" name="author_name" value="{{ service_name }}">
        <input type="hidden" name="redirect_to" value="/orientation/{{ o.id }}">
        <h3>Envoyer un message</h3>
        <div class="form-group">
            <label class="visually-hidden" for="sidebar-message">Message</label>
            <textarea name="content" id="sidebar-message" rows="4"
                      class="form-control" required
                      placeholder="Votre message..."></textarea>
        </div>
        <div class="form-group mt-2">
            <div class="form-row">
                <button class="btn btn-outline-primary btn-sm btn-ico-only bg-white" type="reset">
                    <span class="visually-hidden">Annuler</span>
                    <i class="ri-close-line" aria-hidden="true"></i>
                </button>
                <button class="btn btn-outline-primary btn-sm btn-ico-only bg-white" type="submit">
                    <span class="visually-hidden">Envoyer</span>
                    <i class="ri-check-line" aria-hidden="true"></i>
                </button>
            </div>
        </div>
    </form>
</div>
```

### Filter bar (dropdown checkboxes)

```html
<div class="btn-dropdown-filter-group mb-3 mb-md-4">
    <form method="get" action="/" id="filter-form">
        <div class="dropdown">
            <button type="button"
                    class="btn btn-dropdown-filter dropdown-toggle"
                    data-bs-toggle="dropdown"
                    data-bs-display="static"
                    data-bs-auto-close="outside">
                Filter Label
            </button>
            <ul class="dropdown-menu">
                <li class="dropdown-item">
                    <div class="form-check">
                        <input class="form-check-input"
                               name="status" type="checkbox"
                               value="nouvelle"
                               onchange="this.form.submit()"
                               checked>
                        <label class="form-check-label">Nouvelle demande</label>
                    </div>
                </li>
            </ul>
        </div>

        <!-- Reset link, shown only when filters differ from default -->
        <a href="/" class="btn btn-ico btn-dropdown-filter"
           aria-label="Réinitialiser le filtre actif">
            <i class="ri-eraser-line fw-medium" aria-hidden="true"></i>
            <span>Effacer tout</span>
        </a>
    </form>
</div>
```

`data-bs-auto-close="outside"` keeps the dropdown open when clicking checkboxes. `onchange="this.form.submit()"` submits immediately on toggle.

### Result count

Placed between the filter bar and the table:

```html
<div class="d-flex flex-column flex-md-row align-items-md-center mb-3 mb-md-4">
    <div class="flex-md-grow-1">
        <p class="mb-0" id="orientation-list-count">
            {{ result_count }} résultat{{ "s" if result_count != 1 else "" }}
        </p>
    </div>
</div>
```

### Tables (responsive, hoverable)

```html
<div class="table-responsive">
    <table class="table table-hover">
        <caption class="visually-hidden">Accessible description</caption>
        <thead>
            <tr>
                <th scope="col">Name</th>
                <th scope="col">Date</th>
                <th scope="col" class="text-end w-50px"></th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr class="align-top">
                <td>
                    <a class="btn-link" href="/item/{{ item.id }}">
                        {{ item.name }}
                    </a>
                    <span class="d-block text-muted">Subtitle</span>
                    <span class="badge rounded-pill text-nowrap badge-sm bg-info">Status</span>
                </td>
                <td>{{ item.created_at[:10] }}</td>
                <td class="text-end w-50px align-middle">
                    <a class="btn btn-sm btn-link btn-ico-only"
                       href="/item/{{ item.id }}"
                       data-bs-toggle="tooltip"
                       data-bs-title="Voir ce résultat">
                        <i class="ri-arrow-drop-right-line fs-lg"
                           aria-label="Voir {{ item.name }}"></i>
                    </a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

Table cells can contain: links (`btn-link`), badges, muted subtitles (`d-block text-muted`), icons, and a trailing arrow column (`w-50px`).

### Empty state

```html
<div class="c-box mb-3 mb-md-4">
    <p class="text-muted mb-0">Aucun résultat ne correspond aux filtres sélectionnés.</p>
</div>
```

For inline empty states inside a list: `<div class="text-muted fs-sm">Aucun message</div>`

## Step 6: Tab system for modular detail pages

The detail page uses Bootstrap 5 tabs to split content into sections. This is the core modularity pattern — each tab is an independent `includes/` partial.

### Tab navigation (inside `s-title-02`)

```html
<ul class="s-tabs-01__nav nav nav-tabs mb-0" role="tablist">
    <li class="nav-item" role="presentation">
        <a class="nav-link active" id="info-tab"
           data-bs-toggle="tab" href="#info"
           role="tab" aria-controls="info" aria-selected="true">
            Informations
        </a>
    </li>
    <li class="nav-item" role="presentation">
        <a class="nav-link" id="messages-tab"
           data-bs-toggle="tab" href="#messages"
           role="tab" aria-controls="messages" aria-selected="false">
            Messages{% if messages %} ({{ messages|length }}){% endif %}
        </a>
    </li>
</ul>
```

### Tab content (inside `s-section`)

```html
<div class="tab-content">
    <div class="tab-pane fade show active" id="info"
         role="tabpanel" aria-labelledby="info-tab">
        <div class="s-section__row row">
            <div class="s-section__col col-12 col-xxl-8 col-xxxl-9 order-2 order-xxl-1">
                {% include "includes/personal_info.html" %}
                {% include "includes/sender_info.html" %}
            </div>
            <div class="s-section__col col-12 col-xxl-4 col-xxxl-3 order-1 order-xxl-2">
                {% include "includes/messages_sidebar.html" %}
            </div>
        </div>
    </div>

    <div class="tab-pane fade" id="messages"
         role="tabpanel" aria-labelledby="messages-tab">
        {% include "includes/messages_tab.html" %}
    </div>
</div>
```

### How to add a new tab

1. Add a `<li>` to the tab nav
2. Add a `<div class="tab-pane fade">` to the tab content
3. Create a new `includes/your_section.html` partial
4. Use any of the component patterns above inside it

Tabs are fully modular — you can add, remove, or reorder them without touching other code.

## Step 7: The list page pattern

For index/list pages, les-emplois uses a table inside `s-section`:

```html
<section class="s-title-02">
    <div class="s-title-02__container container">
        <div class="s-title-02__row row">
            <div class="s-title-02__col col-12">
                <div class="c-title">
                    <div class="c-title__main">
                        <h1>Page Title</h1>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="s-section">
    <div class="s-section__container container">
        {# Filter bar row #}
        <div class="s-section__row row">
            <div class="col-12">
                <!-- filter bar here -->
            </div>
        </div>
        {# Results row #}
        <div class="s-section__row row">
            <div class="col-12">
                <!-- result count + table here -->
            </div>
        </div>
    </div>
</section>
```

### The detail page pattern

Detail pages combine prevstep + title + action bar + tabs in `s-title-02`, then tab content in `s-section`:

```html
<section class="s-title-02">
    <!-- s-title-02__container > row > col-12 -->
    <div class="c-prevstep"><!-- back link --></div>
    <div class="c-title"><!-- title + badge --></div>
    <div class="c-box c-box--action"><!-- action buttons --></div>
    <ul class="s-tabs-01__nav nav nav-tabs mb-0"><!-- tabs --></ul>
</section>

<section class="s-section">
    <!-- s-section__container > tab-content -->
    <div class="tab-pane ...">
        <div class="s-section__row row">
            <div class="s-section__col col-12 col-xxl-8 col-xxxl-9 order-2 order-xxl-1">
                <!-- main content (c-box cards) -->
            </div>
            <div class="s-section__col col-12 col-xxl-4 col-xxxl-3 order-1 order-xxl-2">
                <!-- sidebar (messages, quick actions) -->
            </div>
        </div>
    </div>
</section>
```

The main content column uses `order-2 order-xxl-1` and the sidebar uses `order-1 order-xxl-2` so that on mobile the sidebar appears first (above), and on desktop it appears on the right.

## Step 8: Template architecture

### Template globals

These variables are available in every template without being passed by routes:

| Variable | Type | Description |
|----------|------|-------------|
| `service_name` | `str` | Current service name ("PLIE Lille Avenir") |
| `status_labels` | `dict` | Maps status key → `(label, css_class)` tuple |
| `event_labels` | `dict` | Maps event type → human label |
| `modalite_labels` | `dict` | Maps modalite key → human label |

Globals are set in `app.py` via `templates.env.globals.update(...)`.

### Custom Jinja2 filters

| Filter | Usage | Result |
|--------|-------|--------|
| `format_datetime` | `{{ msg.created_at\|format_datetime }}` | `2025-03-12 à 14:30` |

Registered in `app.py` via `templates.env.filters["format_datetime"]`.

### Include partials and their expected variables

Each partial in `templates/includes/` expects specific template variables to be set by the route:

| Partial | Required variables |
|---------|-------------------|
| `personal_info.html` | `o` (Orientation object) |
| `sender_info.html` | `o` (Orientation object) |
| `modalite.html` | `modalite_label` (str) |
| `diagnostic.html` | `o_diagnostic_data` (parsed dict from JSON) |
| `messages_tab.html` | `o`, `messages` (list of Message objects) |
| `messages_sidebar.html` | `o`, `messages` (list of Message objects) |
| `history.html` | `history` (list of HistoryEvent objects) |

All partials also have access to template globals (`service_name`, `status_labels`, etc.).

### How templates access the app

Routes get the Jinja2Templates instance via `request.app.state.templates`:

```python
def _templates(request: Request):
    return request.app.state.templates
```

## Step 9: Backend (FastAPI + SQLModel + PostgreSQL)

### Stack

```
uv init --bare
uv add fastapi uvicorn jinja2 python-multipart sqlmodel "psycopg[binary]"
```

`python-multipart` is **required** for form parsing — without it, any `POST` with form data returns 500.

### File structure

```
app.py          — FastAPI setup, mount routers, template globals, custom filters
config.py       — Settings (DATABASE_URL), constants (labels, statuses)
database.py     — SQLModel engine, init_db(), get_session()
models.py       — SQLModel models (Orientation, Message, HistoryEvent)
routes/
  __init__.py   — Re-exports routers
  orientations.py — All orientation routes
seed.py         — Seed script for fictitious data
```

### app.py — thin wiring

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config import EVENT_LABELS, MODALITE_LABELS, SERVICE_NAME, STATUS_LABELS
from database import init_db
from routes import orientations_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.globals.update({
    "service_name": SERVICE_NAME,
    "status_labels": STATUS_LABELS,
    "event_labels": EVENT_LABELS,
    "modalite_labels": MODALITE_LABELS,
})
templates.env.filters["format_datetime"] = lambda v: v[:16].replace("T", " à ") if v else ""
app.state.templates = templates

init_db()
app.include_router(orientations_router)
```

### models.py — SQLModel models

```python
from sqlmodel import Field, SQLModel

class Orientation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: str = Field(default="nouvelle")
    created_at: str
    person_first_name: str
    person_last_name: str
    # ... other fields
    diagnostic_data: str | None = None  # stored as JSON string

class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    orientation_id: int = Field(foreign_key="orientation.id")
    author_name: str
    content: str
    created_at: str

class HistoryEvent(SQLModel, table=True):
    __tablename__ = "history_event"
    id: int | None = Field(default=None, primary_key=True)
    orientation_id: int = Field(foreign_key="orientation.id")
    event_type: str
    created_at: str
```

JSON fields (like `diagnostic_data`) are stored as TEXT and parsed in routes with `json.loads()` before passing to templates.

### Route pattern

Each route file uses `APIRouter`. GET routes render templates, POST routes mutate then redirect (POST-redirect-GET):

```python
from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from database import engine
from models import Orientation

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def list_view(request: Request, status: list[str] = Query(default=["nouvelle"])):
    with Session(engine) as session:
        orientations = session.exec(
            select(Orientation).where(Orientation.status.in_(status))
        ).all()
    return request.app.state.templates.TemplateResponse("list.html", {"request": request, ...})

@router.post("/item/{id}/action")
async def action(id: int):
    with Session(engine) as session:
        item = session.get(Orientation, id)
        item.status = "new_status"
        session.commit()
    return RedirectResponse(f"/item/{id}", status_code=303)
```

### Query parameters for list filtering

FastAPI requires explicit `Query()` for list parameters:

```python
@app.get("/")
async def list_view(request: Request, status: list[str] = Query(default=["nouvelle"])):
```

Without `Query(default=...)`, multiple `?status=a&status=b` params won't parse correctly.

### Local development

```bash
docker compose up -d                     # start local PostgreSQL
DATABASE_URL=postgresql+psycopg://fluo:fluo@localhost:5432/fluo uv run python seed.py
DATABASE_URL=postgresql+psycopg://fluo:fluo@localhost:5432/fluo uv run uvicorn app:app --reload --port 8002
```

The `DATABASE_URL` uses the `postgresql+psycopg://` prefix (required by SQLAlchemy/SQLModel with the psycopg3 driver).

## Step 10: Finding reference markup in les-emplois

When you need to reproduce a specific pattern:

1. Find the page in les-emplois (e.g., candidature detail)
2. Find the Django template: `grep -r "candidature" itou/templates/` or look at the URL patterns
3. The templates use the same Jinja2-compatible syntax (Django templates)
4. Copy the HTML structure, replace Django-specific tags (`{% url %}`, `{% trans %}`) with plain Jinja2
5. Replace `{{ object.field }}` with your own context variables

Key les-emplois template locations:
- Candidature detail: `itou/templates/apply/`
- Candidature list: `itou/templates/apply/`
- Layout: `itou/templates/layout/`
- Components: check for `{% include %}` paths

## Step 11: Deploy with GitHub Actions + Scaleway Serverless Containers

The app is deployed as a Docker image to Scaleway Serverless Containers. GitHub Actions builds and pushes the image on every push to main.

### Dockerfile

```dockerfile
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-install-project
COPY . .
RUN uv sync --frozen --no-cache
EXPOSE 8080
CMD [".venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### GitHub Actions workflow

The deploy workflow builds the Docker image, pushes it to Scaleway's container registry, and triggers a container deploy. Required GitHub secrets: `SCW_ACCESS_KEY`, `SCW_SECRET_KEY`, `SCW_CONTAINER_ID`, `DATABASE_URL`.

The `DATABASE_URL` is set as an environment variable on the Scaleway container, not baked into the image.

## Recipes: how to extend the prototype

### Add a new list page

1. Create a route in `routes/` with `APIRouter`:
   ```python
   @router.get("/items", response_class=HTMLResponse)
   async def item_list(request: Request, status: list[str] = Query(default=["active"])):
       with Session(engine) as session:
           items = session.exec(select(Item).where(Item.status.in_(status))).all()
       return _templates(request).TemplateResponse("item_list.html", {
           "request": request, "items": items, "active_filters": status, ...
       })
   ```
2. Create `templates/item_list.html` extending `base.html`
3. Use the pattern: `s-title-02` (title) → `s-section` (filter bar + table)
4. Register the router in `app.py` with `app.include_router(router)`
5. Add a nav item in `base.html`'s offcanvas sidebar

### Add a new detail page with tabs

1. Create the route returning the object + related data
2. Create `templates/item_detail.html` extending `base.html`
3. Structure: `s-title-02` (prevstep + title + action bar + tab nav) → `s-section` (tab content)
4. Create `templates/includes/` partials for each tab's content
5. First tab gets `show active`, use `order-*` classes for main/sidebar column layout

### Add a new tab to an existing detail page

1. Add a `<li class="nav-item">` to the tab nav in the detail template
2. Add a `<div class="tab-pane fade">` to the tab content
3. Create `templates/includes/new_section.html`
4. Pass any new data from the route

### Add a new info card

Create a partial in `templates/includes/`:

```html
<div class="c-box mb-3 mb-md-4">
    <h3>Section Title</h3>
    <ul class="list-data mb-3">
        <li>
            <small>Field</small>
            <strong>{{ o.field }}</strong>
        </li>
    </ul>
</div>
```

Include it in the appropriate tab pane with `{% include "includes/your_card.html" %}`.

### Add a new SQLModel model

1. Define the model in `models.py` with `table=True`
2. Tables are auto-created by `init_db()` (calls `SQLModel.metadata.create_all(engine)`)
3. Add seed data in `seed.py` if needed
4. Query with `Session(engine)` + `select()` in routes

### Add a new status or event type

1. Add the status key to `ALL_STATUSES` in `config.py`
2. Add label + CSS class to `STATUS_LABELS` (for statuses) or `EVENT_LABELS` (for events)
3. Templates pick up the new values automatically via globals

## Pitfalls and lessons learned

1. **`python-multipart` is not optional** — FastAPI silently fails on form POSTs without it (500, no clear error)
2. **Respect the BEM nesting** — `s-section` needs `s-section__container`, `s-section__row`, `s-section__col`. Skip a level and margins collapse or padding disappears
3. **`l-authenticated` on `<body>`** — without this class, the sidebar layout doesn't activate on large screens
4. **Remix Icons are in app.css** — don't look for a separate `remixicon.css`, it's compiled into the theme stylesheet
5. **itou.css is essential** — without it, `list-data`, `list-note`, `list-step`, `c-box` variants, and many other patterns render incorrectly. It's the glue between theme-inclusion and les-emplois-specific markup
6. **Use formal names in French UI** — always "Mme Martin", "M. Benali", never first names
7. **Logo choice** — use `logo-plateforme-inclusion.svg` for a generic Plateforme de l'inclusion prototype, not `logo-emploi-inclusion.svg` (which is les-emplois specific)
8. **DATABASE_URL prefix** — SQLAlchemy/SQLModel with psycopg3 requires `postgresql+psycopg://`, not `postgresql://`
9. **JSON fields** — store as TEXT in PostgreSQL, parse with `json.loads()` in routes before passing to templates. Don't try to access nested JSON properties directly on SQLModel objects in templates.
10. **Template globals vs route context** — shared labels/config go in `templates.env.globals` (set once in app.py). Page-specific data (the orientation, messages, etc.) goes in the route's template context.
