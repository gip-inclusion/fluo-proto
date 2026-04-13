import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://recos:recos@localhost:5432/recos",
)

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

BENEFICIARY_TYPES = ["QPV", "RSA", "AAH", "DELD", "DETLD", "Jeune", "Senior"]

BENEFICIARY_TYPE_COLORS = {
    "QPV": "bg-info",
    "RSA": "bg-warning",
    "AAH": "bg-important",
    "DELD": "bg-pilotage",
    "DETLD": "bg-danger",
    "Jeune": "bg-success",
    "Senior": "bg-marche",
}

NAV_ITEMS = [
    {"href": "/dashboard", "icon": "ri-home-line", "label": "Accueil", "active_prefix": "/dashboard"},
    {
        "href": "/beneficiaries",
        "icon": "ri-group-line",
        "label": "Personnes accompagnées",
        "active_prefix": "/beneficiar",
    },
    {
        "href": "/prescriptions-sent",
        "icon": "ri-compass-line",
        "label": "Demandes envoyées",
        "active_prefix": "/prescriptions-sent",
    },
    {
        "href": "/prescriptions-received",
        "icon": "ri-mail-send-line",
        "label": "Demandes reçues",
        "active_prefix": "/prescriptions-received",
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
