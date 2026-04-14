"""Simple matching logic for solution recommendations."""

import json
from collections import defaultdict
from datetime import date

from .models import Beneficiary, Service, Solution

# Cities in the Lille metropolitan area
LILLE_METRO = {
    "lille",
    "hellemmes",
    "roubaix",
    "tourcoing",
    "villeneuve-d'ascq",
    "villeneuve d'ascq",
    "lomme",
    "marcq-en-baroeul",
    "lambersart",
    "wasquehal",
    "croix",
    "mons-en-baroeul",
    "faches-thumesnil",
    "wattrelos",
    "hem",
    "loos",
    "wambrechies",
}

# Solutions that require travel but are still reachable from Lille metro
LILLE_REACHABLE = LILLE_METRO | {"cambrai", "douai", "lens", "arras"}


def compute_age(birthdate_str: str | None) -> int | None:
    return _compute_age(birthdate_str)


def _compute_age(birthdate_str: str | None) -> int | None:
    if not birthdate_str:
        return None
    try:
        bd = date.fromisoformat(birthdate_str)
        today = date.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except ValueError:
        return None


def _parse_eligibilities(beneficiary: Beneficiary) -> dict:
    """Extract boolean eligibility flags from a beneficiary's data."""
    eligibilities = json.loads(beneficiary.eligibilites) if beneficiary.eligibilites else []
    elig_set = set(eligibilities)

    is_brsa = "Éligibilité IAE à valider" in elig_set or any("BRSA" in e.upper() for e in eligibilities)
    is_detld = "PASS IAE valide" in elig_set or any("DETLD" in e.upper() for e in eligibilities)
    is_qpv = any("QPV" in e.upper() for e in eligibilities)
    is_rqth = any("RQTH" in e.upper() for e in eligibilities)

    # Also check diagnostic data for QPV/BRSA hints
    diagnostic = json.loads(beneficiary.diagnostic_data) if beneficiary.diagnostic_data else {}
    extra = diagnostic.get("extra", {})
    identite = extra.get("identite", {})

    # Check address for QPV indicators
    address = (beneficiary.person_address or "").lower()
    if "résidence" in address or "hellemmes" in address:
        is_qpv = True

    # Check if person has BRSA from diagnostic
    situation = extra.get("situationAdministrative", {})
    if situation.get("beneficiaireRSA"):
        is_brsa = True
    if situation.get("inscritPoleEmploiDepuis") and "DETLD" in str(situation.get("inscritPoleEmploiDepuis", "")):
        is_detld = True

    # Extract diagnostic signals for fit matching
    has_health_constraint = False
    has_mobility_constraint = False
    is_autonomous = False
    has_project = False

    tc = diagnostic.get("thematiqueContrainte", {})
    for c in tc.get("contraintes", []):
        if c.get("valeur") in ("NON_ABORDEE", "NON_ABORDE", None):
            continue
        libelle = (c.get("libelle") or "").lower()
        if "santé" in libelle:
            has_health_constraint = True
        if "mobilité" in libelle:
            has_mobility_constraint = True

    pa = diagnostic.get("pouvoirAgir") or {}
    if pa.get("confiance") == "OUI" and pa.get("accompagnement") != "OUI":
        is_autonomous = True

    if diagnostic.get("besoinsParDiagnostic"):
        diag_entry = diagnostic["besoinsParDiagnostic"][0].get("diagnostic", {})
        if diag_entry.get("nomMetier"):
            has_project = True

    return {
        "is_brsa": is_brsa,
        "is_detld": is_detld,
        "is_qpv": is_qpv,
        "is_rqth": is_rqth,
        "age": _compute_age(beneficiary.person_birthdate),
        "diploma_level": identite.get("niveauDiplome"),
        "has_health_constraint": has_health_constraint,
        "has_mobility_constraint": has_mobility_constraint,
        "is_autonomous": is_autonomous,
        "has_project": has_project,
    }


