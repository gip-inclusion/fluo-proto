import json
from pathlib import Path

from sqlmodel import Session

from .database import engine, init_db
from .models import Beneficiary, Structure

_data_dir = Path(__file__).parent.parent / "data"

PROFILES = [
    {
        "file": "brsa.json",
        "person_phone": "06 12 34 56 78",
        "person_email": "k.larrieu@example.fr",
        "person_birthdate": "1992-03-15",
        "person_address": "12 rue des Lilas, 59000 Lille",
        "structure_key": None,
        "modalite": None,  # read from JSON
        "eligibilites": ["Éligibilité IAE à valider"],
        "nb_prescriptions": 1,
    },
    {
        "file": "detld-glo.json",
        "person_phone": "06 98 76 54 32",
        "person_email": "s.delmas@example.fr",
        "person_birthdate": "1975-11-22",
        "person_address": "45 avenue Foch, 59800 Lille",
        "structure_key": "plie",
        "modalite": None,  # read from JSON
        "eligibilites": ["PASS IAE valide", "Éligible PLIE"],
        "nb_prescriptions": 3,
    },
    {
        "file": "fle-qpv-brsa.json",
        "person_phone": "07 45 23 67 89",
        "person_email": "m.benziane@example.fr",
        "person_birthdate": "1988-06-04",
        "person_address": "8 résidence Les Moulins, 59260 Hellemmes",
        "structure_key": None,
        "modalite": None,  # read from JSON
        "eligibilites": ["Éligibilité IAE à valider", "Éligible E2C"],
        "nb_prescriptions": 0,
    },
    {
        "file": "qpv.json",
        "person_phone": "06 33 44 55 66",
        "person_email": "d.caussade@example.fr",
        "person_birthdate": "1999-01-30",
        "person_address": "3 allée Rimbaud, 59650 Villeneuve-d'Ascq",
        "structure_key": "aci",
        "modalite": None,  # read from JSON
        "eligibilites": ["Éligible EPIDE"],
        "nb_prescriptions": 2,
    },
]

STRUCTURES = [
    {"name": "Jardins de Cocagne", "type_acronym": "ACI", "key": "aci"},
    {"name": "Lille Avenir", "type_acronym": "PLIE", "key": "plie"},
    {"name": "Ville de Montluçon", "type_acronym": "CCAS", "key": "ccas"},
    {"name": "Envie Nord", "type_acronym": "ACI", "key": "aci2"},
    {"name": "E2C Grand Lille", "type_acronym": "E2C", "key": "e2c"},
]


def seed() -> None:
    init_db()
    with Session(engine) as session:
        # Create structures
        structure_map = {}
        for s_data in STRUCTURES:
            s = Structure(name=s_data["name"], type_acronym=s_data["type_acronym"])
            session.add(s)
            session.flush()
            structure_map[s_data["key"]] = s.id

        # Create beneficiaries from diagnostic JSON files
        for profile in PROFILES:
            data = json.loads((_data_dir / profile["file"]).read_text())
            identite = data.get("extra", {}).get("identite", {})
            modalite_suivi = data.get("extra", {}).get("modaliteSuivi", {})

            modalite = modalite_suivi.get("modaliteEnCours") if not profile["structure_key"] else None
            structure_id = structure_map.get(profile["structure_key"])

            b = Beneficiary(
                person_first_name=identite.get("prenom", "Prénom"),
                person_last_name=identite.get("nom", "NOM"),
                person_phone=profile["person_phone"],
                person_email=profile["person_email"],
                person_birthdate=profile["person_birthdate"],
                person_address=profile["person_address"],
                modalite=modalite,
                structure_referente_id=structure_id,
                eligibilites=json.dumps(profile["eligibilites"]),
                nb_prescriptions=profile["nb_prescriptions"],
                diagnostic_data=json.dumps(data),
                date_inscription="2025-01-15",
            )
            session.add(b)

        session.commit()


if __name__ == "__main__":
    seed()
    print("Seeded.")
