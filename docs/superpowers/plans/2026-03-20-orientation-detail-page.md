# Orientation Detail Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a functional prototype of the les-emplois "candidature detail" page, repurposed for orientation referrals, with FastAPI + Jinja2 + SQLite.

**Architecture:** FastAPI serves Jinja2 templates styled with theme-inclusion CSS/Bootstrap 5 copied from les-emplois. SQLite stores orientations, messages, and history events. No auth — the receiving service and orienteur are simulated via separate URLs.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, Jinja2, SQLite (stdlib sqlite3), theme-inclusion CSS, Bootstrap 5, Remix Icons

**Spec:** `docs/superpowers/specs/2026-03-20-orientation-detail-page-design.md`

---

## File Structure

```
fluo-proto/
├── app.py                          # FastAPI app: routes, Jinja2 setup, static mount
├── db.py                           # SQLite init, schema, query helpers
├── seed.py                         # Populate DB with mock orientation data
├── requirements.txt                # fastapi, uvicorn, jinja2
├── templates/
│   ├── base.html                   # Base layout: HTML head, CSS/JS includes, simplified header
│   ├── orientation_detail.html     # Main detail page (receiving service view, 3 tabs)
│   ├── orienteur_reply.html        # Simple reply page for orienteur
│   └── includes/
│       ├── personal_info.html      # Section 1: person info card
│       ├── sender_info.html        # Section 2: who is referring
│       ├── modalite.html           # Section 3: type of orientation
│       ├── diagnostic.html         # Section 4: FT diagnostic summary
│       ├── messages_sidebar.html   # Sidebar: quick message form + recent messages
│       ├── messages_tab.html       # Tab 2: full message form + list
│       └── history.html            # Tab 3: status change timeline
├── static/
│   ├── css/
│   │   └── itou.css                # Copied from les-emplois
│   └── vendor/
│       ├── theme-inclusion/        # Copied from les-emplois (CSS, fonts, images)
│       └── bootstrap/              # Copied from les-emplois (JS only)
└── data.db                         # Auto-created by db.py
```

**Why `db.py` instead of `models.py`:** This is plain sqlite3 with raw SQL — no ORM. `db.py` is more accurate for what it does (init schema + query functions).

---

### Task 1: Project setup and static assets

**Files:**
- Create: `requirements.txt`
- Create: `static/` (copy from les-emplois)

- [ ] **Step 1: Create requirements.txt**

```
fastapi
uvicorn
jinja2
```

Write to `fluo-proto/requirements.txt`.

- [ ] **Step 2: Create virtualenv and install deps**

Run:
```bash
cd /Users/louije/Development/gip/fluo-proto
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Add `.venv/` to `.gitignore` (which already has `.superpowers/`, `data.db`, `__pycache__/`).

- [ ] **Step 3: Copy static assets from les-emplois**

```bash
# Theme-inclusion (CSS, fonts, images)
mkdir -p static/vendor
cp -r /Users/louije/Development/gip/les-emplois/itou/static/vendor/theme-inclusion static/vendor/

# Bootstrap JS
cp -r /Users/louije/Development/gip/les-emplois/itou/static/vendor/bootstrap static/vendor/

# jQuery (needed by Bootstrap)
cp -r /Users/louije/Development/gip/les-emplois/itou/static/vendor/jquery static/vendor/