def compute_beneficiary_types(beneficiary: Beneficiary) -> list[str]:
    """Return the subset of {QPV, RSA, AAH, DELD, DETLD, Jeune, Senior} that applies."""
    profile = _parse_eligibilities(beneficiary)
    types: list[str] = []
    if profile["is_qpv"]:
        types.append("QPV")
    if profile["is_brsa"]:
        types.append("RSA")

    eligibilities = json.loads(beneficiary.eligibilites) if beneficiary.eligibilites else []
    diagnostic = json.loads(beneficiary.diagnostic_data) if beneficiary.diagnostic_data else {}
    extra = diagnostic.get("extra", {})
    situation = extra.get("situationAdministrative", {})
    has_aah = any("AAH" in e.upper() for e in eligibilities) or bool(situation.get("beneficiaireAAH"))
    if has_aah:
        types.append("AAH")

    inscription_date_str = (extra.get("insertionActiviteEconomique") or {}).get("dateEnregistrement") or (
        extra.get("modaliteSuivi") or {}
    ).get("dateEnregistrement")
    months = _months_since(inscription_date_str)
    if months is not None:
        if months > 24:
            types.append("DETLD")
        elif months > 12:
            types.append("DELD")

    age = profile["age"]
    if age is not None:
        if age < 26:
            types.append("Jeune")
        elif age >= 50:
            types.append("Senior")
    return types


def _months_since(iso_date_str: str | None) -> int | None:
    if not iso_date_str:
        return None
    try:
        bd = date.fromisoformat(iso_date_str[:10])
    except ValueError:
        return None
    today = date.today()
    return (today.year - bd.year) * 12 + (today.month - bd.month) - (1 if today.day < bd.day else 0)


def _person_city(beneficiary: Beneficiary) -> str | None:
    """Extract city name from address string."""
    address = beneficiary.person_address or ""
    # Expect format like "12 rue des Lilas, 59000 Lille"
    parts = address.split(",")
    if len(parts) >= 2:
        city_part = parts[-1].strip()
        # Remove postal code
        tokens = city_part.split()
        if len(tokens) >= 2 and tokens[0].isdigit():
            return " ".join(tokens[1:])
        return city_part
    return None


def _is_nearby(beneficiary: Beneficiary, solution: Solution) -> bool:
    """Check if solution is geographically relevant for the person."""
    if not solution.commune:
        # Modalités FT have no commune — always relevant
        return True

    person_city = _person_city(beneficiary)
    if not person_city:
        return True  # Can't filter, show everything

    person_city_lower = person_city.lower()
    solution_commune_lower = solution.commune.lower()

    # Direct match
    if person_city_lower == solution_commune_lower:
        return True

    # Both in Lille metro or reachable area
    if person_city_lower in LILLE_METRO and solution_commune_lower in LILLE_REACHABLE:
        return True

    return False


def _matches(beneficiary: Beneficiary, solution: Solution, profile: dict) -> bool:
    """Check if a person is eligible for a solution."""
    age = profile["age"]

    # Territory-bound solutions (PLIE): person must be in the same commune
    territory_bound_types = {"plie"}
    if solution.solution_type in territory_bound_types and solution.commune:
        person_city = _person_city(beneficiary)
        if person_city and person_city.lower() != solution.commune.lower():
            return False

    # Health constraint → skip physical solutions
    if solution.requires_physical and profile.get("has_health_constraint"):
        return False

    # Autonomy-gated solutions (GEIQ, Prépa qualification) → only for people with a project
    if solution.requires_autonomy and not profile.get("has_project"):
        return False

    # Age constraints
    if solution.age_min and age and age < solution.age_min:
        return False
    if solution.age_max and age and age > solution.age_max:
        return False

    # Diploma constraints
    if solution.max_diploma_level and profile.get("diploma_level"):
        try:
            if int(profile["diploma_level"]) > solution.max_diploma_level:
                return False
        except (ValueError, TypeError):
            pass

    # Eligibility requirements — at least one required flag must match
    required_flags = []
    if solution.requires_brsa:
        required_flags.append(profile["is_brsa"])
    if solution.requires_detld:
        required_flags.append(profile["is_detld"])
    if solution.requires_qpv:
        required_flags.append(profile["is_qpv"])
    if solution.requires_rqth:
        required_flags.append(profile["is_rqth"])

    if required_flags and not any(required_flags):
        return False

    return True


