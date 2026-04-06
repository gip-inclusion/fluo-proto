import json

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from ..database import engine
from ..models import Beneficiary, Structure

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
        diagnostic = json.loads(b.diagnostic_data) if b.diagnostic_data else None
    return _templates(request).TemplateResponse(
        "beneficiary_detail.html",
        {
            "request": request,
            "b": b,
            "structure": structure,
            "diagnostic": diagnostic,
        },
    )
