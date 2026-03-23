import json
from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from ..config import ALL_STATUSES, MODALITE_LABELS, SERVICE_NAME, STATUS_LABELS
from ..database import engine
from ..models import HistoryEvent, Message, Orientation, PlieBeneficiaire, SentOrientation

router = APIRouter()


def _templates(request: Request):
    """Get the Jinja2Templates instance from the app state."""
    return request.app.state.templates


def _prefix(request: Request) -> str:
    """Get the current scenario URL prefix (e.g. '/plie')."""
    scenario = request.state.scenario
    return f"/{scenario['slug']}" if scenario else ""


@router.get("/", response_class=HTMLResponse)
async def orientation_index(request: Request):
    return RedirectResponse(f"{_prefix(request)}/orientations", status_code=302)


@router.get("/orientations", response_class=HTMLResponse)
async def orientation_list(request: Request, status: list[str] = Query(default=None)):
    if not status:
        status = ALL_STATUSES
    with Session(engine) as session:
        statement = select(Orientation).where(Orientation.status.in_(status)).order_by(Orientation.created_at.desc())
        orientations = session.exec(statement).all()
    prefix = _prefix(request)
    return _templates(request).TemplateResponse(
        "orientation_list.html",
        {
            "request": request,
            "orientations": orientations,
            "active_filters": status,
            "all_statuses": ALL_STATUSES,
            "result_count": len(orientations),
            "prefix": prefix,
        },
    )


@router.get("/orientation/{orientation_id}", response_class=HTMLResponse)
async def orientation_detail(request: Request, orientation_id: int):
    with Session(engine) as session:
        orientation = session.get(Orientation, orientation_id)
        if not orientation:
            return HTMLResponse("Not found", status_code=404)
        messages = session.exec(
            select(Message).where(Message.orientation_id == orientation_id).order_by(Message.created_at.desc())
        ).all()
        history = session.exec(
            select(HistoryEvent).where(HistoryEvent.orientation_id == orientation_id).order_by(HistoryEvent.created_at)
        ).all()
        diagnostic_data = json.loads(orientation.diagnostic_data) if orientation.diagnostic_data else None
        status_label, status_class = STATUS_LABELS.get(orientation.status, ("Inconnu", "bg-secondary"))
    prefix = _prefix(request)
    # Link to PLIE beneficiaire if accepted
    plie_beneficiaire_url = None
    if orientation.status == "acceptee":
        with Session(engine) as session:
            pb = session.exec(select(PlieBeneficiaire).where(PlieBeneficiaire.orientation_id == orientation_id)).first()
            if pb:
                plie_beneficiaire_url = f"{prefix}/beneficiaire/{pb.id}"
    return _templates(request).TemplateResponse(
        "orientation_detail.html",
        {
            "request": request,
            "o": orientation,
            "o_diagnostic_data": diagnostic_data,
            "messages": messages,
            "history": history,
            "status_label": status_label,
            "status_class": status_class,
            "modalite_label": MODALITE_LABELS.get(orientation.modalite, orientation.modalite),
            "plie_beneficiaire_url": plie_beneficiaire_url,
            "prefix": prefix,
        },
    )


@router.post("/orientation/{orientation_id}/accept")
async def accept_orientation(request: Request, orientation_id: int):
    form = await request.form()
    now = datetime.now().isoformat()
    prefix = _prefix(request)
    response_msg = (form.get("response_message") or "").strip() or None
    recipient = (form.get("recipient_name") or "").strip() or None
    with Session(engine) as session:
        orientation = session.get(Orientation, orientation_id)
        if orientation:
            orientation.status = "acceptee"
            session.add(HistoryEvent(orientation_id=orientation.id, event_type="accepted", created_at=now))
            # Sync to the prescripteur's sent orientation
            linked = session.exec(
                select(SentOrientation).where(SentOrientation.orientation_id == orientation.id)
            ).first()
            if linked:
                linked.status = "acceptee"
                linked.recipient_name = recipient
                linked.response_message = response_msg
            # Create a PLIE beneficiaire if not already existing
            existing_pb = session.exec(
                select(PlieBeneficiaire).where(PlieBeneficiaire.orientation_id == orientation.id)
            ).first()
            if not existing_pb:
                session.add(
                    PlieBeneficiaire(
                        orientation_id=orientation.id,
                        person_first_name=orientation.person_first_name,
                        person_last_name=orientation.person_last_name,
                        person_phone=orientation.person_phone,
                        person_email=orientation.person_email,
                        person_birthdate=orientation.person_birthdate,
                        person_address=orientation.person_address,
                        accompagnateur=recipient,
                        date_entree=now[:10],
                        diagnostic_data=orientation.diagnostic_data,
                    )
                )
            session.commit()
            return RedirectResponse(f"{prefix}/orientation/{orientation.id}", status_code=303)
    return RedirectResponse(f"{prefix}/orientations", status_code=303)