def compute_recommendations(
    beneficiary: Beneficiary, solutions: list[Solution], current_structure_type: str | None = None
) -> dict:
    """Return matched solutions grouped by category.

    Returns:
        {
            "recommended": list of top 3-4 solutions,
            "employeurs": list of SIAE/GEIQ solutions,
            "services": list of all matching solutions,
            "parcours": list of parcours solutions (modalités, PLIE, E2C, EPIDE),
        }
    """
    profile = _parse_eligibilities(beneficiary)

    # Filter by proximity and eligibility
    nearby = [s for s in solutions if _is_nearby(beneficiary, s)]
    matched = [s for s in nearby if _matches(beneficiary, s, profile)]

    # Group by category
    employeur_types = {"aci", "ei", "ai", "etti", "geiq", "cui_cie"}
    parcours_types = {
        "modalite_ft",
        "plie",
        "e2c",
        "epide",
        "cui_cae",
        "prepa_competences",
        "promo_16_18",
        "cdd_tremplin_ea",
    }
    employeurs = [s for s in matched if s.solution_type in employeur_types]
    parcours = [s for s in matched if s.solution_type in parcours_types]

    # Modalités FT: only show when person already has a FT modalité (suggesting a change).
    # If they have a structure référente or nothing, don't recommend modalités.
    current_modalite = beneficiary.modalite  # e.g. "Guidé", or None
    if current_modalite:
        # Keep modalités FT that are different from the current one
        parcours = [
            s for s in parcours if s.solution_type != "modalite_ft" or current_modalite.lower() not in s.name.lower()
        ]
    else:
        # No current modalité → remove all modalités FT
        parcours = [s for s in parcours if s.solution_type != "modalite_ft"]

    # Build recommended list: prioritize solutions with available places
    available = [s for s in matched if s.places_disponibles > 0]
    saturated = [s for s in matched if s.places_disponibles == 0]

    # Apply same modalité filter to candidates
    all_candidates = available + saturated
    if current_modalite:
        all_candidates = [
            s
            for s in all_candidates
            if s.solution_type != "modalite_ft" or current_modalite.lower() not in s.name.lower()
        ]
    else:
        all_candidates = [s for s in all_candidates if s.solution_type != "modalite_ft"]

    # Diversify recommended: max 1 modalité, max 1 SIAE, max 1 GEIQ
    siae_types = {"aci", "ei", "etti", "ai"}
    recommended = []
    counts = {"modalite_ft": 0, "siae": 0, "geiq": 0}
    for s in all_candidates:
        if len(recommended) >= 4:
            break
        if s.solution_type == "modalite_ft":
            if counts["modalite_ft"] >= 1:
                continue
            counts["modalite_ft"] += 1
        elif s.solution_type in siae_types:
            if counts["siae"] >= 1:
                continue
            counts["siae"] += 1
        elif s.solution_type == "geiq":
            if counts["geiq"] >= 1:
                continue
            counts["geiq"] += 1
        recommended.append(s)

    # Group by solution type_label: best first per type, exclude modalités FT
    # Also skip the type the person is currently in (e.g., already at an ACI → no more ACI)
    acronym_to_solution_type = {"aci": "aci", "ei": "ei", "plie": "plie", "e2c": "e2c", "geiq": "geiq"}
    skip_solution_type = acronym_to_solution_type.get((current_structure_type or "").lower())

    # Sheltered paths (ACI, CUI-CAE) are less relevant for autonomous people with a project
    stabilization_types = {"aci", "cui_cae"}

    by_type: dict[str, list] = {}
    for s in matched:
        if s.solution_type == "modalite_ft":
            continue
        if skip_solution_type and s.solution_type == skip_solution_type:
            continue
        if profile.get("is_autonomous") and profile.get("has_project") and s.solution_type in stabilization_types:
            continue
        label = s.type_label
        if label not in by_type:
            by_type[label] = []
        by_type[label].append(s)

    # Sort each group by relevance
    diagnostic = json.loads(beneficiary.diagnostic_data) if beneficiary.diagnostic_data else {}
    projet_metier = ""
    if diagnostic.get("besoinsParDiagnostic"):
        diag = diagnostic["besoinsParDiagnostic"][0].get("diagnostic", {})
        projet_metier = (diag.get("nomMetier") or "").lower()

    def _relevance(s: Solution) -> tuple:
        desc = ((s.description or "") + " " + (s.name or "")).lower()
        projet_words = [w for w in projet_metier.split() if len(w) > 3]
        keyword_match = sum(1 for w in projet_words if w in desc)
        if not projet_metier and ("remobilisation" in desc or "projet professionnel" in desc):
            keyword_match = 1
        person_city = _person_city(beneficiary)
        same_city = 1 if person_city and s.commune and person_city.lower() == s.commune.lower() else 0
        available = 1 if s.places_disponibles > 0 else 0
        return (-keyword_match, -same_city, -available, s.name)

    for label in by_type:
        by_type[label].sort(key=_relevance)

    # Rank types: direct-action solutions before preparatory ones for autonomous people
    preparatory_types = {"prepa_competences"}

    def _type_relevance(label: str) -> tuple:
        best = by_type[label][0]
        # Autonomous person with a project → penalize preparatory solutions
        is_prep = (
            1
            if (profile.get("is_autonomous") and profile.get("has_project") and best.solution_type in preparatory_types)
            else 0
        )
        return (is_prep,) + _relevance(best)

    sorted_types = sorted(by_type.keys(), key=_type_relevance)
    by_type = {k: by_type[k] for k in sorted_types[:3]}

    return {
        "recommended": recommended,
        "by_type": by_type,
        "employeurs": employeurs,
        "services": matched,
        "parcours": parcours,
    }


