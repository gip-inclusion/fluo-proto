import json
from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from ..config import ALL_SENT_STATUSES, SENT_STATUS_LABELS
from ..database import engine
from ..models import Beneficiaire, HistoryEvent, Message, Orientation, SentOrientation
from ..solutions import SOLUTIONS, compute_age, filter_solutions

router = APIRouter()


PREFIX = "/prescripteur"


def _templates(request: Request):
    return request.app.state.templates


@router.get("/", response_class=HTMLResponse)
async def prescripteur_index():
    return RedirectResponse(f"{PREFIX}/beneficiaires", status_code=302)


@router.get("/beneficiaires", response_class=HTMLResponse)
async def beneficiaires_list(request: Request):
    with Session(engine) as session:
        beneficiaires = session.exec(select(Beneficiaire).order_by(Beneficiaire.person_last_name)).all()
    return _templates(request).TemplateResponse(
        "prescripteur/beneficiaires.html",
        {
            "request": request,
            "beneficiaires": beneficiaires,
            "result_count": len(beneficiaires),
            "prefix": PREFIX,
        },
    )


@router.get("/beneficiaire/{beneficiaire_id}", response_class=HTMLResponse)
async def beneficiaire_detail(request: Request, beneficiaire_id: int):
    with Session(engine) as session:
        b = session.get(Beneficiaire, beneficiaire_id)
        if not b:
            return HTMLResponse("Not found", status_code=404)
        messages = session.exec(
            select(Message).where(Message.beneficiaire_id == beneficiaire_id).order_by(Message.created_at.desc())
        ).all()
        sent_orientations = session.exec(
            select(SentOrientation)
            .where(SentOrientation.beneficiaire_id == beneficiaire_id)
            .order_by(SentOrientation.created_at.desc())
        ).all()
        diagnostic_data = json.loads(b.diagnostic_data) if b.diagnostic_data else None
    return _templates(request).TemplateResponse(
        "prescripteur/beneficiaire_detail.html",
        {
            "request": request,
            "o": b,
            "o_diagnostic_data": diagnostic_data,
            "messages": messages,
            "sent_orientations": sent_orientations,
            "message_post_url": f"{PREFIX}/beneficiaire/{beneficiaire_id}/message",
            "prefix": PREFIX,
        },
    )


@router.get("/beneficiaire/{beneficiaire_id}/orienter", response_class=HTMLResponse)
async def orienter(request: Request, beneficiaire_id: int):
    with Session(engine) as session:
        b = session.get(Beneficiaire, beneficiaire_id)
        if not b:
            return HTMLResponse("Not found", status_code=404)
        diagnostic_data = json.loads(b.diagnostic_data) if b.diagnostic_data else None

    age = compute_age(b.person_birthdate)
    projet_pro = ""
    if diagnostic_data and diagnostic_data.get("projet_professionnel", {}).get("nom_metier"):
        projet_pro = diagnostic_data["projet_professionnel"]["nom_metier"]

    contraintes = [c["libelle"] for c in (diagnostic_data or {}).get("contraintes", []) if c.get("est_prioritaire")]

    return _templates(request).TemplateResponse(
        "prescripteur/orienter.html",
        {
            "request": request,
            "o": b,
            "o_diagnostic_data": diagnostic_data,
            "age": age,
            "projet_pro": projet_pro,
            "contraintes": contraintes,
            "solutions": filter_solutions(SOLUTIONS, age, b.modalite_ft),
            "prefix": PREFIX,
        },
    )


