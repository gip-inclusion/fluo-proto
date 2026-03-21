import json
from datetime import datetime

from sqlmodel import Session, select

from database import engine, init_db
from models import HistoryEvent, Message, Orientation

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
    with Session(engine) as session:
        count = session.exec(select(Orientation)).all()
        if count:
            print("Database already seeded.")
            return

        now = datetime(2025, 3, 12, 10, 30).isoformat()

        o1 = Orientation(
            status="nouvelle", created_at=now,
            person_first_name="Sophie", person_last_name="MARTIN",
            person_phone="06 12 34 56 78", person_email="sophie.martin@email.fr",
            person_birthdate="1990-06-15", person_address="Cahors, 46000",
            sender_name="Jean-Marc LEFÈVRE", sender_type="prescripteur",
            sender_organization="FT Agence Cahors", sender_email="jean-marc.lefevre@francetravail.fr",
            sender_message="Mme Martin souhaite se reconvertir comme assistante de vie. "
            "Elle a besoin d'un accompagnement pour lever ses freins de mobilité et de garde d'enfant.",
            modalite="accompagnement_emploi",
            diagnostic_data=json.dumps(DIAGNOSTIC_DATA_1, ensure_ascii=False),
        )
        session.add(o1)
        session.flush()
        session.add(HistoryEvent(orientation_id=o1.id, event_type="created", created_at=now))

        date2 = datetime(2025, 3, 5, 14, 15).isoformat()
        o2 = Orientation(
            status="acceptee", created_at=date2,
            person_first_name="Karim", person_last_name="BENALI",
            person_phone="06 98 76 54 32", person_email="karim.benali@email.fr",
            person_birthdate="1985-11-22", person_address="Lille, 59000",
            sender_name="Nathalie DUPONT", sender_type="prescripteur",
            sender_organization="Mission Locale Lille", sender_email="n.dupont@ml-lille.fr",
            sender_message="M. Benali est en recherche active d'emploi dans le secteur de la logistique. "
            "Il a besoin d'un accompagnement renforcé.",
            modalite="accompagnement_emploi",
            diagnostic_data=json.dumps(DIAGNOSTIC_DATA_2, ensure_ascii=False),
        )
        session.add(o2)
        session.flush()
        session.add(HistoryEvent(orientation_id=o2.id, event_type="created", created_at=date2))
        session.add(HistoryEvent(orientation_id=o2.id, event_type="accepted", created_at=datetime(2025, 3, 7, 9, 0).isoformat()))

        date3 = datetime(2025, 3, 8, 11, 0).isoformat()
        o3 = Orientation(
            status="refusee", created_at=date3,
            person_first_name="Amina", person_last_name="DIALLO",
            person_phone="06 55 44 33 22", person_email="amina.diallo@email.fr",
            person_birthdate="1992-04-10", person_address="Roubaix, 59100",
            sender_name="Pierre MOREAU", sender_type="orienteur",
            sender_organization="CCAS Roubaix", sender_email="p.moreau@ccas-roubaix.fr",
            sender_message="Mme Diallo souhaite une formation en comptabilité. "
            "Orientation vers un accompagnement adapté.",
            modalite="accompagnement_emploi",
            diagnostic_data=json.dumps(DIAGNOSTIC_DATA_3, ensure_ascii=False),
        )
        session.add(o3)
        session.flush()
        session.add(HistoryEvent(orientation_id=o3.id, event_type="created", created_at=date3))
        session.add(HistoryEvent(orientation_id=o3.id, event_type="refused", created_at=datetime(2025, 3, 10, 16, 30).isoformat()))

        date4 = datetime(2025, 3, 14, 9, 45).isoformat()
        o4 = Orientation(
            status="nouvelle", created_at=date4,
            person_first_name="Lucas", person_last_name="PETIT",
            person_phone="07 11 22 33 44", person_email="lucas.petit@email.fr",
            person_birthdate="1998-08-03", person_address="Villeneuve-d'Ascq, 59491",
            sender_name="Nathalie DUPONT", sender_type="prescripteur",
            sender_organization="Mission Locale Lille", sender_email="n.dupont@ml-lille.fr",
            sender_message="M. Petit sort d'un contrat en intérim et souhaite se stabiliser. "
            "Besoin d'un accompagnement vers un emploi durable.",
            modalite="accompagnement_emploi",
            diagnostic_data=json.dumps(DIAGNOSTIC_DATA_4, ensure_ascii=False),
        )
        session.add(o4)
        session.flush()
        session.add(HistoryEvent(orientation_id=o4.id, event_type="created", created_at=date4))

        date5 = datetime(2025, 3, 18, 8, 30).isoformat()
        o5 = Orientation(
            status="nouvelle", created_at=date5,
            person_first_name="Fatou", person_last_name="NDIAYE",
            person_phone="06 77 88 99 00", person_email="fatou.ndiaye@email.fr",
            person_birthdate="1988-01-25", person_address="Tourcoing, 59200",
            sender_name="Jean-Marc LEFÈVRE", sender_type="prescripteur",
            sender_organization="FT Agence Cahors", sender_email="jean-marc.lefevre@francetravail.fr",
            sender_message="Mme Ndiaye est en reconversion professionnelle après un congé parental. "
            "Elle cherche un accompagnement dans le secteur de l'aide à la personne.",
            modalite="accompagnement_emploi",
            diagnostic_data=json.dumps(DIAGNOSTIC_DATA_5, ensure_ascii=False),
        )
        session.add(o5)
        session.flush()
        session.add(HistoryEvent(orientation_id=o5.id, event_type="created", created_at=date5))

        session.add(Message(
            orientation_id=o2.id, author_name="PLIE Lille Avenir",
            content="Merci pour cette orientation, nous prenons en charge le dossier.",
            created_at=datetime(2025, 3, 6, 10, 0).isoformat(),
        ))

        session.commit()
        print("Seeded 5 orientations.")


if __name__ == "__main__":
    seed()
