import os

DATABASE_URL = os.environ["DATABASE_URL"]

SERVICE_NAME = "PLIE Lille Avenir"

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

MODALITE_FT_LABELS = {
    "essentiel": "Essentiel",
    "intensif": "Intensif",
    "global": "Global",
}

ALL_STATUSES = ["nouvelle", "acceptee", "refusee"]

SENT_STATUS_LABELS = {
    "en_attente": ("En attente de réponse", "bg-info"),
    "acceptee": ("Acceptée", "bg-success"),
    "refusee": ("Refusée", "bg-danger"),
}

ALL_SENT_STATUSES = ["en_attente", "acceptee", "refusee"]

SCENARIOS = {
    "plie": {
        "slug": "plie",
        "label": "PLIE Lille Avenir",
        "description": "Orientations reçues",
        "nav": [
            {"label": "Tableau de bord", "icon": "ri-home-line", "href": "/plie/"},
            {
                "label": "Bénéficiaires",
                "icon": "ri-group-line",
                "href": "/plie/beneficiaires",
                "active_prefix": "/plie/beneficiaire",
            },
            {
                "label": "Orientations reçues",
                "icon": "ri-compass-line",
                "href": "/plie/orientations",
                "active_prefix": "/plie/orientation",
            },
        ],
    },
    "prescripteur": {
        "slug": "prescripteur",
        "label": "France Travail Lille",
        "description": "Orientations envoyées",
        "nav": [
            {"label": "Tableau de bord", "icon": "ri-home-line", "href": "/prescripteur/"},
            {
                "label": "Bénéficiaires",
                "icon": "ri-group-line",
                "href": "/prescripteur/beneficiaires",
                "active_prefix": "/prescripteur/beneficiaire",
            },
            {
                "label": "Orientations envoyées",
                "icon": "ri-compass-line",
                "href": "/prescripteur/orientations",
                "active_prefix": "/prescripteur/orientation",
            },
        ],
    },
}
