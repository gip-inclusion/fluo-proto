from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import (
    ELIGIBILITY_COLORS,
    MODALITE_LABELS,
    NAV_ITEMS,
    SERVICE_NAME,
    TAG_COLORS,
)
from .database import init_db
from .routes import beneficiaries_router, placeholders_router

_dir = Path(__file__).parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=_dir / "static"), name="static")

templates = Jinja2Templates(directory=_dir / "templates")
templates.env.globals.update(
    {
        "service_name": SERVICE_NAME,
        "modalite_labels": MODALITE_LABELS,
        "eligibility_colors": ELIGIBILITY_COLORS,
        "nav_items": NAV_ITEMS,
        "tag_colors": TAG_COLORS,
    }
)
templates.env.filters["format_datetime"] = lambda v: v[:16].replace("T", " à ") if v else ""
app.state.templates = templates

init_db()


@app.get("/")
async def root():
    return RedirectResponse("/dashboard", status_code=302)


app.include_router(beneficiaries_router)
app.include_router(placeholders_router)
