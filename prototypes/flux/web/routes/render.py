from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..dsl.models import Modal

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    state = request.app.state
    if not state.flux_model.flows:
        return state.templates.TemplateResponse(
            request,
            "empty.html",
            {"diagnostics": state.diagnostics},
        )
    flow_id, flow = next(iter(state.flux_model.flows.items()))
    return RedirectResponse(url=f"/{flow_id}/{flow.entry}")


@router.get("/{flow_id}/{screen_id}", response_class=HTMLResponse)
async def render_screen(flow_id: str, screen_id: str, request: Request):
    state = request.app.state
    model = state.flux_model
    flow = model.flows.get(flow_id)
    if flow is None:
        raise HTTPException(404, f"unknown flow '{flow_id}'")

    screen = model.screen(flow_id, screen_id)
    if screen is None:
        raise HTTPException(404, f"unknown screen '{screen_id}' in flow '{flow_id}'")

    # Modals are not addressable on their own — bounce to the flow entry.
    if isinstance(screen, Modal):
        return RedirectResponse(url=f"/{flow_id}/{flow.entry}")

    actor = model.actors.get(flow.actor)
    flow_screens = model.screens_in(flow_id)

    # Modals to inline on this page (those referenced by any `opens:` action).
    referenced_modals: dict[str, Modal] = {}
    for action in screen.actions:
        if action.opens:
            target = flow_screens.get(action.opens)
            if isinstance(target, Modal):
                referenced_modals[action.opens] = target

    template = f"archetypes/{screen.kind}.html"
    return state.templates.TemplateResponse(
        request,
        template,
        {
            "flow": flow,
            "screen": screen,
            "screen_id": screen_id,
            "actor": actor,
            "modals": referenced_modals,
            "flow_screens": flow_screens,
            "diagnostics": state.diagnostics,
        },
    )
