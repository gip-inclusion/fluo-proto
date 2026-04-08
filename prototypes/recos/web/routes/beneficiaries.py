import json
from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from ..database import engine
from ..matching import compute_recommendations, get_services_for_beneficiary
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


@router.get("/beneficiaries", response_class=HTMLResponse)
async def list_beneficiaries(request: Request):
    with Session(engine) as session:
        beneficiaries = session.exec(select(Beneficiary).order_by(Beneficiary.person_last_name)).all()
        # Eagerly load structure names for display
        structure_ids = [b.structure_referente_id for b in beneficiaries if b.structure_referente_id]
        structures = {}
        if structure_ids:
            for s in session.exec(select(Structure).where(Structure.id.in_(structure_ids))).all():
                structures[s.id] = s
        # Parse eligibilites JSON for each beneficiary
        for b in beneficiaries:
            b._eligibility_list = json.loads(b.eligibilites) if b.eligibilites else []
            b._structure = structures.get(b.structure_referente_id)
    return _templates(request).TemplateResponse(
        "beneficiary_list.html",
        {
            "request": request,
            "beneficiaries": beneficiaries,
            "result_count": len(beneficiaries),
        },
    )


@router.get("/beneficiary/{id}", response_class=HTMLResponse)
async def detail_beneficiary(request: Request, id: int):
    with Session(engine) as session:
        b = session.get(Beneficiary, id)
        if not b:
            return HTMLResponse("Not found", status_code=404)
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
