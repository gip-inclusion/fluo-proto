import json
from pathlib import Path

from sqlmodel import Session

from .database import engine, init_db
from .models import Beneficiary, Prescription, Professional, Service, Solution, Structure  # noqa: F401

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
        "person_birthdate": "2002-01-30",
        "person_address": "3 allée Rimbaud, 59650 Villeneuve-d'Ascq",
        "structure_key": "aci",
        "referent_key": "aci_ref",
        "eligibilites": ["Éligible EPIDE"],
        "nb_prescriptions": 2,
    },
]


SOLUTIONS = [
    # ── Modalité FT ──
    {
        "name": "Modalité Renforcé",
        "solution_type": "modalite_ft",
        "type_label": "Modalité FT",
        "description": "Accompagnement intensif avec entretiens fréquents pour les personnes éloignées de l'emploi.",
        "conditions_admission": "Inscription France Travail active, freins identifiés",
        "places_disponibles": 99,
    },
    # ── ACI ──
    {
        "name": "Jardins de Cocagne Lille",
        "solution_type": "aci",
        "type_label": "ACI",
        "structure_name": "Jardins de Cocagne",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Maraîchage biologique : production, conditionnement et distribution de paniers. Travail en extérieur, encadrement technique.",
        "conditions_admission": "Éligibilité IAE, capacité à travailler en extérieur",
        "places_disponibles": 3,
        "requires_brsa": True,
        "requires_detld": True,
        "requires_qpv": True,
        "requires_physical": True,
    },
    {
        "name": "Tissons la Solidarité",
        "solution_type": "aci",
        "type_label": "ACI",
        "structure_name": "Tissons la Solidarité",
        "commune": "Tourcoing",
        "code_postal": "59200",
        "description": "Tri et valorisation de textiles. Formation aux gestes de tri, repassage, vente en boutique solidaire.",
        "conditions_admission": "Éligibilité IAE",
        "places_disponibles": 7,
        "requires_brsa": True,
        "requires_detld": True,
        "requires_qpv": True,
    },
    {
        "name": "Atelier Bois Solidaire",
        "solution_type": "aci",
        "type_label": "ACI",
        "structure_name": "Atelier Bois Solidaire",
        "commune": "Villeneuve-d'Ascq",
        "code_postal": "59650",
        "description": "Menuiserie et ébénisterie d'insertion. Fabrication de mobilier, réparation, initiation au travail du bois.",
        "conditions_admission": "Éligibilité IAE, intérêt pour le travail manuel",
        "places_disponibles": 0,
        "requires_brsa": True,
        "requires_detld": True,
        "requires_qpv": True,
        "requires_physical": True,
    },
    # ── EI ──
    {
        "name": "Envie Nord",
        "solution_type": "ei",
        "type_label": "EI",
        "structure_name": "Envie Nord",
        "commune": "Roubaix",
        "code_postal": "59100",
        "description": "Collecte et rénovation d'appareils électroménagers. Poste en atelier avec formation technique intégrée.",
        "conditions_admission": "Éligibilité IAE, autonomie de base en atelier",
        "places_disponibles": 4,
        "requires_brsa": True,
        "requires_detld": True,
        "requires_qpv": True,
    },
    # ── GEIQ ──
    {
        "name": "GEIQ BTP Nord",
        "solution_type": "geiq",
        "type_label": "GEIQ",
        "structure_name": "GEIQ BTP Nord",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Contrat pro en alternance dans le BTP : maçonnerie, peinture, électricité. Qualification diplômante en 12 mois.",
        "conditions_admission": "Motivation pour le BTP, aptitude physique, mobilité",
        "places_disponibles": 8,
        "requires_physical": True,
        "rome_code": "F1601",
        "telephone": "03 20 55 14 00",
        "courriel": "contact@geiqbtpnord.fr",
        "site_web": "https://www.geiqbtpnord.fr",
    },
    {
        "name": "GEIQ Propreté Hauts-de-France",
        "solution_type": "geiq",
        "type_label": "GEIQ",
        "structure_name": "GEIQ Propreté HdF",
        "commune": "Roubaix",
        "code_postal": "59100",
        "description": "Alternance dans les métiers de la propreté : agent de service, laveur de vitres, machiniste. Aucun diplôme requis.",
        "conditions_admission": "Aucun diplôme requis, motivation",
        "places_disponibles": 4,
        "rome_code": "K2204",
        "telephone": "03 20 45 78 90",
        "courriel": "contact@geiq-proprete-hdf.fr",
        "site_web": "https://geiq-proprete-hdf.fr",
    },
    {
        "name": "GEIQ Métiers Verts",
        "solution_type": "geiq",
        "type_label": "GEIQ",
        "structure_name": "GEIQ Métiers Verts",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Alternance dans les métiers agricoles, espaces verts, horticulture et paysagisme. En lien avec les exploitations et collectivités locales.",
        "conditions_admission": "Intérêt pour le travail en extérieur, pas de diplôme requis",
        "places_disponibles": 5,
        "requires_physical": True,
        "rome_code": "A1101",
        "telephone": "03 20 12 34 56",
        "courriel": "contact@geiq-metiers-verts.fr",
        "site_web": "https://geiq-metiers-verts.fr",
    },
    # ── PLIE ──
    {
        "name": "PLIE Lille Avenir",
        "solution_type": "plie",
        "type_label": "PLIE",
        "structure_name": "Lille Avenir",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Accompagnement renforcé et individualisé vers l'emploi durable. Référent unique, levée des freins, mise en situation professionnelle.",
        "conditions_admission": "DELD, résidant sur le territoire lillois, niveau V et infra",
        "places_disponibles": 10,
        "max_diploma_level": 5,
        "telephone": "03 20 95 57 67",
        "courriel": "contact@plielilleavenir.fr",
        "contact_nom_prenom": "Nathalie DUCROCQ",
        "site_web": "https://www.plielilleavenir.fr",
    },
    # ── E2C ──
    {
        "name": "E2C Grand Lille",
        "solution_type": "e2c",
        "type_label": "E2C",
        "structure_name": "E2C Grand Lille",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Parcours individualisé : remise à niveau, stages en entreprise, accompagnement social. Entrées permanentes, 4 à 18 mois.",
        "conditions_admission": "16-25 ans, sans diplôme ni qualification, sorti du système scolaire",
        "places_disponibles": 5,
        "age_min": 16,
        "age_max": 25,
        "telephone": "03 28 38 05 50",
        "courriel": "contact@e2c-grandlille.fr",
        "contact_nom_prenom": "Karim BENALI",
        "site_web": "https://e2c-grandlille.fr",
    },
    # ── EPIDE ──
    {
        "name": "EPIDE Cambrai",
        "solution_type": "epide",
        "type_label": "EPIDE",
        "structure_name": "EPIDE",
        "commune": "Cambrai",
        "code_postal": "59400",
        "description": "Internat de 8 à 24 mois : formation professionnelle, sport, vie collective, accompagnement santé. Centre le plus proche de la métropole lilloise.",
        "conditions_admission": "17-25 ans, niveau infra-bac, volontaire, hébergé sur place",
        "places_disponibles": 2,
        "age_min": 17,
        "age_max": 25,
        "max_diploma_level": 3,
        "telephone": "03 27 73 01 50",
        "courriel": "epide-cambrai@epide.fr",
        "contact_nom_prenom": "Julien LEFEBVRE",
        "site_web": "https://www.epide.fr/centre/cambrai",
    },
    # ── CUI-CAE ──
    {
        "name": "CUI-CAE Mairie de Lille",
        "solution_type": "cui_cae",
        "type_label": "CUI-CAE",
        "structure_name": "Mairie de Lille — Direction Espaces Verts",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "Contrat aidé 12 mois dans les espaces verts municipaux. Encadrement par un chef d'équipe, tutorat.",
        "conditions_admission": "DELD ou bénéficiaire RSA, résidant Lille métropole",
        "places_disponibles": 2,
        "requires_brsa": True,
        "requires_detld": True,
    },
    {
        "name": "CUI-CAE CCAS Roubaix",
        "solution_type": "cui_cae",
        "type_label": "CUI-CAE",
        "structure_name": "CCAS Roubaix — Service Solidarités",
        "commune": "Roubaix",
        "code_postal": "59100",
        "description": "Contrat aidé dans l'accueil et le soutien aux usagers du CCAS. Poste en lien avec le public, accompagnement intégré.",
        "conditions_admission": "DELD ou bénéficiaire RSA, +50 ans prioritaire",
        "places_disponibles": 1,
        "requires_brsa": True,
        "requires_detld": True,
    },
    # ── Prépa Compétences ──
    {
        "name": "Prépa Compétences — Métiers agricoles et espaces verts",
        "solution_type": "prepa_competences",
        "type_label": "Prépa Compétences",
        "structure_name": "AFPA Lille",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "3 mois de découverte des métiers agricoles, horticoles et paysagistes. Stages en exploitation et en collectivité.",
        "conditions_admission": "Demandeur d'emploi, projet en lien avec l'agriculture ou les espaces verts",
        "places_disponibles": 6,
    },
    {
        "name": "Prépa Compétences — Numérique et services",
        "solution_type": "prepa_competences",
        "type_label": "Prépa Compétences",
        "structure_name": "AFPA Roubaix",
        "commune": "Roubaix",
        "code_postal": "59100",
        "description": "4 mois pour découvrir les métiers du numérique : développeur web, infographiste, technicien informatique. Stages en entreprise.",
        "conditions_admission": "Demandeur d'emploi, intérêt pour le numérique, reconversion acceptée",
        "places_disponibles": 4,
    },
    {
        "name": "Prépa Compétences — Remobilisation et projet professionnel",
        "solution_type": "prepa_competences",
        "type_label": "Prépa Compétences",
        "structure_name": "Greta Lille Métropole",
        "commune": "Lille",
        "code_postal": "59000",
        "description": "2 mois pour définir ou confirmer un projet professionnel. Ateliers collectifs, immersions, bilan de compétences.",
        "conditions_admission": "Demandeur d'emploi sans projet défini",
        "places_disponibles": 10,
    },
    # ── CDD Tremplin EA — réservé TH ──
    {
        "name": "CDD Tremplin EA Handipro",
        "solution_type": "cdd_tremplin_ea",
        "type_label": "CDD Tremplin EA",
        "structure_name": "Handipro Nord",
        "commune": "Villeneuve-d'Ascq",
        "code_postal": "59650",
        "description": "CDD en entreprise adaptée : compétences professionnelles avec accompagnement renforcé et aménagement de poste.",
        "conditions_admission": "RQTH obligatoire, demandeur d'emploi",
        "places_disponibles": 3,
        "requires_rqth": True,
    },
    # ── Hors métropole (filtrage géographique) ──
    {
        "name": "ACI Rhône Solidaire",
        "solution_type": "aci",
        "type_label": "ACI",
        "structure_name": "Rhône Solidaire",
        "commune": "Lyon",
        "code_postal": "69000",
        "description": "Entretien d'espaces verts et petite maçonnerie en milieu urbain.",
        "conditions_admission": "Éligibilité IAE",
        "places_disponibles": 4,
        "requires_brsa": True,
        "requires_detld": True,
    },
]


