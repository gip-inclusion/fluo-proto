"""Seed the annuaire prototype with fictitious structures and professionals.

Run with: DATABASE_URL=... uv run python -m web.seed
All data below is invented — any resemblance to real people is coincidental.
"""

from sqlmodel import Session, SQLModel, delete

from .database import engine
from .models import Professional, Structure

# --- Structures -------------------------------------------------------------
# (name, type, address, city, phone, email, has_form, has_agenda)
STRUCTURES = [
    (
        "Agence France Travail Bordeaux Mériadeck",
        "France Travail",
        "9 rue Corps Franc Pommiès, 33000 Bordeaux",
        "Bordeaux",
        "05 56 00 12 00",
        "bordeaux.meriadeck@francetravail.fr",
        True,
        True,
    ),
    (
        "Agence France Travail Pau Université",
        "France Travail",
        "2 avenue du Doyen Poplawski, 64000 Pau",
        "Pau",
        "05 59 80 44 00",
        "pau.universite@francetravail.fr",
        True,
        False,
    ),
    (
        "PLIE Pau Béarn Pyrénées",
        "PLIE",
        "12 place Marguerite Laborde, 64000 Pau",
        "Pau",
        "05 59 11 50 30",
        "contact@plie-paubearn.fr",
        True,
        False,
    ),
    (
        "PLIE Rochefort Océan",
        "PLIE",
        "3 avenue Maurice Chupin, 17300 Rochefort",
        "Rochefort",
        "05 46 82 65 00",
        "accueil@plie-rochefortocean.fr",
        False,
        True,
    ),
    (
        "E2C Charente et Poitou",
        "École de la 2e chance",
        "45 rue de la Grande Champagne, 16000 Angoulême",
        "Angoulême",
        "05 45 38 77 10",
        "contact@e2c-charentepoitou.fr",
        True,
        True,
    ),
    (
        "E2C Bastia",
        "École de la 2e chance",
        "Immeuble Le Régent, avenue Sampiero Corso, 20200 Bastia",
        "Bastia",
        "04 95 30 12 40",
        "bastia@e2c-corse.fr",
        False,
        False,
    ),
    (
        "Centre EPIDE Bourges - Osmoy",
        "EPIDE",
        "Route de Bourges, 18390 Osmoy",
        "Osmoy",
        "02 48 68 30 00",
        "bourges@epide.fr",
        True,
        True,
    ),
    (
        "Conseil Départemental de la Gironde",
        "Conseil Départemental",
        "1 esplanade Charles de Gaulle, 33074 Bordeaux",
        "Bordeaux",
        "05 56 99 33 33",
        "insertion@gironde.fr",
        True,
        False,
    ),
    (
        "Cap emploi Gironde",
        "CAP Emploi",
        "103 rue Belleville, 33000 Bordeaux",
        "Bordeaux",
        "05 57 22 42 90",
        "accueil@capemploi33.fr",
        True,
        True,
    ),
    (
        "Apprentis d'Auteuil Nouvelle-Aquitaine",
        "Apprentis d'Auteuil",
        "18 rue de la Croix Blanche, 33800 Bordeaux",
        "Bordeaux",
        "05 56 91 70 20",
        "nouvelle-aquitaine@apprentis-auteuil.org",
        False,
        True,
    ),
]

