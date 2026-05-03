from collections import defaultdict

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/_diagnostics", response_class=HTMLResponse)
async def diagnostics_page(request: Request):
    state = request.app.state
    grouped: dict[str, list] = defaultdict(list)
    for d in state.diagnostics:
        grouped[d.file or "(unknown)"].append(d)
    return state.templates.TemplateResponse(
        request,
        "diagnostics.html",
        {
            "diagnostics": state.diagnostics,
            "grouped": dict(grouped),
        },
    )
