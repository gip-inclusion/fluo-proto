from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import init_db
from .routes import hello_router

_dir = Path(__file__).parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=_dir / "static"), name="static")

templates = Jinja2Templates(directory=_dir / "templates")
app.state.templates = templates

init_db()
app.include_router(hello_router)
