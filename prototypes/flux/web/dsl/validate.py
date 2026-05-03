"""Post-load validation: edge resolution and id-shape checks.

Pydantic ensures the YAML matches the schema. This module catches the things
Pydantic can't see: dangling FKs (``to: nonexistent_screen``), modals
referenced via ``to`` instead of ``opens``, duplicate ids, etc.

Errors here are appended to the diagnostics list; the model itself is left
untouched. Renderers should treat broken edges as inert links.
"""

from __future__ import annotations

import re

from .models import (
    Action,
    Box,
    Card,
    Dashboard,
    Diagnostic,
    FluxModel,
    KpiTile,
    Modal,
    Page,
    Search,
    Tab,
    Table,
)

_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def validate(model: FluxModel) -> list[Diagnostic]:
    """Walk the model, return cross-reference and id-shape diagnostics."""
    diags: list[Diagnostic] = []

    for flow_id, flow in model.flows.items():
        if not _ID_RE.match(flow_id):
            diags.append(_err(f"flow id '{flow_id}' must match {_ID_RE.pattern}", flow_id))

        if flow.actor not in model.actors:
            diags.append(_err(f"flow '{flow_id}': unknown actor '{flow.actor}'", flow_id))

        flow_screens = model.screens_in(flow_id)
        if flow.entry not in flow_screens:
            diags.append(_err(f"flow '{flow_id}': entry '{flow.entry}' is not a screen", flow_id))

        menu_ids = {item.id for item in flow.menu}

        for sid, screen in flow_screens.items():
            if not _ID_RE.match(sid):
                diags.append(_err(f"screen id '{sid}' must match {_ID_RE.pattern}", f"{flow_id}.{sid}"))
            if screen.nav_item is not None and screen.nav_item not in menu_ids:
                diags.append(
                    _err(
                        f"screen '{sid}': nav_item '{screen.nav_item}' not in flow '{flow_id}' menu",
                        f"{flow_id}.{sid}",
                    )
                )

            for action in screen.actions:
                _check_action(action, flow_id, flow_screens, sid, diags)

            if isinstance(screen, Page):
                if screen.prevstep_to is not None:
                    _check_screen_ref(
                        "prevstep_to",
                        screen.prevstep_to,
                        flow_id,
                        flow_screens,
                        sid,
                        diags,
                        allow_modal=False,
                    )
                for block in screen.body:
                    _check_block(block, flow_id, flow_screens, sid, diags)
                if screen.tabs:
                    for tid, tab in screen.tabs.items():
                        _check_tab(tid, tab, flow_id, flow_screens, sid, diags)

            elif isinstance(screen, Modal):
                for block in screen.body:
                    _check_block(block, flow_id, flow_screens, sid, diags)

            elif isinstance(screen, Dashboard):
                for block in screen.blocks:
                    _check_block(block, flow_id, flow_screens, sid, diags)

    return diags


def _err(message: str, path: str) -> Diagnostic:
    return Diagnostic(level="error", message=message, path=path)


def _check_action(
    action: Action,
    flow_id: str,
    flow_screens: dict,
    parent: str,
    diags: list[Diagnostic],
) -> None:
    if action.to is not None:
        target = flow_screens.get(action.to)
        if target is None:
            diags.append(
                _err(
                    f"action '{action.label}' on '{parent}': to '{action.to}' does not exist in flow '{flow_id}'",
                    f"{flow_id}.{parent}",
                )
            )
        elif isinstance(target, Modal):
            diags.append(
                _err(
                    f"action '{action.label}' on '{parent}': `to: {action.to}` targets a modal — use `opens:` instead",
                    f"{flow_id}.{parent}",
                )
            )
    if action.opens is not None:
        target = flow_screens.get(action.opens)
        if target is None:
            diags.append(
                _err(
                    f"action '{action.label}' on '{parent}': opens '{action.opens}' does not exist in flow '{flow_id}'",
                    f"{flow_id}.{parent}",
                )
            )
        elif not isinstance(target, Modal):
            diags.append(
                _err(
                    f"action '{action.label}' on '{parent}': "
                    f"`opens: {action.opens}` targets a {target.kind} — must be a modal",
                    f"{flow_id}.{parent}",
                )
            )


def _check_screen_ref(
    field: str,
    target_id: str,
    flow_id: str,
    flow_screens: dict,
    parent: str,
    diags: list[Diagnostic],
    *,
    allow_modal: bool = True,
) -> None:
    target = flow_screens.get(target_id)
    if target is None:
        diags.append(
            _err(
                f"{field} '{target_id}' on '{parent}': no such screen in flow '{flow_id}'",
                f"{flow_id}.{parent}",
            )
        )
    elif not allow_modal and isinstance(target, Modal):
        diags.append(
            _err(
                f"{field} '{target_id}' on '{parent}': cannot point at a modal",
                f"{flow_id}.{parent}",
            )
        )


def _check_block(block, flow_id, flow_screens, parent, diags):
    # Walk every screen-ref attribute on each block kind.
    if isinstance(block, Search) and block.to:
        _check_screen_ref("to", block.to, flow_id, flow_screens, parent, diags)
    elif isinstance(block, Table) and block.rows_to:
        _check_screen_ref("rows_to", block.rows_to, flow_id, flow_screens, parent, diags)
    elif isinstance(block, Box) and block.edit_to:
        _check_screen_ref("edit_to", block.edit_to, flow_id, flow_screens, parent, diags)
    elif isinstance(block, Card) and block.to:
        _check_screen_ref("to", block.to, flow_id, flow_screens, parent, diags)
    elif hasattr(block, "tiles"):  # KpiRow
        for tile in block.tiles:
            if isinstance(tile, KpiTile) and tile.to:
                _check_screen_ref("kpi to", tile.to, flow_id, flow_screens, parent, diags)


def _check_tab(
    tid: str,
    tab: Tab,
    flow_id: str,
    flow_screens: dict,
    parent: str,
    diags: list[Diagnostic],
) -> None:
    if not _ID_RE.match(tid):
        diags.append(
            _err(
                f"tab id '{tid}' on '{parent}' must match {_ID_RE.pattern}",
                f"{flow_id}.{parent}.{tid}",
            )
        )
    for target_id in tab.to:
        _check_screen_ref(f"tab '{tid}' to", target_id, flow_id, flow_screens, parent, diags)
