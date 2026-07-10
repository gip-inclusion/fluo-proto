from datetime import date, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from ..config import CONTACT_MEANS_LABELS, STRUCTURE_TYPES, WEEKDAYS
from ..database import engine
from ..models import Professional, Structure

router = APIRouter()

# Candidate slots drawn from deterministically per professional so the agenda is
# stable between requests without any persistence.
_SLOT_POOL = ["09:00", "09:30", "10:00", "11:00", "11:30", "14:00", "14:30", "15:30", "16:30", "17:00"]


def _templates(request: Request):
    return request.app.state.templates


def _contact_means(obj) -> list[dict]:
    """Available contact means for a professional or structure, as icon dicts."""
    means = []
    for key in ("phone", "email", "form", "agenda"):
        available = getattr(obj, key, None) if key in ("phone", "email") else getattr(obj, f"has_{key}", False)
        if available:
            label, icon = CONTACT_MEANS_LABELS[key]
            means.append({"key": key, "label": label, "icon": icon})
    return means


def _week_slots(prof: Professional) -> list[dict]:
    """Deterministic Monday–Friday availability for the current week."""
    if not prof.has_agenda:
        return []
    monday = date.today() - timedelta(days=date.today().weekday())
    days = []
    for offset, weekday in enumerate(WEEKDAYS):
        day = monday + timedelta(days=offset)
        # Vary the picks by professional id and weekday; some days stay empty.
        seed = (prof.id or 0) * 7 + offset
        if seed % 5 == 2:
            slots = []
        else:
            picks = [_SLOT_POOL[i] for i in range(len(_SLOT_POOL)) if (i + seed) % 3 == 0]
            slots = picks[:3]
        days.append(
            {
                "weekday": weekday,
                "day_label": f"{day.day:02d}/{day.month:02d}",
                "slots": slots,
            }
        )
    return days


@router.get("/annuaire", response_class=HTMLResponse)
async def directory(request: Request):
    q = (request.query_params.get("q") or "").strip()
    q_lower = q.lower()
    selected_types = [t for t in request.query_params.getlist("type") if t in STRUCTURE_TYPES]
    selected_contacts = [c for c in request.query_params.getlist("contact") if c in CONTACT_MEANS_LABELS]
    tab = request.query_params.get("tab")
    active_tab = tab if tab in ("personnes", "structures") else "personnes"

    with Session(engine) as session:
        structures = session.exec(select(Structure).order_by(Structure.name)).all()
        structures_by_id = {s.id: s for s in structures}
        professionals = session.exec(
            select(Professional).order_by(Professional.last_name, Professional.first_name)
        ).all()

    for p in professionals:
        p._structure = structures_by_id.get(p.structure_id)
        p._means = _contact_means(p)
        p._mean_keys = {m["key"] for m in p._means}
        p._week_slots = _week_slots(p)

    for s in structures:
        s._means = _contact_means(s)

    # --- Personnes tab: filter professionals ---
    people = professionals
    if selected_types:
        people = [p for p in people if p._structure and p._structure.type in selected_types]
    if selected_contacts:
        people = [p for p in people if all(c in p._mean_keys for c in selected_contacts)]
    if q_lower:
        people = [
            p
            for p in people
            if q_lower in f"{p.first_name} {p.last_name}".lower()
            or q_lower in p.role.lower()
            or (p._structure and q_lower in p._structure.name.lower())
            or (p._structure and q_lower in p._structure.city.lower())
        ]

    # --- Structures tab: filter structures, attach their contacts ---
    structs = structures
    if selected_types:
        structs = [s for s in structs if s.type in selected_types]
    if q_lower:
        structs = [
            s for s in structs if q_lower in s.name.lower() or q_lower in s.type.lower() or q_lower in s.city.lower()
        ]
    contacts_by_structure = {s.id: [] for s in structs}
    for p in professionals:
        if p.structure_id in contacts_by_structure:
            contacts_by_structure[p.structure_id].append(p)

    return _templates(request).TemplateResponse(
        request,
        "directory.html",
        {
            "people": people,
            "structures": structs,
            "all_professionals": professionals,
            "contacts_by_structure": contacts_by_structure,
            "people_count": len(people),
            "structures_count": len(structs),
            "q": q,
            "selected_types": selected_types,
            "selected_contacts": selected_contacts,
            "active_tab": active_tab,
        },
    )
