import json
from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from ..config import BENEFICIARY_TYPES
from ..database import engine
from ..matching import (
    COMMUNE_COORDS,
    compute_age,
    compute_beneficiary_types,
    compute_modalite_months,
    compute_recommendations,
    get_auteuil_services,
    get_contrainte_services,
    get_iae_geiq_solutions,
    get_projet_pro,
    get_services_for_beneficiary,
)
from ..models import Beneficiary, Prescription, Professional, Service, Solution, Structure

router = APIRouter()


def _templates(request: Request):
    return request.app.state.templates


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return _templates(request).TemplateResponse(
        "dashboard.html",
        {"request": request},
    )


@router.get("/search", response_class=HTMLResponse)
async def search(request: Request):
    return _templates(request).TemplateResponse(
        "search.html",
        {"request": request},
    )


@router.get("/flux-entrant", response_class=HTMLResponse)
async def flux_entrant(request: Request):
    selected_types = [t for t in request.query_params.getlist("type") if t in BENEFICIARY_TYPES]
    with Session(engine) as session:
        beneficiaries = session.exec(select(Beneficiary).order_by(Beneficiary.person_last_name)).all()
        for b in beneficiaries:
            b._types = compute_beneficiary_types(b)
            b._age = compute_age(b.person_birthdate)
        if selected_types:
            beneficiaries = [b for b in beneficiaries if any(t in b._types for t in selected_types)]
    return _templates(request).TemplateResponse(
        "flux_entrant.html",
        {
            "request": request,
            "beneficiaries": beneficiaries,
            "result_count": len(beneficiaries),
            "beneficiary_types": BENEFICIARY_TYPES,
            "selected_types": selected_types,
        },
    )


@router.get("/beneficiaries", response_class=HTMLResponse)
async def list_beneficiaries(request: Request):
    selected_types = [t for t in request.query_params.getlist("type") if t in BENEFICIARY_TYPES]
    ft_only = request.query_params.get("ft") == "1"
    ft_modalites = ["Renforcé", "Guidé"]
    selected_modalite = request.query_params.get("modalite") or ""
    if selected_modalite not in ft_modalites:
        selected_modalite = ""
    over5_only = request.query_params.get("over5") == "1"
    with Session(engine) as session:
        beneficiaries = session.exec(select(Beneficiary).order_by(Beneficiary.person_last_name)).all()
        structure_ids = [b.structure_referente_id for b in beneficiaries if b.structure_referente_id]
        structures = {}
        if structure_ids:
            for s in session.exec(select(Structure).where(Structure.id.in_(structure_ids))).all():
                structures[s.id] = s
        for b in beneficiaries:
            b._types = compute_beneficiary_types(b)
            b._structure = structures.get(b.structure_referente_id)
            b._age = compute_age(b.person_birthdate)
            b._modalite_months = compute_modalite_months(b)
        if selected_types:
            beneficiaries = [b for b in beneficiaries if any(t in b._types for t in selected_types)]
        if ft_only:
            beneficiaries = [b for b in beneficiaries if b.modalite]
            if selected_modalite:
                beneficiaries = [b for b in beneficiaries if b.modalite == selected_modalite]
            if over5_only:
                beneficiaries = [b for b in beneficiaries if b._modalite_months is not None and b._modalite_months > 5]
    return _templates(request).TemplateResponse(
        "beneficiary_list.html",
        {
            "request": request,
            "beneficiaries": beneficiaries,
            "result_count": len(beneficiaries),
            "beneficiary_types": BENEFICIARY_TYPES,
            "selected_types": selected_types,
            "ft_only": ft_only,
            "ft_modalites": ft_modalites,
            "selected_modalite": selected_modalite if ft_only else "",
            "over5_only": over5_only and ft_only,
        },
    )


