# Orientation Detail Page — Design Spec

## Overview

A simplified, front-end-focused prototype that reproduces the "Candidature detail" page from les-emplois, repurposed for viewing and processing **demandes d'orientation** (referrals of a person to a service/structure).

The primary user is the **receiving service** — they view the orientation request, can accept or refuse it, and communicate with the referrer via messages.

## Tech Stack

- **Server:** FastAPI + Uvicorn
- **Templates:** Jinja2 (close to Django template syntax)
- **Persistence:** SQLite (via aiosqlite or plain sqlite3)
- **Frontend:** Static assets copied from les-emplois (theme-inclusion CSS, Bootstrap 5 JS, Remix Icons)
- **No JS build step.** Static files served directly.

## Page Structure

### Title Bar

- Back link: "← Retour à la liste"
- Title: "Demande d'orientation — {LAST_NAME} {First_name}"
- Status badge: displays a label derived from the DB `status` field:
  - `"nouvelle"` → "Nouvelle demande" (blue)
  - `"acceptee"` → "Acceptée" (green)
  - `"refusee"` → "Refusée" (red)

### Action Bar

Blue bar with:
- **Accepter** button (POST /orientation/{id}/accept)
- **Refuser** button (POST /orientation/{id}/refuse)
- "Autres actions" dropdown (placeholder, no functionality needed)

Actions change the status and add a history event. After accept/refuse, the page redirects back to the same detail page (GET /orientation/{id}). The action bar then reflects the new state: the Accepter/Refuser buttons are hidden and replaced with a static status indicator matching the new state. Only orientations with status "nouvelle" show the action buttons.

### Tabs

Three tabs using Bootstrap 5 tab API (same as les-emplois):

1. **Informations générales** (default active)
2. **Messages** (replaces "Commentaires" — serves as chat between referrer and receiving service)
3. **Historique** (log of status changes)

### Tab 1: Informations générales

Two-column layout (8/4 on xxl, full-width on mobile) matching les-emplois responsive grid.

**Main column — 4 sections:**

1. **Informations personnelles**
   - Prénom, Nom, Téléphone, Adresse e-mail, Date de naissance, Adresse
   - "Modifier" link (placeholder, no edit functionality needed)

2. **Qui oriente cet usager ?**
   - Émetteur (name), Type (prescripteur/orienteur), Organisation, Adresse e-mail, Date
   - Message de la demande (blockquote)

3. **Modalité d'orientation sollicitée**
   - Displays the type of orientation requested, e.g. "Accompagnement vers l'emploi"

4. **Diagnostic**
   - Read-only summary of the person's socio-professional diagnostic, structured after the France Travail Diagnostic Argumenté v4 API.
   - Sub-sections with colored left-border cards:
     - 🧭 **Projet professionnel** — target job, ROME code, priority, status
     - 🚧 **Contraintes personnelles** — identified barriers (mobility, family…) with impact level
     - 💪 **Confiance et capacité à agir** — confidence, need for support, analysis text
     - 💻 **Maîtrise du numérique** — digital access, equipment, skills
   - Last updated date and agent info at the bottom

**Sidebar:**
- Quick message form — standard HTML form POST to `/orientation/{id}/message`, redirects back to detail page. Author name is hardcoded to the current "service" user (no auth, just a constant like "PLIE Lille Avenir").
- Latest messages list (most recent 3)

### Tab 2: Messages

- Form to add a new message (author name hardcoded to "PLIE Lille Avenir", textarea for content)
- List of all messages, newest first
- Messages are visible to all parties (shared between referrer and receiving service)

### Tab 3: Historique

- Chronological list of status changes, oldest first (matching les-emplois)
- Each entry shows timestamp and a label derived from `event_type`:
  - `"created"` → "Nouvelle demande"
  - `"accepted"` → "Demande acceptée"
  - `"refused"` → "Demande refusée"

### Orienteur Reply Page

A simple standalone page at `/orientation/{id}/orienteur` that lets the orienteur (the person who made the referral) send messages back. This simulates a second user without requiring authentication.

