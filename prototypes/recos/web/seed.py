import json
from pathlib import Path

from sqlmodel import Session

from .database import engine, init_db
from .models import Beneficiary, Professional, Solution, Structure

_data_dir = Path(__file__).parent.parent / "data"

STRUCTURES = [
    {"name": "Jardins de Cocagne", "type_acronym": "ACI", "key": "aci"},
    {"name": "Lille Avenir", "type_acronym": "PLIE", "key": "plie"},
    {"name": "Ville de Montluçon", "type_acronym": "CCAS", "key": "ccas"},
    {"name": "Envie Nord", "type_acronym": "ACI", "key": "aci2"},
    {"name": "E2C Grand Lille", "type_acronym": "E2C", "key": "e2c"},
]

PROFESSIONALS = [
    {"first_name": "Marie", "last_name": "Lefebvre", "structure_key": None, "key": "ft_referent"},
    {"first_name": "Sophie", "last_name": "Dufour", "structure_key": "plie", "key": "plie_ref"},
    {"first_name": "Ahmed", "last_name": "Bouzid", "structure_key": "aci", "key": "aci_ref"},
    {"first_name": "Claire", "last_name": "Petit", "structure_key": "e2c", "key": "e2c_ref"},
]

PROFILES = [
    {
        "file": "brsa.json",
        "person_phone": "06 12 34 56 78",
        "person_email": "k.larrieu@example.fr",
        "person_birthdate": "1992-03-15",
        "person_address": "12 rue des Lilas, 59000 Lille",
        "structure_key": None,
        "referent_key": "ft_referent",
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
        "referent_key": "plie_ref",
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
        "referent_key": "ft_referent",
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
        "referent_key": "aci_ref",
        "eligibilites": ["Éligible EPIDE"],
        "nb_prescriptions": 2,
    },
]