@router.post("/beneficiaire/{beneficiaire_id}/orienter")
async def post_orienter(request: Request, beneficiaire_id: int):
    form = await request.form()
    now = datetime.now().isoformat()
    structure_key = (form.get("structure_key") or "").strip()
    msg = (form.get("message") or "").strip() or None
    with Session(engine) as session:
        b = session.get(Beneficiaire, beneficiaire_id)
        # Create the sent orientation
        so = SentOrientation(
            beneficiaire_id=beneficiaire_id,
            structure_name=(form.get("structure_name") or "").strip(),
            structure_key=structure_key,
            solution_title=(form.get("solution_title") or "").strip(),
            poste_titre=(form.get("poste_titre") or "").strip() or None,
            message=msg,
            created_at=now,
        )
        # If sending to PLIE, also create an Orientation visible on the PLIE side
        if structure_key == "plie" and b:
            o = Orientation(
                status="nouvelle",
                created_at=now,
                person_first_name=b.person_first_name,
                person_last_name=b.person_last_name,
                person_phone=b.person_phone,
                person_email=b.person_email,
                person_birthdate=b.person_birthdate,
                person_address=b.person_address,
                sender_name=b.referent_name,
                sender_type="prescripteur",
                sender_organization="France Travail Lille",
                sender_message=msg,
                modalite="accompagnement_emploi",
                diagnostic_data=b.diagnostic_data,
            )
            session.add(o)
            session.flush()
            so.orientation_id = o.id
            session.add(HistoryEvent(orientation_id=o.id, event_type="created", created_at=now))
        session.add(so)
        session.commit()
        session.refresh(so)
    return RedirectResponse(f"{PREFIX}/orientation/{so.id}", status_code=303)


@router.post("/beneficiaire/{beneficiaire_id}/message")
async def post_beneficiaire_message(request: Request, beneficiaire_id: int):
    form = await request.form()
    content = form.get("content", "").strip()
    author = form.get("author_name", "France Travail Lille").strip()
    if content:
        now = datetime.now().isoformat()
        with Session(engine) as session:
            # Also link to orientation so messages appear on PLIE side
            orientation_id = None
            linked = session.exec(
                select(SentOrientation).where(
                    SentOrientation.beneficiaire_id == beneficiaire_id,
                    SentOrientation.orientation_id.is_not(None),
                )
            ).first()
            if linked:
                orientation_id = linked.orientation_id
            session.add(
                Message(
                    beneficiaire_id=beneficiaire_id,
                    orientation_id=orientation_id,
                    author_name=author,
                    content=content,
                    created_at=now,
                )
            )
            session.commit()
    referer = request.headers.get("referer", "")
    redirect = referer if referer else f"{PREFIX}/beneficiaire/{beneficiaire_id}"
    return RedirectResponse(redirect, status_code=303)


@router.get("/orientations", response_class=HTMLResponse)
async def orientations_envoyees(request: Request, status: list[str] = Query(default=None)):
    if not status:
        status = list(ALL_SENT_STATUSES)
    with Session(engine) as session:
        results = session.exec(
            select(SentOrientation, Beneficiaire)
            .join(Beneficiaire, SentOrientation.beneficiaire_id == Beneficiaire.id)
            .where(SentOrientation.status.in_(status))
            .order_by(SentOrientation.created_at.desc())
        ).all()
    return _templates(request).TemplateResponse(
        "prescripteur/orientations_envoyees.html",
        {
            "request": request,
            "orientations": results,
            "active_filters": status,
            "all_sent_statuses": ALL_SENT_STATUSES,
            "result_count": len(results),
            "prefix": PREFIX,
        },
    )


@router.get("/orientation/{orientation_id}", response_class=HTMLResponse)
async def sent_orientation_detail(request: Request, orientation_id: int):
    with Session(engine) as session:
        so = session.get(SentOrientation, orientation_id)
        if not so:
            return HTMLResponse("Not found", status_code=404)
        b = session.get(Beneficiaire, so.beneficiaire_id)
        diagnostic_data = json.loads(b.diagnostic_data) if b and b.diagnostic_data else None
        messages = session.exec(
            select(Message).where(Message.beneficiaire_id == so.beneficiaire_id).order_by(Message.created_at.desc())
        ).all()
    structure_info = None
    for group in SOLUTIONS:
        if group["key"] == so.structure_key:
            for s in group["structures"]:
                if s["name"] == so.structure_name:
                    structure_info = s
                    break
            break
    status_label, status_class = SENT_STATUS_LABELS.get(so.status, ("Inconnu", "bg-secondary"))
    return _templates(request).TemplateResponse(
        "prescripteur/orientation_detail.html",
        {
            "request": request,
            "so": so,
            "o": b,
            "o_diagnostic_data": diagnostic_data,
            "structure_info": structure_info,
            "status_label": status_label,
            "status_class": status_class,
            "messages": messages,
            "message_post_url": f"{PREFIX}/beneficiaire/{so.beneficiaire_id}/message",
            "beneficiaire_url": f"{PREFIX}/beneficiaire/{so.beneficiaire_id}",
            "prefix": PREFIX,
        },
    )
