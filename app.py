from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import init_db

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()


@app.get("/orientation/{orientation_id}", response_class=HTMLResponse)
async def orientation_detail(request: Request, orientation_id: int):
    return templates.TemplateResponse(
        "orientation_detail.html",
        {"request": request, "orientation_id": orientation_id},
    )