# --- Professionals ----------------------------------------------------------
# (structure_index, first, last, role, phone, email, has_form, has_agenda)
# structure_index is 0-based into STRUCTURES above.
# A row with phone=email=None and has_form=has_agenda=False renders the
# "ne souhaite pas partager ses coordonnées" state.
PROFESSIONALS = [
    # 0 — FT Bordeaux Mériadeck (5 pros → triggers "voir les autres" on structure card)
    (
        0,
        "Nadia",
        "Belkacem",
        "Directrice d'agence",
        "05 56 00 12 01",
        "nadia.belkacem@francetravail.fr",
        True,
        True,
    ),
    (
        0,
        "Julien",
        "Moreau",
        "Conseiller en Insertion Professionnelle",
        "05 56 00 12 02",
        "julien.moreau@francetravail.fr",
        False,
        True,
    ),
    (
        0,
        "Sophie",
        "Da Costa",
        "Chargée de relations entreprise",
        "05 56 00 12 03",
        "sophie.dacosta@francetravail.fr",
        True,
        False,
    ),
    (
        0,
        "Karim",
        "Haddad",
        "Conseiller en Insertion Professionnelle",
        None,
        "karim.haddad@francetravail.fr",
        True,
        True,
    ),
    (
        0,
        "Émilie",
        "Renard",
        "Chargée d'accueil",
        None,
        None,
        False,
        False,
    ),
    # 1 — FT Pau Université
    (
        1,
        "Thomas",
        "Lefèvre",
        "Directeur d'agence",
        "05 59 80 44 01",
        "thomas.lefevre@francetravail.fr",
        True,
        False,
    ),
    (
        1,
        "Awa",
        "Diallo",
        "Conseillère en Insertion Professionnelle",
        "05 59 80 44 02",
        "awa.diallo@francetravail.fr",
        False,
        True,
    ),
    # 2 — PLIE Pau Béarn Pyrénées
    (
        2,
        "Christine",
        "Etchegoyen",
        "Directrice",
        "05 59 11 50 31",
        "christine.etchegoyen@plie-paubearn.fr",
        True,
        False,
    ),
    (
        2,
        "Mathieu",
        "Barrère",
        "Référent de parcours PLIE",
        "05 59 11 50 32",
        "mathieu.barrere@plie-paubearn.fr",
        True,
        True,
    ),
    (
        2,
        "Leïla",
        "Ben Amar",
        "Chargée de relations entreprise",
        None,
        "leila.benamar@plie-paubearn.fr",
        True,
        False,
    ),
    # 3 — PLIE Rochefort Océan
    (
        3,
        "Gaëlle",
        "Priou",
        "Coordinatrice PLIE",
        "05 46 82 65 01",
        "gaelle.priou@plie-rochefortocean.fr",
        False,
        True,
    ),
    (
        3,
        "Antoine",
        "Chauveau",
        "Référent de parcours PLIE",
        "05 46 82 65 02",
        "antoine.chauveau@plie-rochefortocean.fr",
        False,
        True,
    ),
    # 4 — E2C Charente et Poitou
    (
        4,
        "Valérie",
        "Nguyen",
        "Directrice",
        "05 45 38 77 11",
        "valerie.nguyen@e2c-charentepoitou.fr",
        True,
        True,
    ),
    (
        4,
        "Bruno",
        "Faucher",
        "Formateur référent",
        "05 45 38 77 12",
        "bruno.faucher@e2c-charentepoitou.fr",
        False,
        True,
    ),
    (
        4,
        "Sandra",
        "Lopez",
        "Conseillère en Insertion Professionnelle",
        None,
        "sandra.lopez@e2c-charentepoitou.fr",
        True,
        False,
    ),
    (
        4,
        "Yohan",
        "Mercier",
        "Chargé de relations entreprise",
        "05 45 38 77 14",
        None,
        True,
        True,
    ),
    # 5 — E2C Bastia
    (
        5,
        "Paul-Antoine",
        "Santini",
        "Responsable pédagogique",
        "04 95 30 12 41",
        "pa.santini@e2c-corse.fr",
        False,
        False,
    ),
    (
        5,
        "Laetitia",
        "Filippi",
        "Formatrice",
        None,
        None,
        False,
        False,
    ),
    # 6 — EPIDE Bourges - Osmoy
    (
        6,
        "Frédéric",
        "Aubert",
        "Directeur adjoint",
        "02 48 68 30 01",
        "frederic.aubert@epide.fr",
        True,
        True,
    ),
    (
        6,
        "Marion",
        "Delaunay",
        "Conseillère en Insertion Professionnelle",
        "02 48 68 30 02",
        "marion.delaunay@epide.fr",
        False,
        True,
    ),
    (
        6,
        "Idriss",
        "Traoré",
        "Cadre de compagnie",
        "02 48 68 30 03",
        "idriss.traore@epide.fr",
        True,
        False,
    ),
    # 7 — Conseil Départemental Gironde
    (
        7,
        "Hélène",
        "Boucher",
        "Responsable insertion",
        "05 56 99 33 34",
        "helene.boucher@gironde.fr",
        True,
        False,
    ),
    (
        7,
        "Cédric",
        "Vasseur",
        "Référent RSA",
        "05 56 99 33 35",
        "cedric.vasseur@gironde.fr",
        True,
        False,
    ),
    (
        7,
        "Fatou",
        "Sow",
        "Travailleuse sociale",
        None,
        "fatou.sow@gironde.fr",
        True,
        False,
    ),
    # 8 — Cap emploi Gironde
    (
        8,
        "Isabelle",
        "Marchand",
        "Directrice",
        "05 57 22 42 91",
        "isabelle.marchand@capemploi33.fr",
        True,
        True,
    ),
    (
        8,
        "Olivier",
        "Guérin",
        "Chargé de relations entreprise",
        "05 57 22 42 92",
        "olivier.guerin@capemploi33.fr",
        False,
        True,
    ),
    (
        8,
        "Nawel",
        "Cherif",
        "Conseillère en Insertion Professionnelle",
        None,
        "nawel.cherif@capemploi33.fr",
        True,
        True,
    ),
    # 9 — Apprentis d'Auteuil Nouvelle-Aquitaine
    (
        9,
        "Grégoire",
        "Lambert",
        "Responsable de dispositif",
        "05 56 91 70 21",
        "gregoire.lambert@apprentis-auteuil.org",
        True,
        True,
    ),
    (
        9,
        "Manon",
        "Roussel",
        "Éducatrice - accompagnement vers l'emploi",
        None,
        "manon.roussel@apprentis-auteuil.org",
        False,
        True,
    ),
]


def seed():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.exec(delete(Professional))
        session.exec(delete(Structure))
        session.commit()

        structures = []
        for name, type_, address, city, phone, email, has_form, has_agenda in STRUCTURES:
            s = Structure(
                name=name,
                type=type_,
                address=address,
                city=city,
                phone=phone,
                email=email,
                has_form=has_form,
                has_agenda=has_agenda,
            )
            session.add(s)
            structures.append(s)
        session.commit()
        for s in structures:
            session.refresh(s)

        for idx, first, last, role, phone, email, has_form, has_agenda in PROFESSIONALS:
            session.add(
                Professional(
                    first_name=first,
                    last_name=last,
                    role=role,
                    structure_id=structures[idx].id,
                    phone=phone,
                    email=email,
                    has_form=has_form,
                    has_agenda=has_agenda,
                )
            )
        session.commit()

        print(f"Seeded {len(structures)} structures and {len(PROFESSIONALS)} professionals.")


if __name__ == "__main__":
    seed()