SOLUTIONS = [
    # Modalités FT — always available, no restrictions
    {
        "name": "Modalité Suivi",
        "solution_type": "modalite_ft",
        "type_label": "Modalité FT",
        "description": "Accompagnement ponctuel pour les demandeurs d'emploi autonomes dans leurs démarches.",
        "conditions_admission": "Inscription France Travail active",
        "places_disponibles": 99,
    },
    {
        "name": "Modalité Guidé",
        "solution_type": "modalite_ft",
        "type_label": "Modalité FT",
        "description": "Accompagnement régulier avec un conseiller référent pour structurer le parcours de retour à l'emploi.",
        "conditions_admission": "Inscription France Travail active",
        "places_disponibles": 99,
    },
    {
        "name": "Modalité Renforcé",
        "solution_type": "modalite_ft",
        "type_label": "Modalité FT",
        "description": "Accompagnement intensif avec entretiens fréquents pour les personnes éloignées de l'emploi.",
        "conditions_admission": "Inscription France Travail active, freins identifiés",
        "places_disponibles": 99,
    },
    # SIAE near Lille
    {
        "name": "Jardins de Cocagne Lille",
        "solution_type": "aci",
        "type_label": "ACI",
        "structure_name": "Jardins de Cocagne",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Chantier d'insertion par le maraîchage biologique. Activités de production, conditionnement et distribution de paniers de légumes.",
        "conditions_admission": "Éligibilité IAE validée, capacité à travailler en extérieur",
        "places_disponibles": 3,
        "requires_brsa": True,
        "requires_detld": True,
        "requires_qpv": True,
    },
    {
        "name": "Envie Nord",
        "solution_type": "ei",
        "type_label": "EI",
        "structure_name": "Envie Nord",
        "commune": "Roubaix",
        "code_postal": "59100",
        "description": "Entreprise d'insertion spécialisée dans la collecte et la rénovation d'appareils électroménagers.",
        "conditions_admission": "Éligibilité IAE validée",
        "places_disponibles": 0,
        "requires_brsa": True,
        "requires_detld": True,
        "requires_qpv": True,
    },
    {
        "name": "Tissons la Solidarité",
        "solution_type": "aci",
        "type_label": "ACI",
        "structure_name": "Tissons la Solidarité",
        "commune": "Tourcoing",
        "code_postal": "59200",
        "description": "Chantier d'insertion dans le tri et la valorisation de textiles. Formation aux gestes de tri, repassage et vente.",
        "conditions_admission": "Éligibilité IAE validée",
        "places_disponibles": 7,
        "requires_brsa": True,
        "requires_detld": True,
        "requires_qpv": True,
    },
    {
        "name": "Nord Emploi Services",
        "solution_type": "etti",
        "type_label": "ETTI",
        "structure_name": "Nord Emploi Services",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Entreprise de travail temporaire d'insertion. Missions d'intérim dans le BTP, la logistique et l'industrie.",
        "conditions_admission": "Éligibilité IAE validée, mobilité requise",
        "places_disponibles": 5,
        "requires_brsa": True,
        "requires_detld": True,
        "requires_qpv": True,
    },
    {
        "name": "Réseau Artisanal Solidaire",
        "solution_type": "ei",
        "type_label": "EI",
        "structure_name": "Réseau Artisanal Solidaire",
        "commune": "Villeneuve-d'Ascq",
        "code_postal": "59650",
        "description": "Entreprise d'insertion proposant des activités de menuiserie, peinture et petits travaux de rénovation.",
        "conditions_admission": "Éligibilité IAE validée, intérêt pour les métiers manuels",
        "places_disponibles": 0,
        "requires_brsa": True,
        "requires_detld": True,
        "requires_qpv": True,
    },
    # GEIQ near Lille
    {
        "name": "GEIQ BTP Nord",
        "solution_type": "geiq",
        "type_label": "GEIQ",
        "structure_name": "GEIQ BTP Nord",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Groupement d'employeurs pour l'insertion et la qualification dans le bâtiment et travaux publics.",
        "conditions_admission": "Motivation pour le secteur BTP, aptitude physique",
        "places_disponibles": 8,
    },
    {
        "name": "GEIQ Propreté Hauts-de-France",
        "solution_type": "geiq",
        "type_label": "GEIQ",
        "structure_name": "GEIQ Propreté HdF",
        "commune": "Roubaix",
        "code_postal": "59100",
        "description": "Formation et emploi en alternance dans les métiers de la propreté et de l'hygiène.",
        "conditions_admission": "Aucun diplôme requis, motivation",
        "places_disponibles": 4,
    },
    {
        "name": "GEIQ Industrie Nord",
        "solution_type": "geiq",
        "type_label": "GEIQ",
        "structure_name": "GEIQ Industrie Nord",
        "commune": "Tourcoing",
        "code_postal": "59200",
        "description": "Parcours qualifiant dans les métiers de l'industrie : conduite de ligne, maintenance, logistique.",
        "conditions_admission": "Niveau CAP minimum, mobilité",
        "places_disponibles": 0,
    },
    # PLIE
    {
        "name": "PLIE Lille Avenir",
        "solution_type": "plie",
        "type_label": "PLIE",
        "structure_name": "Lille Avenir",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Plan local pour l'insertion et l'emploi. Accompagnement renforcé et individualisé vers l'emploi durable.",
        "conditions_admission": "Demandeur d'emploi de longue durée, résidant sur le territoire lillois",
        "places_disponibles": 10,
        "max_diploma_level": 5,
    },
    {
        "name": "PLIE Roubaix Insertion",
        "solution_type": "plie",
        "type_label": "PLIE",
        "structure_name": "Roubaix Insertion",
        "commune": "Roubaix",
        "code_postal": "59100",
        "description": "Accompagnement global vers l'emploi pour les habitants de Roubaix et environs.",
        "conditions_admission": "Résidant sur Roubaix ou communes associées",
        "places_disponibles": 6,
        "max_diploma_level": 5,
    },
    # E2C
    {
        "name": "E2C Grand Lille",
        "solution_type": "e2c",
        "type_label": "E2C",
        "structure_name": "E2C Grand Lille",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "École de la deuxième chance. Parcours individualisé alternant remise à niveau, stages en entreprise et accompagnement social.",
        "conditions_admission": "16-25 ans, sans diplôme ni qualification",
        "places_disponibles": 5,
        "age_max": 25,
    },
    # EPIDE
    {
        "name": "EPIDE Lille",
        "solution_type": "epide",
        "type_label": "EPIDE",
        "structure_name": "EPIDE",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Établissement pour l'insertion dans l'emploi. Parcours en internat de 8 à 24 mois avec formation, sport et accompagnement.",
        "conditions_admission": "18-25 ans, niveau infra-bac, volontaire",
        "places_disponibles": 2,
        "age_max": 25,
        "max_diploma_level": 3,
    },
    # Solutions near Lyon / Marseille (should NOT appear for Lille people)
    {
        "name": "Atelier et Chantiers Lyon",
        "solution_type": "aci",
        "type_label": "ACI",
        "structure_name": "Atelier et Chantiers Lyon",
        "commune": "Lyon",
        "code_postal": "69000",
        "description": "Chantier d'insertion dans l'entretien des espaces verts et la petite maçonnerie.",
        "conditions_admission": "Éligibilité IAE validée",
        "places_disponibles": 4,
        "requires_brsa": True,
        "requires_detld": True,
    },
    {
        "name": "Marseille Insertion Pro",
        "solution_type": "ei",
        "type_label": "EI",
        "structure_name": "Marseille Insertion Pro",
        "commune": "Marseille",
        "code_postal": "13000",
        "description": "Entreprise d'insertion dans les services aux entreprises : nettoyage, accueil, logistique.",
        "conditions_admission": "Éligibilité IAE validée",
        "places_disponibles": 6,
        "requires_brsa": True,
        "requires_detld": True,
    },
    {
        "name": "GEIQ Logistique Rhône",
        "solution_type": "geiq",
        "type_label": "GEIQ",
        "structure_name": "GEIQ Logistique Rhône",
        "commune": "Lyon",
        "code_postal": "69000",
        "description": "Parcours qualifiant dans la logistique et le transport.",
        "conditions_admission": "Permis B souhaité",
        "places_disponibles": 3,
    },
]


