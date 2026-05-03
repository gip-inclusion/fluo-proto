from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from ..dsl import graph as graph_emitter

router = APIRouter()


@router.get("/_graph", response_class=HTMLResponse)
async def graph_all(request: Request):
    state = request.app.state
    sources = {flow_id: graph_emitter.emit(state.flux_model, only_flow=flow_id) for flow_id in state.flux_model.flows}
    return state.templates.TemplateResponse(
        request,
        "graph.html",
        {
            "sources": sources,
            "single": False,
            "diagnostics": state.diagnostics,
        },
    )


@router.get("/_graph/{flow_id}", response_class=HTMLResponse)
async def graph_flow(flow_id: str, request: Request):
    state = request.app.state
    if flow_id not in state.flux_model.flows:
        raise HTTPException(404, f"unknown flow '{flow_id}'")
    sources = {flow_id: graph_emitter.emit(state.flux_model, only_flow=flow_id)}
    return state.templates.TemplateResponse(
        request,
        "graph.html",
        {
            "sources": sources,
            "single": True,
            "diagnostics": state.diagnostics,
        },
    )
