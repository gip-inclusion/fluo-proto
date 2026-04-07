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

    return {
        "is_brsa": is_brsa,
        "is_detld": is_detld,
        "is_qpv": is_qpv,
        "is_rqth": is_rqth,
        "age": _compute_age(beneficiary.person_birthdate),
        "diploma_level": identite.get("niveauDiplome"),
    }


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

    # Both in Lille metro
    if person_city_lower in LILLE_METRO and solution_commune_lower in LILLE_METRO:
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


def compute_recommendations(beneficiary: Beneficiary, solutions: list[Solution]) -> dict:
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

    return {
        "recommended": recommended,
        "employeurs": employeurs,
        "services": matched,
        "parcours": parcours,
    }


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
