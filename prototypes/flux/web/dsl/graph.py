"""Emit Mermaid ``flowchart LR`` source from a :class:`FluxModel`.

Rendered client-side via mermaid.js. Each node carries a ``click`` directive
pointing at ``/<flow_id>/<screen_id>`` so the graph doubles as a navigator.
"""

from __future__ import annotations

from .models import (
    Card,
    Dashboard,
    FluxModel,
    KpiRow,
    Modal,
    Page,
    Search,
    Table,
)


def emit(model: FluxModel, only_flow: str | None = None) -> str:
    lines: list[str] = ["flowchart LR"]
    flows = {only_flow: model.flows[only_flow]} if only_flow and only_flow in model.flows else model.flows

    for flow_id, flow in flows.items():
        lines.append(f"  subgraph {_safe(flow_id)}[{_q(flow.id)}]")
        lines.append("    direction LR")

        flow_screens = model.screens_in(flow_id)
        for sid, screen in flow_screens.items():
            node = _screen_node(flow_id, sid, screen)
            lines.append(f"    {node}")
            lines.append(f'    click {_node_id(flow_id, sid)} "/{flow_id}/{sid}" "Voir l\'écran" _self')

            if isinstance(screen, Page) and screen.tabs:
                for tid, tab in screen.tabs.items():
                    tab_node = _node_id(flow_id, sid) + "__" + tid
                    lines.append(f"    {tab_node}([{_q('# ' + tab.label)}])")

        lines.append("  end")

        # Edges
        for sid, screen in flow_screens.items():
            src = _node_id(flow_id, sid)
            for action in screen.actions:
                if action.to:
                    lines.append(_edge(src, _node_id(flow_id, action.to), action.label))
                elif action.opens:
                    lines.append(_edge(src, _node_id(flow_id, action.opens), action.label))

            if isinstance(screen, Page):
                if screen.prevstep_to:
                    lines.append(_edge(src, _node_id(flow_id, screen.prevstep_to), "← retour"))
                for block in screen.body:
                    _edges_from_block(block, src, flow_id, lines)
                if screen.tabs:
                    for tid, tab in screen.tabs.items():
                        tab_node = src + "__" + tid
                        lines.append(_edge(src, tab_node, ""))
                        for target in tab.to:
                            lines.append(_edge(tab_node, _node_id(flow_id, target), target))
            elif isinstance(screen, (Modal, Dashboard)):
                blocks = screen.body if isinstance(screen, Modal) else screen.blocks
                for block in blocks:
                    _edges_from_block(block, src, flow_id, lines)

    return "\n".join(lines)


def _edges_from_block(block, src: str, flow_id: str, lines: list[str]) -> None:
    if isinstance(block, Search) and block.to:
        lines.append(_edge(src, _node_id(flow_id, block.to), "🔍"))
    elif isinstance(block, Table) and block.rows_to:
        lines.append(_edge(src, _node_id(flow_id, block.rows_to), "row"))
    elif isinstance(block, Card) and block.to:
        lines.append(_edge(src, _node_id(flow_id, block.to), "voir tout"))
    elif isinstance(block, KpiRow):
        for tile in block.tiles:
            if tile.to:
                lines.append(_edge(src, _node_id(flow_id, tile.to), tile.label))


def _screen_node(flow_id: str, sid: str, screen) -> str:
    nid = _node_id(flow_id, sid)
    label = _q(screen.title or sid)
    if isinstance(screen, Modal):
        return f"{nid}{{{{{label}}}}}"
    if isinstance(screen, Dashboard):
        return f"{nid}({label})"
    return f"{nid}[{label}]"


def _node_id(flow_id: str, sid: str) -> str:
    return f"{_safe(flow_id)}__{_safe(sid)}"


def _safe(s: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in s)


def _q(s: str) -> str:
    return '"' + s.replace('"', "&quot;") + '"'


def _edge(src: str, dst: str, label: str) -> str:
    if label:
        return f"    {src} -->|{_q(label)}| {dst}"
    return f"    {src} --> {dst}"
