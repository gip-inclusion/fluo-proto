import json
from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from config import ALL_STATUSES, MODALITE_LABELS, SERVICE_NAME, STATUS_LABELS
from database import engine
from models import HistoryEvent, Message, Orientation

router = APIRouter()


def _templates(request: Request):
    """Get the Jinja2Templates instance from the app state."""
    return request.app.state.templates


@router.get("/", response_class=HTMLResponse)
async def orientation_list(request: Request, status: list[str] = Query(default=["nouvelle"])):
    if not status:
        status = ["nouvelle"]
    with Session(engine) as session:
        statement = select(Orientation).where(Orientation.status.in_(status)).order_by(Orientation.created_at.desc())
        orientations = session.exec(statement).all()
    return _templates(request).TemplateResponse(
        "orientation_list.html",
        {
            "request": request,
            "orientations": orientations,
            "active_filters": status,
            "all_statuses": ALL_STATUSES,
            "result_count": len(orientations),
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
        },
    )


@router.post("/orientation/{orientation_id}/accept")
async def accept_orientation(orientation_id: int):
    now = datetime.now().isoformat()
    with Session(engine) as session:
        orientation = session.get(Orientation, orientation_id)
        if orientation:
            orientation.status = "acceptee"
            session.add(HistoryEvent(orientation_id=orientation_id, event_type="accepted", created_at=now))
            session.commit()
    return RedirectResponse(f"/orientation/{orientation_id}", status_code=303)


@router.post("/orientation/{orientation_id}/refuse")
async def refuse_orientation(orientation_id: int):
    now = datetime.now().isoformat()
    with Session(engine) as session:
        orientation = session.get(Orientation, orientation_id)
        if orientation:
            orientation.status = "refusee"
            session.add(HistoryEvent(orientation_id=orientation_id, event_type="refused", created_at=now))
            session.commit()
    return RedirectResponse(f"/orientation/{orientation_id}", status_code=303)


@router.post("/orientation/{orientation_id}/message")
async def post_message(request: Request, orientation_id: int):
    form = await request.form()
    content = form.get("content", "").strip()
    author = form.get("author_name", SERVICE_NAME)
    redirect_to = form.get("redirect_to", f"/orientation/{orientation_id}")
    if content:
        now = datetime.now().isoformat()
        with Session(engine) as session:
            session.add(Message(orientation_id=orientation_id, author_name=author, content=content, created_at=now))
            session.commit()
    return RedirectResponse(redirect_to, status_code=303)


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
    return _templates(request).TemplateResponse(
        "orienteur_reply.html",
        {
            "request": request,
            "o": orientation,
            "messages": messages,
            "status_label": status_label,
            "status_class": status_class,
        },
    )