@router.post("/orientation/{orientation_id}/refuse")
async def refuse_orientation(request: Request, orientation_id: int):
    form = await request.form()
    now = datetime.now().isoformat()
    prefix = _prefix(request)
    response_msg = (form.get("response_message") or "").strip() or None
    with Session(engine) as session:
        orientation = session.get(Orientation, orientation_id)
        if orientation:
            orientation.status = "refusee"
            session.add(HistoryEvent(orientation_id=orientation.id, event_type="refused", created_at=now))
            # Sync to the prescripteur's sent orientation
            linked = session.exec(
                select(SentOrientation).where(SentOrientation.orientation_id == orientation.id)
            ).first()
            if linked:
                linked.status = "refusee"
                linked.response_message = response_msg
            session.commit()
            return RedirectResponse(f"{prefix}/orientation/{orientation.id}", status_code=303)
    return RedirectResponse(f"{prefix}/orientations", status_code=303)


@router.post("/orientation/{orientation_id}/message")
async def post_message(request: Request, orientation_id: int):
    form = await request.form()
    content = form.get("content", "").strip()
    author = form.get("author_name", SERVICE_NAME)
    source = form.get("source", "")
    if content:
        now = datetime.now().isoformat()
        with Session(engine) as session:
            # Also link to beneficiaire so messages appear on prescripteur side
            beneficiaire_id = None
            linked = session.exec(
                select(SentOrientation).where(SentOrientation.orientation_id == orientation_id)
            ).first()
            if linked:
                beneficiaire_id = linked.beneficiaire_id
            session.add(
                Message(
                    orientation_id=orientation_id,
                    beneficiaire_id=beneficiaire_id,
                    author_name=author,
                    content=content,
                    created_at=now,
                )
            )
            session.commit()
    prefix = _prefix(request)
    oid = int(orientation_id)
    redirect_map = {
        "orienteur": f"{prefix}/orientation/{oid}/orienteur",
        "messages": f"{prefix}/orientation/{oid}#messages",
    }
    return RedirectResponse(redirect_map.get(source, f"{prefix}/orientation/{oid}"), status_code=303)


@router.get("/orientation/{orientation_id}/orienteur", response_class=HTMLResponse)
async def orienteur_reply(request: Request, orientation_id: int):
    with Session(engine) as session:
        orientation = session.get(Orientation, orientation_id)
        if not orientation:
            return HTMLResponse("Not found", status_code=404)
        messages = session.exec(
            select(Message).where(Message.orientation_id == orientation_id).order_by(Message.created_at.desc())
        ).all()
        status_label, status_class = STATUS_LABELS.get(orientation.status, ("Inconnu", "bg-secondary"))
    prefix = _prefix(request)
    return _templates(request).TemplateResponse(
        "orienteur_reply.html",
        {
            "request": request,
            "o": orientation,
            "messages": messages,
            "status_label": status_label,
            "status_class": status_class,
            "prefix": prefix,
        },
    )


@router.get("/beneficiaires", response_class=HTMLResponse)
async def plie_beneficiaires_list(request: Request):
    with Session(engine) as session:
        beneficiaires = session.exec(select(PlieBeneficiaire).order_by(PlieBeneficiaire.person_last_name)).all()
    prefix = _prefix(request)
    return _templates(request).TemplateResponse(
        "beneficiaire_list.html",
        {
            "request": request,
            "beneficiaires": beneficiaires,
            "result_count": len(beneficiaires),
            "prefix": prefix,
        },
    )


@router.get("/beneficiaire/{beneficiaire_id}", response_class=HTMLResponse)
async def plie_beneficiaire_detail(request: Request, beneficiaire_id: int):
    with Session(engine) as session:
        pb = session.get(PlieBeneficiaire, beneficiaire_id)
        if not pb:
            return HTMLResponse("Not found", status_code=404)
        diagnostic_data = json.loads(pb.diagnostic_data) if pb.diagnostic_data else None
        # Get linked orientation if any
        orientation = session.get(Orientation, pb.orientation_id) if pb.orientation_id else None
        # Messages linked to the orientation
        messages = []
        if pb.orientation_id:
            messages = session.exec(
                select(Message).where(Message.orientation_id == pb.orientation_id).order_by(Message.created_at.desc())
            ).all()
    prefix = _prefix(request)
    return _templates(request).TemplateResponse(
        "beneficiaire_detail.html",
        {
            "request": request,
            "o": pb,
            "o_diagnostic_data": diagnostic_data,
            "orientation": orientation,
            "messages": messages,
            "message_post_url": f"{prefix}/orientation/{pb.orientation_id}/message" if pb.orientation_id else None,
            "prefix": prefix,
        },
    )
