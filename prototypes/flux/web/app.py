"""Flux entrypoint.

Loads the YAML model on startup, makes it available on ``app.state``, and
mounts the render/graph/diagnostics routers. In dev, ``watchfiles`` reloads
the model whenever ``flows/`` changes and SSE pings connected browsers.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import FLOWS_DIR
from .dsl import load
from .dsl.models import Flow, FluxModel
from .dsl.validate import validate
from .routes import diagnostics_router, graph_router, render_router

_dir = Path(__file__).parent


def _reload_model(app: FastAPI) -> None:
    model, parse_diags = load(FLOWS_DIR)
    edge_diags = validate(model)
    app.state.flux_model = model
    app.state.diagnostics = parse_diags + edge_diags


async def _watch_flows(app: FastAPI) -> None:
    from watchfiles import awatch

    async for _ in awatch(str(FLOWS_DIR)):
        _reload_model(app)
        # Notify any SSE listeners.
        for queue in list(app.state.reload_listeners):
            try:
                queue.put_nowait("reload")
            except asyncio.QueueFull:
                pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.reload_listeners = set()
    _reload_model(app)
    watcher = None
    if FLOWS_DIR.exists():
        watcher = asyncio.create_task(_watch_flows(app))
    try:
        yield
    finally:
        if watcher:
            watcher.cancel()


def _resolve_menu_href(flow: Flow, menu_item_id: str) -> str | None:
    """Find the first screen in ``flow`` whose ``nav_item`` matches.

    Used by the offcanvas template so that clicking a menu entry lands on
    a real screen rather than being dead.
    """
    model: FluxModel = app.state.flux_model
    for (fid, sid), screen in model.screens.items():
        if fid == flow.id and screen.nav_item == menu_item_id:
            return sid
    return None


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=_dir / "static"), name="static")

templates = Jinja2Templates(directory=_dir / "templates")
templates.env.globals["resolve_menu_href"] = _resolve_menu_href
app.state.templates = templates

# Graph + diagnostics routes use literal `_graph` / `_diagnostics` prefixes
# which would otherwise be shadowed by the catch-all `/{flow_id}/{screen_id}`
# in render_router. Register the literal routes first.
app.include_router(graph_router)
app.include_router(diagnostics_router)
app.include_router(render_router)


@app.get("/_reload")
async def reload_stream():
    """SSE channel: emits ``reload`` whenever flows/ changes."""

    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=8)
    app.state.reload_listeners.add(queue)

    async def gen():
        try:
            yield "retry: 2000\n\n"
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"data: {msg}\n\n"
                except TimeoutError:
                    yield ": ping\n\n"
        finally:
            app.state.reload_listeners.discard(queue)

    return StreamingResponse(gen(), media_type="text/event-stream")
