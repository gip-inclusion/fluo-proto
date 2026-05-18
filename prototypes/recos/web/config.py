import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://recos:recos@localhost:5432/recos",
)

UI_VARIANT = os.environ.get("UI_VARIANT", "recos")

SERVICE_NAME = "France Travail"

MODALITE_LABELS = {
    "Suivi": "Suivi",
    "Guidé": "Guidé",
    "Renforcé": "Renforcé",
    "Global": "Global",
}

ELIGIBILITY_COLORS = {
    "PASS IAE valide": "bg-success",
    "Éligibilité IAE à valider": "bg-warning",
    "Éligible PLIE": "bg-info",
    "Éligible EPIDE": "bg-info",
    "Éligible E2C": "bg-info",
}

BENEFICIARY_TYPES = ["QPV", "RSA", "AAH", "OETH", "ZRR", "DELD", "DETLD", "Jeune", "Senior"]

BENEFICIARY_TYPE_COLORS = {
    "QPV": "bg-info",
    "RSA": "bg-warning",
    "AAH": "bg-important",
    "OETH": "bg-communaute",
    "ZRR": "bg-emploi",
    "DELD": "bg-pilotage",
    "DETLD": "bg-danger",
    "Jeune": "bg-success",
    "Senior": "bg-marche",
}

NAV_ITEMS = [
    {"href": "/dashboard", "icon": "ri-home-line", "label": "Accueil", "active_prefix": "/dashboard"},
    {"href": "#", "icon": "ri-draft-line", "label": "Candidatures", "active_prefix": "/candidatures"},
    {
        "icon": "ri-user-line",
        "label": "Candidats",
        "slug": "candidats",
        "subitems": [
            {"href": "#", "label": "Mes candidats", "active_prefix": "/mes-candidats"},
            {"href": "#", "label": "Tous les candidats de la structure", "active_prefix": "/candidats-structure"},
            {"href": "#", "label": "Gérer les prolongations de PASS IAE", "active_prefix": "/prolongations"},
        ],
    },
    {
        "icon": "ri-team-line",
        "label": "Organisation",
        "slug": "organisation",
        "subitems": [
            {"href": "#", "label": "Présentation", "active_prefix": "/presentation"},
            {"href": "#", "label": "Collaborateurs", "active_prefix": "/collaborateurs"},
        ],
    },
    {
        "icon": "ri-search-line",
        "label": "Rechercher",
        "slug": "rechercher",
        "subitems": [
            {"href": "#", "label": "Un emploi inclusif", "active_prefix": "/search/employers"},
            {"href": "#", "label": "Un prescripteur habilité", "active_prefix": "/search/prescribers"},
            {"href": "#", "label": "Un service d'insertion", "active_prefix": "/search/services"},
        ],
    },
    {
        "href": "/beneficiaries",
        "icon": "ri-lightbulb-line",
        "label": "Actions recommandées",
        "active_prefix": "/beneficiar",
    },
]

PRESCRIPTION_STATUS_LABELS = {
    "en_attente": ("En attente", "bg-warning-lighter text-warning"),
    "acceptee": ("Acceptée", "bg-success-lighter text-success"),
    "refusee": ("Refusée", "bg-danger-lighter text-danger"),
}

TAG_COLORS = {
    "POINT_FORT": ("Point fort", "bg-success"),
    "BESOIN": ("Besoin", "bg-info"),
    "NON_EXPLORE": ("Non exploré", "bg-secondary"),
    "OUI": ("Oui", "bg-danger"),
    "NON": ("Non", "bg-primary"),
    "NON_ABORDEE": ("Non abordé", "bg-secondary"),
    "NON_ABORDE": ("Non abordé", "bg-secondary"),
    "EN_COURS": ("En cours", "bg-warning"),
    "REALISE": ("Réalisé", "bg-success"),
    "CLOTUREE": ("Clôturé", "bg-success"),
    "ABANDONNE": ("Abandonné", "bg-secondary"),
    "FORT": ("Fort", "bg-danger"),
    "MOYEN": ("Moyen", "bg-warning"),
    "FAIBLE": ("Faible", "bg-info"),
    "NON_RENSEIGNE": ("—", "bg-secondary"),
}