def seed() -> None:
    init_db()
    with Session(engine) as session:
        # Solutions
        for sol_data in SOLUTIONS:
            sol = Solution(
                name=sol_data["name"],
                solution_type=sol_data["solution_type"],
                type_label=sol_data["type_label"],
                structure_name=sol_data.get("structure_name"),
                commune=sol_data.get("commune"),
                code_postal=sol_data.get("code_postal"),
                description=sol_data.get("description"),
                conditions_admission=sol_data.get("conditions_admission"),
                places_disponibles=sol_data.get("places_disponibles", 0),
                age_min=sol_data.get("age_min"),
                age_max=sol_data.get("age_max"),
                requires_brsa=sol_data.get("requires_brsa", False),
                requires_detld=sol_data.get("requires_detld", False),
                requires_qpv=sol_data.get("requires_qpv", False),
                requires_rqth=sol_data.get("requires_rqth", False),
                max_diploma_level=sol_data.get("max_diploma_level"),
            )
            session.add(sol)

        # Structures
        structure_map = {}
        for s_data in STRUCTURES:
            s = Structure(name=s_data["name"], type_acronym=s_data["type_acronym"])
            session.add(s)
            session.flush()
            structure_map[s_data["key"]] = s.id

        # Professionals
        pro_map = {}
        for p_data in PROFESSIONALS:
            p = Professional(
                first_name=p_data["first_name"],
                last_name=p_data["last_name"],
                structure_id=structure_map.get(p_data["structure_key"]),
            )
            session.add(p)
            session.flush()
            pro_map[p_data["key"]] = p.id

        # Beneficiaries
        for profile in PROFILES:
            data = json.loads((_data_dir / profile["file"]).read_text())
            identite = data.get("extra", {}).get("identite", {})
            modalite_suivi = data.get("extra", {}).get("modaliteSuivi", {})

            modalite = modalite_suivi.get("modaliteEnCours") if not profile["structure_key"] else None
            structure_id = structure_map.get(profile["structure_key"])
            referent_id = pro_map.get(profile["referent_key"])

            b = Beneficiary(
                person_first_name=identite.get("prenom", "Prénom"),
                person_last_name=identite.get("nom", "NOM"),
                person_phone=profile["person_phone"],
                person_email=profile["person_email"],
                person_birthdate=profile["person_birthdate"],
                person_address=profile["person_address"],
                modalite=modalite,
                structure_referente_id=structure_id,
                referent_id=referent_id,
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
