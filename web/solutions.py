from datetime import date

# Mock local structures for the Lille area, grouped by solution type.
# Filter keys: max_age (int), modalites (list of modalite_ft values).
# Groups with no filter are always shown.
SOLUTIONS = [
    {
        "key": "plie",
        "title": "PLIE",
        "action": "dora",
        "structures": [
            {
                "name": "PLIE Lille Avenir",
                "address": "2 rue de Courtrai, 59000 Lille",
                "phone": "06 85 78 55 92",
                "email": "contact@plie-lille-avenir.fr",
            },
        ],
    },
    {
        "key": "mde",
        "title": "Maison de l'emploi",
        "modalites": ["global", "intensif"],
        "action": "dora",
        "structures": [
            {
                "name": "Maison de l'Emploi Lille-Lomme-Hellemmes",
                "address": "Place Augustin Laurent, 59000 Lille",
                "phone": "03 20 63 79 00",
                "horaires": "Du lundi au vendredi : 8h30-12h – 13h30-17h",
            },
            {
                "name": "Maison de l'Emploi de Roubaix",
                "address": "97 rue de l'Épeule, 59100 Roubaix",
                "phone": "03 20 66 28 40",
                "horaires": "Du lundi au vendredi : 9h-12h – 14h-17h",
            },
        ],
    },
    {
        "key": "prepa",
        "title": "Prépa Compétences",
        "action": "dora",
        "structures": [
            {
                "name": "Prépa Compétences — AFPA Lomme",
                "address": "35 rue de la Mitterie, 59160 Lomme",
                "phone": "09 72 72 39 36",
                "email": "mc_hauts-de-france@afpa.fr",
            },
        ],
    },
    {
        "key": "e2c",
        "title": "École de la 2ᵉ Chance (E2C)",
        "max_age": 25,
        "action": "dora",
        "structures": [
            {
                "name": "E2C Grand Lille",
                "address": "30 rue des Jardins, 59000 Lille",
                "phone": "03 20 06 22 60",
                "email": "contact@e2c-grandlille.fr",
            },
        ],
    },
    {
        "key": "epide",
        "title": "EPIDE",
        "max_age": 25,
        "action": "dora",
        "structures": [
            {
                "name": "Centre EPIDE de Cambrai",
                "address": "Caserne Mortier, Rue Louis Blériot, 59400 Cambrai",
                "phone": "03 27 74 29 60",
                "horaires": "Du lundi au vendredi : 8h-12h – 13h-17h",
            },
        ],
    },
    {
        "key": "iae_geiq",
        "title": "IAE & GEIQ",
        "action": "emplois",
        "structures": [
            {
                "badge": "GEIQ",
                "name": "GEIQ Métropole Européenne de Lille",
                "postes": [
                    {
                        "titre": "Apprenti cuisinier en contrat d'apprentissage",
                        "contrat": "Contrat d'apprentissage",
                        "heures": "35h/semaine",
                        "lieu": "Lille (59)",
                        "distance": "0 km",
                    },
                    {
                        "titre": "Agent de propreté et d'hygiène",
                        "contrat": "Contrat de professionnalisation",
                        "heures": "35h/semaine",
                        "lieu": "Villeneuve-d'Ascq (59)",
                        "distance": "8,5 km",
                    },
                ],
            },
            {
                "badge": "ACI",
                "name": "Régie de Quartier Lille Sud",
                "postes": [
                    {
                        "titre": "Ouvrier(e) polyvalent(e) des espaces verts",
                        "contrat": "CDDI",
                        "heures": "26h/semaine",
                        "lieu": "Lille (59)",
                        "distance": "2,3 km",
                    },
                ],
            },
            {
                "badge": "AI",
                "name": "Aréli",
                "postes": [
                    {
                        "titre": "Aide de cuisine / employé(e) de cantine",
                        "contrat": "Mise à disposition",
                        "heures": "20h/semaine",
                        "lieu": "Lomme (59)",
                        "distance": "5,2 km",
                    },
                    {
                        "titre": "Employé(e) de ménage à domicile",
                        "contrat": "Mise à disposition",
                        "heures": "15h/semaine",
                        "lieu": "Lille (59)",
                        "distance": "1,8 km",
                    },
                ],
            },
        ],
    },
]


def compute_age(birthdate_str: str | None) -> int | None:
    if not birthdate_str:
        return None
    bd = date.fromisoformat(birthdate_str)
    today = date.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))


def filter_solutions(groups: list[dict], age: int | None, modalite: str | None) -> list[dict]:
    out = []
    for g in groups:
        if g.get("max_age") and (not age or age > g["max_age"]):
            continue
        if g.get("modalites") and (not modalite or modalite not in g["modalites"]):
            continue
        out.append(g)
    return out
