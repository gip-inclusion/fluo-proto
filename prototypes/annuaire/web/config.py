import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://annuaire:annuaire@localhost:5432/annuaire",
)

SERVICE_NAME = "France Travail Bordeaux Mériadeck"

# Left sidebar navigation. "Annuaire pro" carries a Bêta badge and is the only
# built page — the other items are decorative, matching a real les-emplois sidebar.
NAV_ITEMS = [
    {"href": "#", "icon": "ri-home-line", "label": "Accueil", "active_prefix": "/accueil"},
    {"href": "#", "icon": "ri-draft-line", "label": "Candidatures", "active_prefix": "/candidatures"},
    {"href": "#", "icon": "ri-group-line", "label": "Mes candidats", "active_prefix": "/candidats"},
    {
        "href": "/annuaire",
        "icon": "ri-contacts-book-line",
        "label": "Annuaire pro",
        "active_prefix": "/annuaire",
        "badge": "Bêta",
    },
]

# Structure types and their theme-inclusion colour token. The tag renders as the
# "-lighter" background with the matching "text-" colour (see includes/_tag.html).
STRUCTURE_TYPES = [
    "France Travail",
    "Conseil Départemental",
    "PLIE",
    "EPIDE",
    "École de la 2e chance",
    "Apprentis d'Auteuil",
    "CAP Emploi",
]

STRUCTURE_TYPE_COLORS = {
    "France Travail": "bg-info",
    "Conseil Départemental": "bg-pilotage",
    "PLIE": "bg-marche",
    "EPIDE": "bg-emploi",
    "École de la 2e chance": "bg-communaute",
    "Apprentis d'Auteuil": "bg-important",
    "CAP Emploi": "bg-success",
}

# Contact means: query value -> (label, Remix icon).
CONTACT_MEANS = [
    ("phone", "Téléphone", "ri-phone-line"),
    ("email", "Courriel", "ri-mail-line"),
    ("form", "Formulaire", "ri-file-text-line"),
    ("agenda", "Agenda", "ri-calendar-2-line"),
]

CONTACT_MEANS_LABELS = {key: (label, icon) for key, label, icon in CONTACT_MEANS}

# Objects offered in the "Envoyer un message" accordion. The last entry reveals
# a free-text field (see the js-subject-select handler in directory.html).
MESSAGE_SUBJECTS = [
    "Besoin d'information sur un accompagnement",
    "Demande de suivi conjoint",
    "Coordination autour d'une situation",
    "Proposition de partenariat",
    "Demande de présentation de votre offre",
    "Organisation d'une rencontre",
    "Participation à un événement",
    "Intervention auprès de nos publics",
    "Autre (avec précision)",
]

# Meeting formats offered in the "Réserver un rendez-vous" accordion.
RDV_TYPES = ["Visio", "Téléphone", "Présentiel", "Au choix"]

# Objects offered in the "Réserver un rendez-vous" accordion (no free-text option).
RDV_SUBJECTS = [
    "Point de coordination",
    "Réunion de suivi",
    "Échange autour d'une situation",
    "Premier contact",
    "Rencontre partenariale",
    "Information sur un dispositif",
    "Assistance technique",
]

WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