THEMATIQUE_TO_CATEGORY = {
    "mobilite": ("Mobilité", "mobilite"),
    "numerique": ("Numérique", "numerique"),
    "se-former": ("Formation", "formation"),
    "trouver-un-emploi": ("Emploi", "emploi"),
    "preparer-sa-candidature": ("Emploi", "emploi"),
    "choisir-un-metier": ("Emploi", "emploi"),
    "difficultes-administratives-ou-juridiques": ("Démarches administratives", "administratif"),
    "difficultes-financieres": ("Difficultés financières", "financieres"),
    "sante": ("Santé", "sante"),
    "logement-hebergement": ("Logement", "logement"),
    "famille": ("Famille et parentalité", "famille"),
    "remobilisation": ("Remobilisation", "remobilisation"),
    "lecture-ecriture-calcul": ("Français et compétences de base", "francais"),
}

DATA_INCLUSION_FIXTURE = Path(__file__).resolve().parent.parent / "data" / "data_inclusion_services.json"


def _seed_services(session: Session) -> None:
    """Seed Service records from the committed data-inclusion fixture."""
    with open(DATA_INCLUSION_FIXTURE) as f:
        fixture = json.load(f)

    # Track how many per category to ensure variety
    category_counts: dict[str, int] = {}
    max_per_category = 5
    seen_names: set[str] = set()
    services_added = 0

    for row in fixture["lille_metro"]:
        if services_added >= 30:
            break

        name = row["nom"]
        if not name or name in seen_names:
            continue

        # Skip garde d'enfants
        if "garde" in name.lower() and "enfant" in name.lower():
            continue

        thematiques_raw = row["thematiques"]
        try:
            thematiques = json.loads(thematiques_raw)
        except (json.JSONDecodeError, TypeError):
            continue

        # Find first matching category
        category_key = None
        category_label = None
        for thematique in thematiques:
            prefix = thematique.split("--")[0] if "--" in thematique else thematique
            if prefix in THEMATIQUE_TO_CATEGORY:
                category_label, category_key = THEMATIQUE_TO_CATEGORY[prefix]
                break

        if not category_key:
            continue

        if category_counts.get(category_key, 0) >= max_per_category:
            continue

        structure_name = row["structure_name"] or ""
        description = row["description"] or ""
        # Truncate long descriptions
        if len(description) > 300:
            description = description[:297] + "..."

        svc = Service(
            name=name,
            structure_name=structure_name,
            commune=row["commune"],
            code_postal=row["code_postal"],
            description=description,
            category=category_key,
            category_label=category_label,
            thematiques=thematiques_raw,
            latitude=row["latitude"],
            longitude=row["longitude"],
            telephone=row["telephone"],
            courriel=row["courriel"],
            contact_nom_prenom=row["contact_nom_prenom"],
            site_web=row["site_web"],
            source=row.get("source"),
            lien_source=row.get("lien_source"),
            lien_mobilisation=row.get("lien_mobilisation"),
        )
        session.add(svc)
        seen_names.add(name)
        category_counts[category_key] = category_counts.get(category_key, 0) + 1
        services_added += 1

    # ── Supplementary: Apprentis d'Auteuil services across Hauts-de-France ──
    for row in fixture["auteuil"]:
        name = row["nom"]
        if not name or name in seen_names:
            continue
        try:
            thematiques = json.loads(row["thematiques"])
        except (json.JSONDecodeError, TypeError):
            continue
        category_key = None
        category_label = None
        for thematique in thematiques:
            prefix = thematique.split("--")[0] if "--" in thematique else thematique
            if prefix in THEMATIQUE_TO_CATEGORY:
                category_label, category_key = THEMATIQUE_TO_CATEGORY[prefix]
                break
        if not category_key:
            continue
        description = (row["description"] or "")[:297]
        svc = Service(
            name=name,
            structure_name=row["structure_name"] or "",
            commune=row["commune"],
            code_postal=row["code_postal"],
            description=description,
            category=category_key,
            category_label=category_label,
            thematiques=row["thematiques"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            telephone=row["telephone"],
            courriel=row["courriel"],
            contact_nom_prenom=row["contact_nom_prenom"],
            site_web=row["site_web"],
            source=row.get("source"),
            lien_source=row.get("lien_source"),
            lien_mobilisation=row.get("lien_mobilisation"),
        )
        session.add(svc)
        seen_names.add(name)


def seed() -> None:
    init_db()
    with Session(engine) as session:
        # Services from data-inclusion
        _seed_services(session)

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
                telephone=sol_data.get("telephone"),
                courriel=sol_data.get("courriel"),
                contact_nom_prenom=sol_data.get("contact_nom_prenom"),
                site_web=sol_data.get("site_web"),
                rome_code=sol_data.get("rome_code"),
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
