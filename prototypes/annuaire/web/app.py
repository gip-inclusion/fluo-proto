from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import (
    CONTACT_MEANS,
    MESSAGE_SUBJECTS,
    NAV_ITEMS,
    RDV_SUBJECTS,
    RDV_TYPES,
    SERVICE_NAME,
    STRUCTURE_TYPE_COLORS,
    STRUCTURE_TYPES,
)
from .database import init_db
from .routes import directory_router, profile_router

_dir = Path(__file__).parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=_dir / "static"), name="static")

templates = Jinja2Templates(directory=_dir / "templates")
templates.env.globals.update(
    {
        "service_name": SERVICE_NAME,
        "nav_items": NAV_ITEMS,
        "structure_type_colors": STRUCTURE_TYPE_COLORS,
        "structure_types": STRUCTURE_TYPES,
        "contact_means": CONTACT_MEANS,
        "message_subjects": MESSAGE_SUBJECTS,
        "rdv_subjects": RDV_SUBJECTS,
        "rdv_types": RDV_TYPES,
    }
)
app.state.templates = templates

init_db()


@app.get("/")
async def root():
    return RedirectResponse("/annuaire", status_code=302)


app.include_router(directory_router)
app.include_router(profile_router)