- Minimal layout: same `base.html` but no action bar, no tabs
- Shows the orientation title and status badge at the top
- Shows the full message thread (all messages, newest first)
- A form at the top to post a new message (author name hardcoded to the orienteur's name from `sender_name`, e.g. "Jean-Marc Lefèvre")
- POST to the same `/orientation/{id}/message` endpoint, but with the orienteur's name as author
- Redirects back to `/orientation/{id}/orienteur` after posting

This page is intentionally bare — just enough to test the two-way messaging flow.

## Data Model

### Table: `orientation`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| status | TEXT | "nouvelle", "acceptee", "refusee" |
| created_at | DATETIME | When the orientation was created |
| person_first_name | TEXT | |
| person_last_name | TEXT | |
| person_phone | TEXT | |
| person_email | TEXT | |
| person_birthdate | DATE | |
| person_address | TEXT | |
| sender_name | TEXT | |
| sender_type | TEXT | "prescripteur" or "orienteur" |
| sender_organization | TEXT | |
| sender_email | TEXT | |
| sender_message | TEXT | |
| modalite | TEXT | e.g. "accompagnement_emploi" |
| diagnostic_data | TEXT (JSON) | Full diagnostic blob matching FT API shape |

### Table: `message`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| orientation_id | INTEGER FK | → orientation.id |
| author_name | TEXT | |
| content | TEXT | |
| created_at | DATETIME | |

### Table: `history_event`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| orientation_id | INTEGER FK | → orientation.id |
| event_type | TEXT | "created", "accepted", "refused" |
| created_at | DATETIME | |

## Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/orientation/{id}` | Render detail page (receiving service view) |
| POST | `/orientation/{id}/accept` | Accept → update status, add history event, redirect |
| POST | `/orientation/{id}/refuse` | Refuse → update status, add history event, redirect |
| GET | `/orientation/{id}/orienteur` | Orienteur reply page (simple message view) |
| POST | `/orientation/{id}/message` | Add message → redirect back (to referrer based on `author` param) |
| GET | `/static/{path}` | Serve static files |

## Static Assets

Copied from `les-emplois/itou/static/`:
- `vendor/theme-inclusion/stylesheets/app.css` — main design system CSS
- `vendor/theme-inclusion/fonts/` — Remix Icon font files
- `vendor/theme-inclusion/images/` — logos, favicon
- `vendor/bootstrap/bootstrap.min.js` + `popper.min.js` — Bootstrap 5 JS
- `css/itou.css` — application-specific overrides

## Project Structure

```
fluo-proto/
├── app.py                          # FastAPI app, all routes
├── db.py                           # SQLite init, schema, query helpers
├── seed.py                         # Populate with mock data
├── requirements.txt                # fastapi, uvicorn, jinja2, aiosqlite
├── templates/
│   ├── base.html                   # Base layout (simplified header)
│   ├── orientation_detail.html     # Main detail page (receiving service)
│   ├── orienteur_reply.html        # Simple reply page (orienteur)
│   └── includes/
│       ├── personal_info.html
│       ├── sender_info.html
│       ├── modalite.html
│       ├── diagnostic.html
│       ├── messages.html
│       └── history.html
├── static/
│   └── vendor/                     # Copied from les-emplois
│       ├── theme-inclusion/
│       └── bootstrap/
└── data.db                         # Auto-created SQLite DB
```

## Diagnostic JSON Shape

The `diagnostic_data` column stores a JSON object with this structure (simplified from the FT Diagnostic Argumenté v4 API):

```json
{
  "projet_professionnel": {
    "nom_metier": "Assistante de vie aux familles",
    "code_rome": "K1302",
    "statut": "EN_COURS",
    "est_prioritaire": true
  },
  "contraintes": [
    {
      "libelle": "Développer sa mobilité",
      "valeur": "OUI",
      "impact": "FORT",
      "est_prioritaire": true,
      "situations": [
        {"libelle": "Aucun moyen de transport à disposition", "valeur": "OUI"},
        {"libelle": "Dépendant des transports en commun", "valeur": "NON"}
      ],
      "objectifs": [
        {"libelle": "Obtenir le permis de conduire", "valeur": "EN_COURS"}
      ]
    },
    {
      "libelle": "Surmonter ses contraintes familiales",
      "valeur": "OUI",
      "impact": "MOYEN",
      "est_prioritaire": false,
      "situations": [
        {"libelle": "Enfant(s) de moins de 3 ans sans solution de garde", "valeur": "OUI"},
        {"libelle": "Contraintes horaires", "valeur": "OUI"}
      ],
      "objectifs": [
        {"libelle": "Trouver des solutions de garde d'enfant", "valeur": "EN_COURS"}
      ]
    }
  ],
  "pouvoir_agir": {
    "confiance": "NON",
    "accompagnement": "OUI",
    "resultat_analyse": "Besoin d'appui pour consolider sa confiance à mener ses démarches"
  },
  "autonomie_numerique": {
    "impact": "FAIBLE",
    "situations": [
      {"libelle": "Dispose d'un smartphone", "valeur": "OUI"},
      {"libelle": "Dispose d'un ordinateur", "valeur": "NON"},
      {"libelle": "Difficulté démarches en ligne", "valeur": "OUI"}
    ],
    "objectifs": [
      {"libelle": "Maîtriser les fondamentaux du numérique", "valeur": "EN_COURS"}
    ]
  },
  "agent": {
    "nom": "Lefèvre",
    "prenom": "Jean-Marc",
    "structure": "FT Agence Cahors"
  },
  "date_mise_a_jour": "2025-03-12"
}
```

## Mock Data

`seed.py` creates one sample orientation with realistic data (inspired by the Sophie Martin example from the diagnostic documentation):
- Person: Sophie Martin, 34, Cahors
- Sender: Jean-Marc Lefèvre, FT Agence Cahors, prescripteur
- Modalité: "Accompagnement vers l'emploi"
- Diagnostic: JSON blob with professional project (assistante de vie), mobility and family barriers, low confidence, digital skills gap
- One initial history event ("Nouvelle demande")
- No initial messages

## Out of Scope

- List view of orientations (to be designed later)
- User authentication / login
- Edit functionality for personal info
- "Autres actions" dropdown actions
- Real France Travail API integration
