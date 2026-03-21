from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import EVENT_LABELS, MODALITE_LABELS, SERVICE_NAME, STATUS_LABELS
from database import init_db
from routes import orientations_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.globals.update({
    "service_name": SERVICE_NAME,
    "status_labels": STATUS_LABELS,
    "event_labels": EVENT_LABELS,
    "modalite_labels": MODALITE_LABELS,
})
templates.env.filters["format_datetime"] = lambda v: v[:16].replace("T", " à ") if v else ""
app.state.templates = templates

init_db()
app.include_router(orientations_router)
