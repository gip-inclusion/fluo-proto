from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from .config import (
    EVENT_LABELS,
    MODALITE_FT_LABELS,
    MODALITE_LABELS,
    SCENARIOS,
    SENT_STATUS_LABELS,
    SERVICE_NAME,
    STATUS_LABELS,
)
from .database import init_db
from .routes import orientations_router
from .routes.prescripteur import router as prescripteur_router

_dir = Path(__file__).parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=_dir / "static"), name="static")

templates = Jinja2Templates(directory=_dir / "templates")
templates.env.globals.update(
    {
        "service_name": SERVICE_NAME,
        "status_labels": STATUS_LABELS,
        "event_labels": EVENT_LABELS,
        "modalite_labels": MODALITE_LABELS,
        "modalite_ft_labels": MODALITE_FT_LABELS,
        "scenarios": SCENARIOS,
        "sent_status_labels": SENT_STATUS_LABELS,
    }
)
templates.env.filters["format_datetime"] = lambda v: v[:16].replace("T", " à ") if v else ""
app.state.templates = templates


class ScenarioMiddleware(BaseHTTPMiddleware):
    """Set request.state.scenario based on URL prefix."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        request.state.scenario = None
        for slug, scenario in SCENARIOS.items():
            if path.startswith(f"/{slug}/") or path == f"/{slug}":
                request.state.scenario = scenario
                break
        return await call_next(request)


app.add_middleware(ScenarioMiddleware)

init_db()


@app.get("/")
async def root():
    return RedirectResponse("/plie/orientations", status_code=302)


app.include_router(orientations_router, prefix="/plie")
app.include_router(prescripteur_router, prefix="/prescripteur")
