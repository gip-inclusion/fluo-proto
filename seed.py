import json
from datetime import datetime

from db import get_db, init_db

DIAGNOSTIC_DATA_1 = {
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

DIAGNOSTIC_DATA_2 = {
    "projet_professionnel": {
        "nom_metier": "Préparateur de commandes en logistique",
        "code_rome": "N1103",
        "statut": "VALIDE",
        "est_prioritaire": True,
    },
    "contraintes": [
        {
            "libelle": "Maîtriser la langue française",
            "valeur": "OUI",
            "impact": "MOYEN",
            "est_prioritaire": True,
            "situations": [
                {"libelle": "Difficulté à l'écrit", "valeur": "OUI"},
                {"libelle": "Difficulté à l'oral", "valeur": "NON"},
            ],
            "objectifs": [
                {"libelle": "Suivre une formation FLE à visée professionnelle", "valeur": "EN_COURS"},
            ],
        },
    ],
    "pouvoir_agir": {
        "confiance": "OUI",
        "accompagnement": "OUI",
        "resultat_analyse": "Karim est autonome et motivé, un accompagnement léger suffit",
    },
    "autonomie_numerique": {
        "impact": "FAIBLE",
        "situations": [
            {"libelle": "Dispose d'un smartphone", "valeur": "OUI"},
            {"libelle": "Dispose d'un ordinateur", "valeur": "OUI"},
            {"libelle": "Difficulté à réaliser des démarches administratives en ligne", "valeur": "NON"},
        ],
        "objectifs": [],
    },
    "agent": {
        "nom": "Dupont",
        "prenom": "Nathalie",
        "structure": "Mission Locale Lille",
    },
    "date_mise_a_jour": "2025-03-04",
}

DIAGNOSTIC_DATA_3 = {
    "projet_professionnel": {
        "nom_metier": "Comptable",
        "code_rome": "M1203",
        "statut": "A_DEFINIR",
        "est_prioritaire": False,
    },
    "contraintes": [
        {
            "libelle": "Se loger",
            "valeur": "OUI",
            "impact": "FORT",
            "est_prioritaire": True,
            "situations": [
                {"libelle": "Hébergement chez un tiers", "valeur": "OUI"},
                {"libelle": "Risque de perte de logement", "valeur": "NON"},
            ],
            "objectifs": [
                {"libelle": "Accéder à un logement autonome", "valeur": "NON_ABORDE"},
            ],
        },
        {
            "libelle": "Surmonter ses contraintes familiales",
            "valeur": "OUI",
            "impact": "FORT",
            "est_prioritaire": True,
            "situations": [
                {"libelle": "Enfant(s) de moins de 3 ans sans solution de garde", "valeur": "NON"},
                {"libelle": "Contraintes horaires", "valeur": "OUI"},
                {"libelle": "Famille monoparentale", "valeur": "OUI"},
            ],
            "objectifs": [
                {"libelle": "Trouver des solutions de garde d'enfant", "valeur": "NON_ABORDE"},
                {"libelle": "Adapter les horaires de travail", "valeur": "EN_COURS"},
            ],
        },
        {
            "libelle": "Développer sa mobilité",
            "valeur": "OUI",
            "impact": "MOYEN",
            "est_prioritaire": False,
            "situations": [
                {"libelle": "Aucun moyen de transport à disposition", "valeur": "NON"},
                {"libelle": "Dépendant des transports en commun", "valeur": "OUI"},
            ],
            "objectifs": [
                {"libelle": "Obtenir le permis de conduire", "valeur": "NON_ABORDE"},
            ],
        },
    ],
    "pouvoir_agir": {
        "confiance": "OUI",
        "accompagnement": "NON",
        "resultat_analyse": "Amina est déterminée mais fait face à des freins périphériques importants",
    },
    "autonomie_numerique": {
        "impact": "FAIBLE",
        "situations": [
            {"libelle": "Dispose d'un smartphone", "valeur": "OUI"},
            {"libelle": "Dispose d'un ordinateur", "valeur": "OUI"},
            {"libelle": "Difficulté à réaliser des démarches administratives en ligne", "valeur": "NON"},
        ],
        "objectifs": [],
    },
    "agent": {
        "nom": "Moreau",
        "prenom": "Pierre",
        "structure": "CCAS Roubaix",
    },
    "date_mise_a_jour": "2025-03-07",
}

DIAGNOSTIC_DATA_4 = {
    "projet_professionnel": {
        "nom_metier": "",
        "code_rome": "",
        "statut": "A_DEFINIR",
        "est_prioritaire": False,
    },
    "contraintes": [
        {
            "libelle": "Développer sa mobilité",
            "valeur": "OUI",
            "impact": "MOYEN",
            "est_prioritaire": False,
            "situations": [
                {"libelle": "Aucun moyen de transport à disposition", "valeur": "NON"},
                {"libelle": "Dépendant des transports en commun", "valeur": "OUI"},
            ],
            "objectifs": [
                {"libelle": "Obtenir le permis de conduire", "valeur": "EN_COURS"},
            ],
        },
    ],
    "pouvoir_agir": {
        "confiance": "NON",
        "accompagnement": "NON",
        "resultat_analyse": "Lucas manque de confiance et a du mal à se projeter dans un projet professionnel",
    },
    "autonomie_numerique": {
        "impact": "FORT",
        "situations": [
            {"libelle": "Dispose d'un smartphone", "valeur": "OUI"},
            {"libelle": "Dispose d'un ordinateur", "valeur": "NON"},
            {"libelle": "Difficulté à réaliser des démarches administratives en ligne", "valeur": "OUI"},
            {"libelle": "Ne dispose pas d'adresse e-mail", "valeur": "OUI"},
        ],
        "objectifs": [
            {"libelle": "Maîtriser les fondamentaux du numérique", "valeur": "NON_ABORDE"},
            {"libelle": "Créer une adresse e-mail", "valeur": "EN_COURS"},
        ],
    },
    "agent": {
        "nom": "Dupont",
        "prenom": "Nathalie",
        "structure": "Mission Locale Lille",
    },
    "date_mise_a_jour": "2025-03-13",
}

DIAGNOSTIC_DATA_5 = {
    "projet_professionnel": {
        "nom_metier": "Aide à domicile",
        "code_rome": "K1304",
        "statut": "EN_COURS",
        "est_prioritaire": True,
    },
    "contraintes": [
        {
            "libelle": "Surmonter ses contraintes familiales",
            "valeur": "OUI",
            "impact": "FORT",
            "est_prioritaire": True,
            "situations": [
                {"libelle": "Enfant(s) de moins de 3 ans sans solution de garde", "valeur": "OUI"},
                {"libelle": "Contraintes horaires", "valeur": "OUI"},
                {"libelle": "Famille monoparentale", "valeur": "OUI"},
            ],
            "objectifs": [
                {"libelle": "Trouver des solutions de garde d'enfant", "valeur": "EN_COURS"},
            ],
        },
        {
            "libelle": "Développer sa mobilité",
            "valeur": "OUI",
            "impact": "FORT",
            "est_prioritaire": True,
            "situations": [
                {"libelle": "Aucun moyen de transport à disposition", "valeur": "OUI"},
                {"libelle": "Dépendant des transports en commun", "valeur": "OUI"},
            ],
            "objectifs": [
                {"libelle": "Obtenir le permis de conduire", "valeur": "NON_ABORDE"},
                {"libelle": "S'informer sur les aides à la mobilité", "valeur": "EN_COURS"},
            ],
        },
        {
            "libelle": "Maîtriser la langue française",
            "valeur": "OUI",
            "impact": "MOYEN",
            "est_prioritaire": False,
            "situations": [
                {"libelle": "Difficulté à l'écrit", "valeur": "OUI"},
                {"libelle": "Difficulté à l'oral", "valeur": "NON"},
            ],
            "objectifs": [
                {"libelle": "Suivre une formation FLE à visée professionnelle", "valeur": "EN_COURS"},
            ],
        },
    ],
    "pouvoir_agir": {
        "confiance": "OUI",
        "accompagnement": "OUI",
        "resultat_analyse": "Fatou est volontaire et engagée, elle a besoin d'un cadre d'accompagnement structuré",
    },
    "autonomie_numerique": {
        "impact": "MOYEN",
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
    "date_mise_a_jour": "2025-03-17",
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
            "Mme Martin souhaite se reconvertir comme assistante de vie. "
            "Elle a besoin d'un accompagnement pour lever ses freins "
            "de mobilité et de garde d'enfant.",
            "accompagnement_emploi",
            json.dumps(DIAGNOSTIC_DATA_1, ensure_ascii=False),
        ),
    )

    conn.execute(
        "INSERT INTO history_event (orientation_id, event_type, created_at) VALUES (?, ?, ?)",
        (1, "created", now),
    )

    # Orientation 2: accepted
    date2 = datetime(2025, 3, 5, 14, 15).isoformat()
    conn.execute(
        """INSERT INTO orientation (
            status, created_at,
            person_first_name, person_last_name, person_phone, person_email,
            person_birthdate, person_address,
            sender_name, sender_type, sender_organization, sender_email, sender_message,
            modalite, diagnostic_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "acceptee",
            date2,
            "Karim",
            "BENALI",
            "06 98 76 54 32",
            "karim.benali@email.fr",
            "1985-11-22",
            "Lille, 59000",
            "Nathalie DUPONT",
            "prescripteur",
            "Mission Locale Lille",
            "n.dupont@ml-lille.fr",
            "M. Benali est en recherche active d'emploi dans le secteur de la logistique. "
            "Il a besoin d'un accompagnement renforcé.",
            "accompagnement_emploi",
            json.dumps(DIAGNOSTIC_DATA_2, ensure_ascii=False),
        ),
    )
    conn.execute(
        "INSERT INTO history_event (orientation_id, event_type, created_at) VALUES (?, ?, ?)",
        (2, "created", date2),
    )
    conn.execute(
        "INSERT INTO history_event (orientation_id, event_type, created_at) VALUES (?, ?, ?)",
        (2, "accepted", datetime(2025, 3, 7, 9, 0).isoformat()),
    )

    # Orientation 3: refused
    date3 = datetime(2025, 3, 8, 11, 0).isoformat()
    conn.execute(
        """INSERT INTO orientation (
            status, created_at,
            person_first_name, person_last_name, person_phone, person_email,
            person_birthdate, person_address,
            sender_name, sender_type, sender_organization, sender_email, sender_message,
            modalite, diagnostic_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "refusee",
            date3,
            "Amina",
            "DIALLO",
            "06 55 44 33 22",
            "amina.diallo@email.fr",
            "1992-04-10",
            "Roubaix, 59100",
            "Pierre MOREAU",
            "orienteur",
            "CCAS Roubaix",
            "p.moreau@ccas-roubaix.fr",
            "Mme Diallo souhaite une formation en comptabilité. "
            "Orientation vers un accompagnement adapté.",
            "accompagnement_emploi",
            json.dumps(DIAGNOSTIC_DATA_3, ensure_ascii=False),
        ),
    )
    conn.execute(
        "INSERT INTO history_event (orientation_id, event_type, created_at) VALUES (?, ?, ?)",
        (3, "created", date3),
    )
    conn.execute(
        "INSERT INTO history_event (orientation_id, event_type, created_at) VALUES (?, ?, ?)",
        (3, "refused", datetime(2025, 3, 10, 16, 30).isoformat()),
    )

    # Orientation 4: nouvelle
    date4 = datetime(2025, 3, 14, 9, 45).isoformat()
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
            date4,
            "Lucas",
            "PETIT",
            "07 11 22 33 44",
            "lucas.petit@email.fr",
            "1998-08-03",
            "Villeneuve-d'Ascq, 59491",
            "Nathalie DUPONT",
            "prescripteur",
            "Mission Locale Lille",
            "n.dupont@ml-lille.fr",
            "M. Petit sort d'un contrat en intérim et souhaite se stabiliser. "
            "Besoin d'un accompagnement vers un emploi durable.",
            "accompagnement_emploi",
            json.dumps(DIAGNOSTIC_DATA_4, ensure_ascii=False),
        ),
    )
    conn.execute(
        "INSERT INTO history_event (orientation_id, event_type, created_at) VALUES (?, ?, ?)",
        (4, "created", date4),
    )

    # Orientation 5: nouvelle
    date5 = datetime(2025, 3, 18, 8, 30).isoformat()
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
            date5,
            "Fatou",
            "NDIAYE",
            "06 77 88 99 00",
            "fatou.ndiaye@email.fr",
            "1988-01-25",
            "Tourcoing, 59200",
            "Jean-Marc LEFÈVRE",
            "prescripteur",
            "FT Agence Cahors",
            "jean-marc.lefevre@francetravail.fr",
            "Mme Ndiaye est en reconversion professionnelle après un congé parental. "
            "Elle cherche un accompagnement dans le secteur de l'aide à la personne.",
            "accompagnement_emploi",
            json.dumps(DIAGNOSTIC_DATA_5, ensure_ascii=False),
        ),
    )
    conn.execute(
        "INSERT INTO history_event (orientation_id, event_type, created_at) VALUES (?, ?, ?)",
        (5, "created", date5),
    )

    # Add a message on orientation 2 for realism
    conn.execute(
        "INSERT INTO message (orientation_id, author_name, content, created_at) VALUES (?, ?, ?, ?)",
        (2, "PLIE Lille Avenir", "Merci pour cette orientation, nous prenons en charge le dossier.",
         datetime(2025, 3, 6, 10, 0).isoformat()),
    )

    conn.commit()
    conn.close()
    print("Seeded 5 orientations.")


if __name__ == "__main__":
    seed()