@router.get("/beneficiary/{id}", response_class=HTMLResponse)
async def detail_beneficiary(request: Request, id: int):
    with Session(engine) as session:
        b = session.get(Beneficiary, id)
        if not b:
            return HTMLResponse("Not found", status_code=404)
        b._eligibility_list = json.loads(b.eligibilites) if b.eligibilites else []
        b._age = compute_age(b.person_birthdate)
        b._modalite_months = compute_modalite_months(b)
        b._types = compute_beneficiary_types(b)
        structure = None
        if b.structure_referente_id:
            structure = session.get(Structure, b.structure_referente_id)
        referent = None
        if b.referent_id:
            referent = session.get(Professional, b.referent_id)
            if referent and referent.structure_id:
                referent._structure = session.get(Structure, referent.structure_id)
            else:
                referent._structure = None
        diagnostic = json.loads(b.diagnostic_data) if b.diagnostic_data else None
        # Prescriptions for this person
        prescriptions = session.exec(
            select(Prescription).where(Prescription.beneficiary_id == id).order_by(Prescription.created_at.desc())
        ).all()
        prescription_solution_ids = [p.solution_id for p in prescriptions]
        prescription_solutions_map = {}
        if prescription_solution_ids:
            for s in session.exec(select(Solution).where(Solution.id.in_(prescription_solution_ids))).all():
                prescription_solutions_map[s.id] = s
        for p in prescriptions:
            p._solution = prescription_solutions_map.get(p.solution_id)
        # Solutions recommendations
        all_solutions = session.exec(select(Solution)).all()
        current_struct_type = structure.type_acronym if structure else None
        results = compute_recommendations(b, all_solutions, current_structure_type=current_struct_type)
        # Services grouped by category
        all_services = session.exec(select(Service)).all()
        services_grouped = get_services_for_beneficiary(b, all_services)
        contrainte_solutions = get_contrainte_services(b, all_services)
        from ..matching import _category_for_contrainte  # local import

        matched_categories = sorted(
            {
                cat
                for entry in contrainte_solutions
                if (cat := _category_for_contrainte(entry["contrainte"].get("libelle") or ""))
            }
        )
        # Suggest PLIE when beneficiary is followed by France Travail and has at least one active contrainte
        plie_solution = None
        if b.modalite and not b.structure_referente_id:
            tc = (diagnostic or {}).get("thematiqueContrainte") or {}
            has_active_contrainte = any(
                c.get("valeur") and c["valeur"] not in ("NON_ABORDEE", "NON_ABORDE")
                for c in (tc.get("contraintes") or [])
            )
            if has_active_contrainte:
                plie_solution = next((s for s in all_solutions if s.solution_type == "plie"), None)
        # Map center coords from beneficiary commune
        from ..matching import _person_city  # local import to avoid cycle

        city = (_person_city(b) or "").lower().strip()
        beneficiary_coords = COMMUNE_COORDS.get(city)
        # Jeunes paths (EPIDE, E2C) — only for beneficiaries aged 16-25
        jeunes_solutions: list = []
        age = b._age
        if age is not None and 16 <= age <= 25:
            jeunes_solutions = [
                s
                for s in all_solutions
                if s.solution_type in {"epide", "e2c"}
                and (s.age_min is None or age >= s.age_min)
                and (s.age_max is None or age <= s.age_max)
            ]
        # IAE / GEIQ for RSA/QPV/DETLD suivi FT
        projet = get_projet_pro(b)
        iae_solutions, geiq_solutions = get_iae_geiq_solutions(
            b, all_solutions, compute_beneficiary_types(b), (projet or {}).get("rome_code")
        )
        auteuil_services = get_auteuil_services(b, all_services, age, bool(projet and projet.get("nom_metier")))

        def _coords_for(obj):
            lat = getattr(obj, "latitude", None)
            lng = getattr(obj, "longitude", None)
            if lat is not None and lng is not None:
                return (lat, lng)
            commune = ((getattr(obj, "commune", None) or "").lower()).strip()
            return COMMUNE_COORDS.get(commune)

        map_points: list[dict] = []

        def _add_point(obj, label):
            coords = _coords_for(obj)
            if not coords:
                return
            map_points.append(
                {
                    "lat": coords[0],
                    "lng": coords[1],
                    "title": obj.name,
                    "structure": getattr(obj, "structure_name", "") or "",
                    "commune": obj.commune or "",
                    "label": label,
                }
            )

        for entry in contrainte_solutions:
            for s in entry["services"]:
                _add_point(s, entry["contrainte"].get("libelle") or "Contrainte")
        if plie_solution:
            _add_point(plie_solution, "PLIE")
        for s in jeunes_solutions:
            _add_point(s, s.type_label)
        for s in iae_solutions:
            _add_point(s, s.type_label)
        for s in geiq_solutions:
            _add_point(s, "GEIQ")
        for s in auteuil_services:
            _add_point(s, "Apprentis d'Auteuil")
    return _templates(request).TemplateResponse(
        "beneficiary_detail.html",
        {
            "request": request,
            "b": b,
            "structure": structure,
            "referent": referent,
            "diagnostic": diagnostic,
            "prescriptions": prescriptions,
            "results": results,
            "services_grouped": services_grouped,
            "contrainte_solutions": contrainte_solutions,
            "plie_solution": plie_solution,
            "beneficiary_coords": beneficiary_coords,
            "projet_pro": projet,
            "jeunes_solutions": jeunes_solutions,
            "iae_solutions": iae_solutions,
            "geiq_solutions": geiq_solutions,
            "auteuil_services": auteuil_services,
            "map_points": map_points,
            "matched_categories": matched_categories,
        },
    )