# Itou custom CSS
mkdir -p static/css
cp /Users/louije/Development/gip/les-emplois/itou/static/css/itou.css static/css/
```

Add `static/vendor/` and `static/css/itou.css` to `.gitignore` (they're copied, not source).

- [ ] **Step 4: Commit**

```bash
git add requirements.txt .gitignore
git commit -m "Add requirements and gitignore for vendor assets"
```

---

### Task 2: Database layer

**Files:**
- Create: `db.py`

- [ ] **Step 1: Write db.py with schema init and query helpers**

```python
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS orientation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL DEFAULT 'nouvelle',
            created_at TEXT NOT NULL,
            person_first_name TEXT NOT NULL,
            person_last_name TEXT NOT NULL,
            person_phone TEXT,
            person_email TEXT,
            person_birthdate TEXT,
            person_address TEXT,
            sender_name TEXT NOT NULL,
            sender_type TEXT NOT NULL,
            sender_organization TEXT,
            sender_email TEXT,
            sender_message TEXT,
            modalite TEXT,
            diagnostic_data TEXT
        );

        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orientation_id INTEGER NOT NULL REFERENCES orientation(id),
            author_name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS history_event (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orientation_id INTEGER NOT NULL REFERENCES orientation(id),
            event_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def get_orientation(orientation_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM orientation WHERE id = ?", (orientation_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    result = dict(row)
    if result["diagnostic_data"]:
        result["diagnostic_data"] = json.loads(result["diagnostic_data"])
    return result


def update_orientation_status(orientation_id: int, new_status: str):
    now = datetime.now().isoformat()
    conn = get_db()
    conn.execute(
        "UPDATE orientation SET status = ? WHERE id = ?",
        (new_status, orientation_id),
    )
    event_type = {"acceptee": "accepted", "refusee": "refused"}[new_status]
    conn.execute(
        "INSERT INTO history_event (orientation_id, event_type, created_at) VALUES (?, ?, ?)",
        (orientation_id, event_type, now),
    )
    conn.commit()
    conn.close()


def get_messages(orientation_id: int) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM message WHERE orientation_id = ? ORDER BY created_at DESC",
        (orientation_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_message(orientation_id: int, author_name: str, content: str):
    now = datetime.now().isoformat()
    conn = get_db()
    conn.execute(
        "INSERT INTO message (orientation_id, author_name, content, created_at) VALUES (?, ?, ?, ?)",
        (orientation_id, author_name, content, now),
    )
    conn.commit()
    conn.close()


def get_history(orientation_id: int) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM history_event WHERE orientation_id = ? ORDER BY created_at ASC",
        (orientation_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

- [ ] **Step 2: Verify it runs without error**

Run:
```bash
cd /Users/louije/Development/gip/fluo-proto
.venv/bin/python -c "from db import init_db; init_db(); print('OK')"
```
Expected: `OK` and a `data.db` file created.

- [ ] **Step 3: Commit**

```bash
git add db.py
git commit -m "Add SQLite database layer"
```

---

### Task 3: Seed data

**Files:**
- Create: `seed.py`

- [ ] **Step 1: Write seed.py**

```python
import json
from datetime import datetime

from db import get_db, init_db

DIAGNOSTIC_DATA = {
    "projet_professionnel": {
        "nom_metier": "Assistante de vie aux familles",
        "code_rome": "K1302",
        "statut": "EN_COURS",
        "est_prioritaire": True,
    },
    "contraintes": [
        {
            "libelle": "Développer sa mobilité",
            "valeur": "OUI",
            "impact": "FORT",
            "est_prioritaire": True,
            "situations": [
                {"libelle": "Aucun moyen de transport à disposition", "valeur": "OUI"},
                {"libelle": "Dépendant des transports en commun", "valeur": "NON"},
            ],
            "objectifs": [
                {"libelle": "Obtenir le permis de conduire", "valeur": "EN_COURS"},
            ],
        },
        {
            "libelle": "Surmonter ses contraintes familiales",
            "valeur": "OUI",
            "impact": "MOYEN",
            "est_prioritaire": False,
            "situations": [
                {"libelle": "Enfant(s) de moins de 3 ans sans solution de garde", "valeur": "OUI"},
                {"libelle": "Contraintes horaires", "valeur": "OUI"},
            ],
            "objectifs": [
                {"libelle": "Trouver des solutions de garde d'enfant", "valeur": "EN_COURS"},
            ],
        },
    ],
    "pouvoir_agir": {
        "confiance": "NON",
        "accompagnement": "OUI",
        "resultat_analyse": "Besoin d'appui pour consolider sa confiance à mener ses démarches",
    },
    "autonomie_numerique": {
        "impact": "FAIBLE",
        "situations": [
            {"libelle": "Dispose d'un smartphone", "valeur": "OUI"},
            {"libelle": "Dispose d'un ordinateur", "valeur": "NON"},
            {"libelle": "Difficulté à réaliser des démarches administratives en ligne", "valeur": "OUI"},
        ],
        "objectifs": [
            {"libelle": "Maîtriser les fondamentaux du numérique", "valeur": "EN_COURS"},
        ],
    },
    "agent": {
        "nom": "Lefèvre",
        "prenom": "Jean-Marc",
        "structure": "FT Agence Cahors",
    },
    "date_mise_a_jour": "2025-03-12",
}


def seed():
    init_db()
    conn = get_db()

    # Check if already seeded
    count = conn.execute("SELECT COUNT(*) FROM orientation").fetchone()[0]
    if count > 0:
        print("Database already seeded.")
        conn.close()
        return

    now = datetime(2025, 3, 12, 10, 30).isoformat()

    conn.execute(
        """INSERT INTO orientation (
            status, created_at,
            person_first_name, person_last_name, person_phone, person_email,
            person_birthdate, person_address,
            sender_name, sender_type, sender_organization, sender_email, sender_message,
            modalite, diagnostic_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "nouvelle",
            now,
            "Sophie",
            "MARTIN",
            "06 12 34 56 78",
            "sophie.martin@email.fr",
            "1990-06-15",
            "Cahors, 46000",
            "Jean-Marc LEFÈVRE",
            "prescripteur",
            "FT Agence Cahors",
            "jean-marc.lefevre@francetravail.fr",
            "Sophie souhaite se reconvertir comme assistante de vie. "
            "Elle a besoin d'un accompagnement pour lever ses freins "
            "de mobilité et de garde d'enfant.",
            "accompagnement_emploi",
            json.dumps(DIAGNOSTIC_DATA, ensure_ascii=False),
        ),
    )

    conn.execute(
        "INSERT INTO history_event (orientation_id, event_type, created_at) VALUES (?, ?, ?)",
        (1, "created", now),
    )

    conn.commit()
    conn.close()
    print("Seeded 1 orientation.")


if __name__ == "__main__":
    seed()
```

- [ ] **Step 2: Run seed**

Run:
```bash
cd /Users/louije/Development/gip/fluo-proto
rm -f data.db
.venv/bin/python seed.py
```
Expected: `Seeded 1 orientation.`

- [ ] **Step 3: Verify data**

Run:
```bash
.venv/bin/python -c "
from db import get_orientation, get_history
o = get_orientation(1)
print(o['person_first_name'], o['person_last_name'], '—', o['status'])
print('Diagnostic keys:', list(o['diagnostic_data'].keys()))
h = get_history(1)
print('History events:', len(h))
"
```
Expected:
```
Sophie MARTIN — nouvelle
Diagnostic keys: ['projet_professionnel', 'contraintes', 'pouvoir_agir', 'autonomie_numerique', 'agent', 'date_mise_a_jour']
History events: 1
```

- [ ] **Step 4: Commit**

```bash
git add seed.py
git commit -m "Add seed data for mock orientation"
```

---

### Task 4: FastAPI app shell with base template

**Files:**
- Create: `app.py`
- Create: `templates/base.html`

- [ ] **Step 1: Write app.py with minimal route**

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import init_db

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()


@app.get("/orientation/{orientation_id}", response_class=HTMLResponse)
async def orientation_detail(request: Request, orientation_id: int):
    return templates.TemplateResponse(
        "orientation_detail.html",
        {"request": request, "orientation_id": orientation_id},
    )
```

- [ ] **Step 2: Write base.html**

This is the simplified base layout. It loads theme-inclusion CSS, Bootstrap JS, jQuery, Remix Icons — same stack as les-emplois but without Django-specific bits.

Reference les-emplois patterns: `<body class="l-authenticated">`, `<main id="main" class="s-main">`, the `s-title-02` section structure.

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>{% block title %}Fluo{% endblock %} - Fluo Proto</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="/static/vendor/theme-inclusion/images/favicon.ico" type="image/ico">
    <link rel="stylesheet" href="/static/vendor/theme-inclusion/stylesheets/app.css">
    <link rel="stylesheet" href="/static/css/itou.css">
</head>
<body class="l-authenticated">
    <header role="banner" id="header">
        <section class="s-header-authenticated">
            <div class="s-header-authenticated__container container">
                <div class="s-header-authenticated__row row">
                    <div class="s-header-authenticated__col s-header-authenticated__col--logo-service col-auto d-flex align-items-center pe-0">
                        <a href="/">
                            <img src="/static/vendor/theme-inclusion/images/logo-emploi-inclusion.svg"
                                 alt="Fluo Proto" height="90">
                        </a>
                    </div>
                </div>
            </div>
        </section>
    </header>

    <main id="main" role="main" class="s-main">
        {% block content %}{% endblock %}
    </main>

    <script src="/static/vendor/jquery/jquery.min.js"></script>
    <script src="/static/vendor/bootstrap/popper.min.js"></script>
    <script src="/static/vendor/bootstrap/bootstrap.min.js"></script>
</body>
</html>
```

- [ ] **Step 3: Write a stub orientation_detail.html**

```html
{% extends "base.html" %}
{% block title %}Orientation{% endblock %}
{% block content %}
<section class="s-title-02">
    <div class="s-title-02__container container">
        <div class="s-title-02__row row">
            <div class="s-title-02__col col-12">
                <h1>Placeholder — orientation {{ orientation_id }}</h1>
            </div>
        </div>
    </div>
</section>
{% endblock %}
```

- [ ] **Step 4: Seed the DB and start the server**

Run:
```bash
cd /Users/louije/Development/gip/fluo-proto
rm -f data.db && .venv/bin/python seed.py
.venv/bin/uvicorn app:app --reload --port 8000
```

Open http://localhost:8000/orientation/1 — verify the page renders with the theme-inclusion header and "Placeholder" text.

- [ ] **Step 5: Commit**

```bash
git add app.py templates/base.html templates/orientation_detail.html
git commit -m "Add FastAPI app shell with base template"
```

---

### Task 5: Title bar, status badge, and action bar

**Files:**
- Modify: `app.py` (pass orientation data to template)
- Modify: `templates/orientation_detail.html`

- [ ] **Step 1: Update app.py to load orientation data**

Replace the `orientation_detail` route:

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import add_message, get_history, get_messages, get_orientation, init_db, update_orientation_status

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()

STATUS_LABELS = {
    "nouvelle": ("Nouvelle demande", "bg-info"),
    "acceptee": ("Acceptée", "bg-success"),
    "refusee": ("Refusée", "bg-danger"),
}

EVENT_LABELS = {
    "created": "Nouvelle demande",
    "accepted": "Demande acceptée",
    "refused": "Demande refusée",
}

MODALITE_LABELS = {
    "accompagnement_emploi": "Accompagnement vers l'emploi",
}

SERVICE_NAME = "PLIE Lille Avenir"


@app.get("/orientation/{orientation_id}", response_class=HTMLResponse)
async def orientation_detail(request: Request, orientation_id: int):
    orientation = get_orientation(orientation_id)
    if not orientation:
        return HTMLResponse("Not found", status_code=404)
    messages = get_messages(orientation_id)
    history = get_history(orientation_id)
    status_label, status_class = STATUS_LABELS.get(
        orientation["status"], ("Inconnu", "bg-secondary")
    )
    return templates.TemplateResponse(
        "orientation_detail.html",
        {
            "request": request,
            "o": orientation,
            "messages": messages,
            "history": history,
            "status_label": status_label,
            "status_class": status_class,
            "event_labels": EVENT_LABELS,
            "modalite_label": MODALITE_LABELS.get(orientation["modalite"], orientation["modalite"]),
            "service_name": SERVICE_NAME,
        },
    )


@app.post("/orientation/{orientation_id}/accept")
async def accept_orientation(orientation_id: int):
    update_orientation_status(orientation_id, "acceptee")
    return RedirectResponse(f"/orientation/{orientation_id}", status_code=303)


@app.post("/orientation/{orientation_id}/refuse")
async def refuse_orientation(orientation_id: int):
    update_orientation_status(orientation_id, "refusee")
    return RedirectResponse(f"/orientation/{orientation_id}", status_code=303)


@app.post("/orientation/{orientation_id}/message")
async def post_message(request: Request, orientation_id: int):
    form = await request.form()
    content = form.get("content", "").strip()
    author = form.get("author_name", SERVICE_NAME)
    redirect_to = form.get("redirect_to", f"/orientation/{orientation_id}")
    if content:
        add_message(orientation_id, author, content)
    return RedirectResponse(redirect_to, status_code=303)


@app.get("/orientation/{orientation_id}/orienteur", response_class=HTMLResponse)
async def orienteur_reply(request: Request, orientation_id: int):
    orientation = get_orientation(orientation_id)
    if not orientation:
        return HTMLResponse("Not found", status_code=404)
    messages = get_messages(orientation_id)
    status_label, status_class = STATUS_LABELS.get(
        orientation["status"], ("Inconnu", "bg-secondary")
    )
    return templates.TemplateResponse(
        "orienteur_reply.html",
        {
            "request": request,
            "o": orientation,
            "messages": messages,
            "status_label": status_label,
            "status_class": status_class,
        },
    )
```

- [ ] **Step 2: Write the full orientation_detail.html with title bar, action bar, and tab structure**

```html
{% extends "base.html" %}

{% block title %}Demande d'orientation — {{ o.person_last_name }} {{ o.person_first_name }}{% endblock %}

{% block content %}
<section class="s-title-02">
    <div class="s-title-02__container container">
        <div class="s-title-02__row row">
            <div class="s-title-02__col col-12">

                {# Back link #}
                <div class="c-prevstep">
                    <a href="#" class="btn btn-ico btn-link ps-0">
                        <i class="ri-arrow-drop-left-line ri-xl fw-medium" aria-hidden="true"></i>
                        <span>Retour à la liste</span>
                    </a>
                </div>

                {# Title + badge #}
                <div class="c-title">
                    <div class="c-title__main">
                        <h1>
                            Demande d'orientation —
                            {{ o.person_last_name }} {{ o.person_first_name }}
                            <span class="badge rounded-pill text-nowrap badge-base {{ status_class }}">
                                {{ status_label }}
                            </span>
                        </h1>
                    </div>
                </div>

                {# Action bar #}
                <div class="c-box c-box--action">
                    <h2 class="visually-hidden">Actions rapides</h2>
                    {% if o.status == "nouvelle" %}
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
                    {% else %}
                    <div class="d-flex align-items-center gap-3 px-3 py-2">
                        <span class="badge rounded-pill {{ status_class }} text-white">
                            {{ status_label }}
                        </span>
                    </div>
                    {% endif %}
                </div>

                {# Tabs #}
                <ul class="s-tabs-01__nav nav nav-tabs mb-0" role="tablist">
                    <li class="nav-item" role="presentation">
                        <a class="nav-link active" id="informations-tab"
                           data-bs-toggle="tab" href="#informations"
                           role="tab" aria-controls="informations" aria-selected="true">
                            Informations générales
                        </a>
                    </li>
                    <li class="nav-item" role="presentation">
                        <a class="nav-link" id="messages-tab"
                           data-bs-toggle="tab" href="#messages"
                           role="tab" aria-controls="messages" aria-selected="false">
                            Messages{% if messages %} ({{ messages|length }}){% endif %}
                        </a>
                    </li>
                    <li class="nav-item" role="presentation">
                        <a class="nav-link" id="historique-tab"
                           data-bs-toggle="tab" href="#historique"
                           role="tab" aria-controls="historique" aria-selected="false">
                            Historique
                        </a>
                    </li>
                </ul>

            </div>
        </div>
    </div>
</section>

<section class="s-section">
    <div class="s-section__container container">
        <div class="tab-content">

            {# Tab 1: Informations générales #}
            <div class="tab-pane fade show active" id="informations"
                 role="tabpanel" aria-labelledby="informations-tab">
                <div class="s-section__row row">
                    <div class="s-section__col col-12 col-xxl-8 col-xxxl-9 order-2 order-xxl-1">
                        <h2 class="mb-3 mb-md-4">Informations générales</h2>
                        {% include "includes/personal_info.html" %}
                        {% include "includes/sender_info.html" %}
                        {% include "includes/modalite.html" %}
                        {% include "includes/diagnostic.html" %}
                    </div>
                    <div class="s-section__col col-12 col-xxl-4 col-xxxl-3 order-1 order-xxl-2">
                        {% include "includes/messages_sidebar.html" %}
                    </div>
                </div>
            </div>

            {# Tab 2: Messages #}
            <div class="tab-pane fade" id="messages"
                 role="tabpanel" aria-labelledby="messages-tab">
                <div class="s-section__row row">
                    <div class="col-12 col-xxl-8 col-xxxl-9">
                        {% include "includes/messages_tab.html" %}
                    </div>
                </div>
            </div>

            {# Tab 3: Historique #}
            <div class="tab-pane fade" id="historique"
                 role="tabpanel" aria-labelledby="historique-tab">
                <div class="s-section__row row">
                    <div class="s-section__col col-12 col-xxl-8 col-xxxl-9">
                        {% include "includes/history.html" %}
                    </div>
                </div>
            </div>

        </div>
    </div>
</section>
{% endblock %}
```

- [ ] **Step 3: Create stub includes so the page doesn't crash**

Create each of these files with a placeholder `<div class="c-box mb-3 mb-md-4"><h3>Section name</h3><p>TODO</p></div>`:

- `templates/includes/personal_info.html`
- `templates/includes/sender_info.html`
- `templates/includes/modalite.html`
- `templates/includes/diagnostic.html`
- `templates/includes/messages_sidebar.html`
- `templates/includes/messages_tab.html`
- `templates/includes/history.html`

- [ ] **Step 4: Start the server and verify**

Run:
```bash
cd /Users/louije/Development/gip/fluo-proto
rm -f data.db && .venv/bin/python seed.py
.venv/bin/uvicorn app:app --reload --port 8000
```

Open http://localhost:8000/orientation/1 — verify:
- Title: "Demande d'orientation — MARTIN Sophie"
- Blue "Nouvelle demande" badge
- Blue action bar with Accepter / Refuser buttons
- 3 tabs, first one active
- Stub content renders

- [ ] **Step 5: Commit**

```bash
git add app.py templates/
git commit -m "Add orientation detail page with title bar, actions, and tabs"
```

---

### Task 6: Personal info include

**Files:**
- Modify: `templates/includes/personal_info.html`

- [ ] **Step 1: Write the personal info card**

Uses the les-emplois `list-data` pattern with `<small>` label + `<strong>` value.

```html
<div class="c-box mb-3 mb-md-4">
    <div class="row mb-3">
        <div class="col-12 col-sm">
            <h3 class="mb-0">Informations personnelles</h3>
        </div>
        <div class="col-12 col-sm-auto mt-2 mt-sm-0 d-flex align-items-center">
            <span class="btn btn-ico btn-outline-primary disabled">
                <i class="ri-pencil-line fw-medium" aria-hidden="true"></i>
                <span>Modifier</span>
            </span>
        </div>
    </div>
    <ul class="list-data mb-3">
        <li>
            <small>Prénom</small>
            <strong>{{ o.person_first_name }}</strong>
        </li>
        <li>
            <small>Nom</small>
            <strong>{{ o.person_last_name }}</strong>
        </li>
        <li>
            <small>Téléphone</small>
            {% if o.person_phone %}
                <strong>{{ o.person_phone }}</strong>
            {% else %}
                <i class="text-disabled">Non renseigné</i>
            {% endif %}
        </li>
        <li>
            <small>Adresse e-mail</small>
            {% if o.person_email %}
                <strong>{{ o.person_email }}</strong>
            {% else %}
                <i class="text-disabled">Non renseigné</i>
            {% endif %}
        </li>
        <li>
            <small>Date de naissance</small>
            {% if o.person_birthdate %}
                <strong>{{ o.person_birthdate }}</strong>
            {% else %}
                <i class="text-disabled">Non renseigné</i>
            {% endif %}
        </li>
        <li>
            <small>Adresse</small>
            {% if o.person_address %}
                <address>{{ o.person_address }}</address>
            {% else %}
                <i class="text-disabled">Non renseigné</i>
            {% endif %}
        </li>
    </ul>
</div>
```

- [ ] **Step 2: Verify in browser**

Reload http://localhost:8000/orientation/1 — the personal info card should show Sophie MARTIN's data in the les-emplois style.

- [ ] **Step 3: Commit**

```bash
git add templates/includes/personal_info.html
git commit -m "Add personal info card"
```

---

### Task 7: Sender info include

**Files:**
- Modify: `templates/includes/sender_info.html`

- [ ] **Step 1: Write the sender info card**

```html
<div class="c-box mb-3 mb-md-4">
    <h3>Qui oriente cet usager ?</h3>
    <ul class="list-data mb-3">
        <li>
            <small>Émetteur</small>
            <strong>{{ o.sender_name }}</strong>
        </li>
        <li>
            <small>Type</small>
            <strong>{{ o.sender_type|capitalize }}</strong>
        </li>
        {% if o.sender_organization %}
        <li>
            <small>Organisation</small>
            <strong>{{ o.sender_organization }}</strong>
            {% if o.sender_type == "prescripteur" %}
                <span class="badge badge-xs rounded-pill bg-warning">Prescripteur habilité</span>
            {% endif %}
        </li>
        {% endif %}
        {% if o.sender_email %}
        <li>
            <small>Adresse e-mail</small>
            <strong>{{ o.sender_email }}</strong>
        </li>
        {% endif %}
        <li>
            <small>Date</small>
            <strong>Le {{ o.created_at[:10] }}</strong>
        </li>
    </ul>
    {% if o.sender_message %}
    <ul class="list-data mb-3">
        <li class="has-forced-line-break">
            <small>Message de la demande</small>
            <blockquote class="blockquote mt-2 mb-0">
                <p>{{ o.sender_message }}</p>
            </blockquote>
        </li>
    </ul>
    {% endif %}
</div>
```

- [ ] **Step 2: Verify in browser, commit**

```bash
git add templates/includes/sender_info.html
git commit -m "Add sender info card"
```

---

### Task 8: Modalité include

**Files:**
- Modify: `templates/includes/modalite.html`

- [ ] **Step 1: Write the modalite card**

```html
<div class="c-box mb-3 mb-md-4">
    <h3>Modalité d'orientation sollicitée</h3>
    <ul class="list-data mb-3">
        <li>
            <small>Type d'accompagnement</small>
            <strong>{{ modalite_label }}</strong>
        </li>
    </ul>
</div>
```

- [ ] **Step 2: Verify in browser, commit**

```bash
git add templates/includes/modalite.html
git commit -m "Add modalite card"
```

---

### Task 9: Diagnostic include

**Files:**
- Modify: `templates/includes/diagnostic.html`

- [ ] **Step 1: Write the diagnostic card**

This displays the France Travail diagnostic summary with colored left-border sub-cards. The diagnostic data is in `o.diagnostic_data` (already parsed from JSON by `db.py`).

```html
<div class="c-box mb-3 mb-md-4">
    <h3>Diagnostic</h3>
    <p class="fs-sm text-muted mb-3">
        Diagnostic socio-professionnel issu du dossier France Travail
    </p>

    {% set d = o.diagnostic_data %}

    {# Projet professionnel #}
    {% if d.projet_professionnel %}
    {% set pp = d.projet_professionnel %}
    <div class="mb-3 ps-3" style="border-left: 3px solid #0a6ebd;">
        <div class="fw-bold fs-sm mb-1">Projet professionnel</div>
        <div class="fs-sm">
            {{ pp.nom_metier }} ({{ pp.code_rome }})
            {% if pp.est_prioritaire %}
                <span class="badge badge-xs rounded-pill bg-info ms-1">Prioritaire</span>
            {% endif %}
        </div>
    </div>
    {% endif %}

    {# Contraintes personnelles #}
    {% if d.contraintes %}
    <div class="mb-3 ps-3" style="border-left: 3px solid #f59e0b;">
        <div class="fw-bold fs-sm mb-1">Contraintes personnelles</div>
        {% for c in d.contraintes %}
        <div class="fs-sm{% if not loop.last %} mb-2{% endif %}">
            <strong>{{ c.libelle }}</strong>
            — Impact {{ c.impact|lower }}
            {% if c.est_prioritaire %}, prioritaire{% endif %}
            {% if c.situations %}
            <div class="text-muted ms-3">
                {% for s in c.situations %}
                    {% if s.valeur == "OUI" %}• {{ s.libelle }}<br>{% endif %}
                {% endfor %}
            </div>
            {% endif %}
            {% if c.objectifs %}
            <div class="ms-3">
                {% for obj in c.objectifs %}
                    <span class="fs-xs">→ {{ obj.libelle }}
                    {% if obj.valeur == "EN_COURS" %}
                        <span class="badge badge-xs rounded-pill bg-info-lighter text-info">En cours</span>
                    {% elif obj.valeur == "REALISE" %}
                        <span class="badge badge-xs rounded-pill bg-success-lighter text-success">Réalisé</span>
                    {% endif %}
                    </span><br>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {# Pouvoir agir #}
    {% if d.pouvoir_agir %}
    {% set pa = d.pouvoir_agir %}
    <div class="mb-3 ps-3" style="border-left: 3px solid #8b5cf6;">
        <div class="fw-bold fs-sm mb-1">Confiance et capacité à agir</div>
        <div class="fs-sm">
            {% if pa.resultat_analyse %}
                {{ pa.resultat_analyse }}
            {% else %}
                Confiance : {{ pa.confiance }} — Accompagnement : {{ pa.accompagnement }}
            {% endif %}
        </div>
    </div>
    {% endif %}

    {# Autonomie numérique #}
    {% if d.autonomie_numerique %}
    {% set an = d.autonomie_numerique %}
    <div class="mb-3 ps-3" style="border-left: 3px solid #06b6d4;">
        <div class="fw-bold fs-sm mb-1">Maîtrise du numérique</div>
        <div class="fs-sm">
            Impact {{ an.impact|lower }}
            {% if an.situations %}
            <div class="text-muted ms-3">
                {% for s in an.situations %}
                    • {{ s.libelle }} : {{ "Oui" if s.valeur == "OUI" else "Non" }}<br>
                {% endfor %}
            </div>
            {% endif %}
            {% if an.objectifs %}
            <div class="ms-3">
                {% for obj in an.objectifs %}
                    <span class="fs-xs">→ {{ obj.libelle }}
                    {% if obj.valeur == "EN_COURS" %}
                        <span class="badge badge-xs rounded-pill bg-info-lighter text-info">En cours</span>
                    {% endif %}
                    </span><br>
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    {% endif %}

    {# Agent + date #}
    {% if d.agent %}
    <div class="fs-xs text-muted mt-2">
        Dernière mise à jour : {{ d.date_mise_a_jour }}
        par {{ d.agent.prenom }} {{ d.agent.nom }}
        {% if d.agent.structure %} — {{ d.agent.structure }}{% endif %}
    </div>
    {% endif %}
</div>
```

- [ ] **Step 2: Verify in browser, commit**

Reload — the diagnostic card should show project, constraints, confidence, and digital sections.

```bash
git add templates/includes/diagnostic.html
git commit -m "Add diagnostic summary card"
```

---

### Task 10: Messages sidebar include

**Files:**
- Modify: `templates/includes/messages_sidebar.html`

- [ ] **Step 1: Write the sidebar messages form + recent list**

```html
{# Quick message form #}
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

{# Recent messages #}
{% if messages %}
<div class="c-box mb-3 mb-md-4">
    <h3>Derniers messages</h3>
    <ul class="list-note">
        {% for msg in messages[:3] %}
        <li>
            <div>
                <time class="fs-xs text-muted">{{ msg.created_at[:16]|replace("T", " à ") }}</time>
                <strong class="d-block">{{ msg.author_name }}</strong>
                <blockquote class="blockquote mt-1 mb-0">
                    <p>{{ msg.content }}</p>
                </blockquote>
            </div>
        </li>
        {% endfor %}
    </ul>
    {% if messages|length > 3 %}
    <button class="btn btn-outline-primary btn-block bg-white mt-3"
            onclick="document.querySelector('#messages-tab').click()">
        Voir tous les messages
    </button>
    {% endif %}
</div>
{% endif %}
```

- [ ] **Step 2: Verify in browser, commit**

```bash
git add templates/includes/messages_sidebar.html
git commit -m "Add sidebar messages form and recent list"
```

---

### Task 11: Messages tab include

**Files:**
- Modify: `templates/includes/messages_tab.html`

- [ ] **Step 1: Write the messages tab**

```html
<h2>Messages</h2>

{# Message form #}
<div class="c-form mb-3 mb-md-4">
    <form method="post" action="/orientation/{{ o.id }}/message">
        <input type="hidden" name="author_name" value="{{ service_name }}">
        <input type="hidden" name="redirect_to" value="/orientation/{{ o.id }}#messages">
        <div class="form-group">
            <label class="form-label" for="tab-message">Envoyer un message</label>
            <textarea name="content" id="tab-message" rows="4"
                      class="form-control" required></textarea>
            <div class="form-text">
                Les messages sont visibles par tous les intervenants de cette orientation.
            </div>
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

{# Messages list #}
<div class="c-form mb-3 mb-md-4">
    <h3>Liste des messages ({{ messages|length }})</h3>
    <ul class="list-note">
        {% for msg in messages %}
        <li{% if msg.author_name == service_name %} class="is-current-user"{% endif %}>
            <div>
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <time class="fs-xs text-muted">
                            {{ msg.created_at[:16]|replace("T", " à ") }}
                        </time>
                        <strong class="d-block">
                            {{ msg.author_name }}
                            {% if msg.author_name == service_name %} (vous){% endif %}
                        </strong>
                    </div>
                </div>
                <blockquote class="blockquote mt-1 mb-0">
                    <p>{{ msg.content }}</p>
                </blockquote>
            </div>
        </li>
        {% else %}
        <li>
            <div class="text-muted fs-sm">Aucun message</div>
        </li>
        {% endfor %}
    </ul>
</div>
```

- [ ] **Step 2: Verify in browser — click Messages tab, commit**

```bash
git add templates/includes/messages_tab.html
git commit -m "Add messages tab"
```

---

### Task 12: History tab include

**Files:**
- Modify: `templates/includes/history.html`

- [ ] **Step 1: Write the history tab**

```html
<h2>Historique des modifications</h2>

<ul class="list-step">
    {% for event in history %}
    <li>
        <time datetime="{{ event.created_at }}">
            Le {{ event.created_at[:10] }} à {{ event.created_at[11:16] }}
        </time>
        <span>{{ event_labels.get(event.event_type, event.event_type) }}</span>
    </li>
    {% endfor %}
</ul>
```

- [ ] **Step 2: Verify in browser — click Historique tab, commit**

```bash
git add templates/includes/history.html
git commit -m "Add history tab"
```

---

### Task 13: Orienteur reply page

**Files:**
- Create: `templates/orienteur_reply.html`

- [ ] **Step 1: Write the orienteur reply page**

Minimal layout: title + status, message list, reply form. No tabs, no action bar.

```html
{% extends "base.html" %}

{% block title %}Répondre — {{ o.person_last_name }} {{ o.person_first_name }}{% endblock %}

{% block content %}
<section class="s-title-02">
    <div class="s-title-02__container container">
        <div class="s-title-02__row row">
            <div class="s-title-02__col col-12">
                <div class="c-title">
                    <div class="c-title__main">
                        <h1>
                            Demande d'orientation —
                            {{ o.person_last_name }} {{ o.person_first_name }}
                            <span class="badge rounded-pill text-nowrap badge-base {{ status_class }}">
                                {{ status_label }}
                            </span>
                        </h1>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="s-section">
    <div class="s-section__container container">
        <div class="s-section__row row">
            <div class="s-section__col col-12 col-xxl-8 col-xxxl-9">

                {# Reply form #}
                <div class="c-form mb-3 mb-md-4">
                    <form method="post" action="/orientation/{{ o.id }}/message">
                        <input type="hidden" name="author_name" value="{{ o.sender_name }}">
                        <input type="hidden" name="redirect_to"
                               value="/orientation/{{ o.id }}/orienteur">
                        <div class="form-group">
                            <label class="form-label" for="orienteur-message">
                                Répondre en tant que {{ o.sender_name }}
                            </label>
                            <textarea name="content" id="orienteur-message" rows="4"
                                      class="form-control" required></textarea>
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

                {# Messages list #}
                <div class="c-form mb-3 mb-md-4">
                    <h3>Messages ({{ messages|length }})</h3>
                    <ul class="list-note">
                        {% for msg in messages %}
                        <li{% if msg.author_name == o.sender_name %} class="is-current-user"{% endif %}>
                            <div>
                                <time class="fs-xs text-muted">
                                    {{ msg.created_at[:16]|replace("T", " à ") }}
                                </time>
                                <strong class="d-block">
                                    {{ msg.author_name }}
                                    {% if msg.author_name == o.sender_name %} (vous){% endif %}
                                </strong>
                                <blockquote class="blockquote mt-1 mb-0">
                                    <p>{{ msg.content }}</p>
                                </blockquote>
                            </div>
                        </li>
                        {% else %}
                        <li>
                            <div class="text-muted fs-sm">Aucun message</div>
                        </li>
                        {% endfor %}
                    </ul>
                </div>

            </div>
        </div>
    </div>
</section>
{% endblock %}
```

- [ ] **Step 2: Verify in browser**

Open http://localhost:8000/orientation/1/orienteur — should show the reply page with "Répondre en tant que Jean-Marc LEFÈVRE".

- [ ] **Step 3: End-to-end test**

1. Open http://localhost:8000/orientation/1 in one tab (service view)
2. Open http://localhost:8000/orientation/1/orienteur in another tab (orienteur view)
3. Send a message from the service view sidebar
4. Refresh the orienteur view — the message appears
5. Send a reply from the orienteur view
6. Refresh the service view — the reply appears in sidebar and Messages tab
7. Click "Accepter" on the service view — status changes to "Acceptée", action buttons disappear
8. Check the Historique tab — two entries: "Nouvelle demande" and "Demande acceptée"

- [ ] **Step 4: Commit**

```bash
git add templates/orienteur_reply.html
git commit -m "Add orienteur reply page"
```

---

### Task 14: Final cleanup and verification

- [ ] **Step 1: Verify all static assets load without 404s**

Open browser dev tools Network tab on http://localhost:8000/orientation/1 — check that app.css, itou.css, bootstrap.min.js, jquery.min.js, and Remix Icon fonts all load correctly (status 200).

If any file has a hashed filename (like `app.eb2ad9c7a8ad.css`) in les-emplois but the template references a plain name, find and use the correct filename. Or rename the copied file to strip the hash.

- [ ] **Step 2: Fix any broken static asset references**

The les-emplois static files have Django's `ManifestStaticFilesStorage` hashes in filenames (e.g. `app.eb2ad9c7a8ad.css`). Either:
- Rename the copied files to strip the hash, OR
- Update `base.html` to use the hashed filenames

Pick whichever is simpler. The CSS file internally references fonts/images with relative paths, so stripping hashes from CSS/JS filenames should work as long as the font/image paths inside the CSS also resolve correctly.

- [ ] **Step 3: Commit any fixes**

```bash
git add -A
git commit -m "Fix static asset references"
```
