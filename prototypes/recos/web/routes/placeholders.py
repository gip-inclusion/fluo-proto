from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


def _templates(request: Request):
    return request.app.state.templates


@router.get("/prescriptions-received", response_class=HTMLResponse)
async def prescriptions_received(request: Request):
    return _templates(request).TemplateResponse(
        request,
        "placeholder.html",
        {"page_title": "Demandes reçues"},
    )