@router.get("/beneficiary/{id}/profil", response_class=HTMLResponse)
async def profil_beneficiary(request: Request, id: int):
    with Session(engine) as session:
        b = session.get(Beneficiary, id)
        if not b:
            return HTMLResponse("Not found", status_code=404)
        b._age = compute_age(b.person_birthdate)
        b._modalite_months = compute_modalite_months(b)
        b._types = compute_beneficiary_types(b)
        structure = None
        if b.structure_referente_id:
            structure = session.get(Structure, b.structure_referente_id)
        referent = None
        if b.referent_id:
            referent = session.get(Professional, b.referent_id)
            if referent and referent.structure_id:
                referent._structure = session.get(Structure, referent.structure_id)
            else:
                referent._structure = None
        diagnostic = json.loads(b.diagnostic_data) if b.diagnostic_data else None
    return _templates(request).TemplateResponse(
        "beneficiary_profil.html",
        {
            "request": request,
            "b": b,
            "structure": structure,
            "referent": referent,
            "diagnostic": diagnostic,
        },
    )


@router.get("/solution/{id}", response_class=HTMLResponse)
async def solution_detail(request: Request, id: int):
    from_id = request.query_params.get("from")
    with Session(engine) as session:
        solution = session.get(Solution, id)
        if not solution:
            return HTMLResponse("Not found", status_code=404)
        beneficiary = None
        if from_id:
            beneficiary = session.get(Beneficiary, int(from_id))
    return _templates(request).TemplateResponse(
        "solution_detail.html",
        {
            "request": request,
            "solution": solution,
            "b": beneficiary,
        },
    )


@router.post("/beneficiary/{beneficiary_id}/prescribe/{solution_id}")
async def prescribe(beneficiary_id: int, solution_id: int, message: str = Form("")):
    with Session(engine) as session:
        b = session.get(Beneficiary, beneficiary_id)
        s = session.get(Solution, solution_id)
        if not b or not s:
            return HTMLResponse("Not found", status_code=404)
        p = Prescription(
            beneficiary_id=beneficiary_id,
            solution_id=solution_id,
            message=message or None,
            created_at=datetime.now().isoformat(),
        )
        session.add(p)
        b.nb_prescriptions += 1
        session.commit()
        session.refresh(p)
        prescription_id = p.id
    return RedirectResponse(f"/prescription/{prescription_id}", status_code=303)


@router.get("/prescription/{id}", response_class=HTMLResponse)
async def prescription_detail(request: Request, id: int):
    with Session(engine) as session:
        p = session.get(Prescription, id)
        if not p:
            return HTMLResponse("Not found", status_code=404)
        beneficiary = session.get(Beneficiary, p.beneficiary_id)
        solution = session.get(Solution, p.solution_id)
    return _templates(request).TemplateResponse(
        "prescription_detail.html",
        {
            "request": request,
            "prescription": p,
            "beneficiary": beneficiary,
            "solution": solution,
        },
    )


@router.get("/prescriptions-sent", response_class=HTMLResponse)
async def prescriptions_sent(request: Request):
    with Session(engine) as session:
        prescriptions = session.exec(select(Prescription).order_by(Prescription.created_at.desc())).all()
        beneficiary_ids = {p.beneficiary_id for p in prescriptions}
        solution_ids = {p.solution_id for p in prescriptions}
        beneficiaries_map = {}
        if beneficiary_ids:
            for b in session.exec(select(Beneficiary).where(Beneficiary.id.in_(beneficiary_ids))).all():
                beneficiaries_map[b.id] = b
        solutions_map = {}
        if solution_ids:
            for s in session.exec(select(Solution).where(Solution.id.in_(solution_ids))).all():
                solutions_map[s.id] = s
        for p in prescriptions:
            p._beneficiary = beneficiaries_map.get(p.beneficiary_id)
            p._solution = solutions_map.get(p.solution_id)
    return _templates(request).TemplateResponse(
        "prescriptions_sent.html",
        {
            "request": request,
            "prescriptions": prescriptions,
        },
    )