CONTRAINTE_KEYWORD_TO_CATEGORY = [
    ("mobilité", "mobilite"),
    ("logement", "logement"),
    ("financi", "financieres"),
    ("santé", "sante"),
    ("administrati", "administratif"),
    ("judiciaire", "administratif"),
    ("lecture", "francais"),
    ("écriture", "francais"),
    ("calcul", "francais"),
    ("français", "francais"),
    ("familial", "famille"),
    ("numérique", "numerique"),
]


def _category_for_contrainte(libelle: str) -> str | None:
    low = libelle.lower()
    for kw, cat in CONTRAINTE_KEYWORD_TO_CATEGORY:
        if kw in low:
            return cat
    return None


def get_contrainte_services(beneficiary: Beneficiary, services: list[Service]) -> list[dict]:
    """Return services matching the beneficiary's declared contraintes, grouped by contrainte."""
    diagnostic = json.loads(beneficiary.diagnostic_data) if beneficiary.diagnostic_data else {}
    tc = diagnostic.get("thematiqueContrainte") or {}
    raw_contraintes = [
        c
        for c in tc.get("contraintes") or []
        if c.get("valeur") and c["valeur"] not in ("NON_ABORDEE", "NON_ABORDE")
    ]
    if not raw_contraintes:
        return []

    person_city = _person_city(beneficiary)
    person_city_lower = person_city.lower() if person_city else None

    def _nearby(svc: Service) -> bool:
        if not svc.commune or not person_city_lower:
            return True
        sc = svc.commune.lower()
        return sc == person_city_lower or (person_city_lower in LILLE_METRO and sc in LILLE_METRO)

    impact_weight = {"FORT": 3, "MOYEN": 2, "FAIBLE": 1, "NON_RENSEIGNE": 0}
    result = []
    for c in raw_contraintes:
        cat = _category_for_contrainte(c.get("libelle") or "")
        if not cat:
            continue
        matching = [s for s in services if s.category == cat and _nearby(s)]
        if not matching:
            continue
        result.append(
            {
                "contrainte": c,
                "services": matching,
                "est_prioritaire": bool(c.get("estPrioritaire")),
                "impact": c.get("impact") or "NON_RENSEIGNE",
            }
        )

    result.sort(key=lambda r: (not r["est_prioritaire"], -impact_weight.get(r["impact"], 0)))
    return result


def get_services_for_beneficiary(beneficiary: Beneficiary, services: list[Service]) -> dict[str, list[Service]]:
    """Return services grouped by category_label, filtered by proximity."""
    person_city = _person_city(beneficiary)
    person_city_lower = person_city.lower() if person_city else None

    grouped: dict[str, list[Service]] = defaultdict(list)
    for svc in services:
        # Filter by proximity: same commune or both in Lille metro
        if svc.commune and person_city_lower:
            svc_commune_lower = svc.commune.lower()
            if svc_commune_lower != person_city_lower and not (
                person_city_lower in LILLE_METRO and svc_commune_lower in LILLE_METRO
            ):
                continue
        grouped[svc.category_label].append(svc)

    return dict(grouped)
