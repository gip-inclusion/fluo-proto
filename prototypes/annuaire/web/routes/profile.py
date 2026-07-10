from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from ..config import CURRENT_PROFESSIONAL_ID, SHARE_AUDIENCES, SHARE_INFO_OPTIONS
from ..database import engine
from ..models import Professional, Structure

router = APIRouter()


@router.get("/mon-espace/profil", response_class=HTMLResponse)
async def edit_profile(request: Request):
    with Session(engine) as session:
        me = session.get(Professional, CURRENT_PROFESSIONAL_ID)
        if not me:
            return HTMLResponse("Not found", status_code=404)
        structure = session.get(Structure, me.structure_id) if me.structure_id else None
        structures = session.exec(select(Structure).order_by(Structure.name)).all()
    return request.app.state.templates.TemplateResponse(
        request,
        "profile.html",
        {
            "me": me,
            "structure": structure,
            "structures": structures,
            "share_info_options": SHARE_INFO_OPTIONS,
            "share_audiences": SHARE_AUDIENCES,
        },
    )
