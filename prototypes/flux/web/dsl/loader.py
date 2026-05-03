"""Load YAML from disk into a :class:`FluxModel`.

The loader is intentionally forgiving: it captures Pydantic and YAML errors
as :class:`Diagnostic`s and returns whatever was parsed successfully, so the
dev experience survives broken YAML.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .models import (
    Dashboard,
    Diagnostic,
    Flow,
    FluxConfig,
    FluxModel,
    Modal,
    Page,
)

_SCREEN_KIND_MAP = {"page": Page, "modal": Modal, "dashboard": Dashboard}


def load(flows_dir: Path) -> tuple[FluxModel, list[Diagnostic]]:
    """Read ``flux.yaml`` and every flow file, returning the composed model
    plus any diagnostics encountered. The returned model is always usable —
    missing pieces are reported, not raised.
    """
    diagnostics: list[Diagnostic] = []
    actors = {}
    flows: dict[str, Flow] = {}
    screens: dict[tuple[str, str], Page | Modal | Dashboard] = {}

    config_path = flows_dir / "flux.yaml"
    config = _load_config(config_path, diagnostics)
    if config:
        actors = config.actors
        for rel_path in config.flows:
            flow_file = flows_dir / rel_path
            flow, flow_screens = _load_flow_file(flow_file, diagnostics)
            if flow is None:
                continue
            if flow.id in flows:
                diagnostics.append(
                    Diagnostic(
                        message=f"Duplicate flow id '{flow.id}' (also defined in another file)",
                        path=f"flow.id={flow.id}",
                        file=str(flow_file.name),
                    )
                )
                continue
            flows[flow.id] = flow
            for sid, screen in flow_screens.items():
                screens[(flow.id, sid)] = screen

    model = FluxModel(actors=actors, flows=flows, screens=screens)
    return model, diagnostics


def _load_yaml(path: Path, diagnostics: list[Diagnostic]) -> Any:
    try:
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        diagnostics.append(Diagnostic(message=f"File not found: {path}", file=str(path.name)))
        return None
    except yaml.YAMLError as exc:
        diagnostics.append(Diagnostic(message=f"YAML parse error: {exc}", file=str(path.name)))
        return None


def _load_config(path: Path, diagnostics: list[Diagnostic]) -> FluxConfig | None:
    raw = _load_yaml(path, diagnostics)
    if raw is None:
        return None
    try:
        return FluxConfig.model_validate(raw)
    except ValidationError as exc:
        for err in exc.errors():
            diagnostics.append(
                Diagnostic(
                    message=err["msg"],
                    path=".".join(str(p) for p in err["loc"]),
                    file=str(path.name),
                )
            )
        return None


def _load_flow_file(
    path: Path, diagnostics: list[Diagnostic]
) -> tuple[Flow | None, dict[str, Page | Modal | Dashboard]]:
    raw = _load_yaml(path, diagnostics)
    if raw is None:
        return None, {}
    if not isinstance(raw, dict):
        diagnostics.append(Diagnostic(message="flow file must be a mapping", file=str(path.name)))
        return None, {}

    flow_raw = raw.get("flow")
    screens_raw = raw.get("screens", {}) or {}

    flow: Flow | None = None
    if flow_raw is None:
        diagnostics.append(Diagnostic(message="missing top-level `flow:` block", file=str(path.name)))
    else:
        try:
            flow = Flow.model_validate(flow_raw)
        except ValidationError as exc:
            for err in exc.errors():
                diagnostics.append(
                    Diagnostic(
                        message=err["msg"],
                        path="flow." + ".".join(str(p) for p in err["loc"]),
                        file=str(path.name),
                    )
                )

    screens: dict[str, Page | Modal | Dashboard] = {}
    if not isinstance(screens_raw, dict):
        diagnostics.append(Diagnostic(message="`screens:` must be a mapping", file=str(path.name)))
    else:
        for sid, screen_raw in screens_raw.items():
            screen = _parse_screen(sid, screen_raw, path, diagnostics)
            if screen is not None:
                screens[sid] = screen

    return flow, screens


def _parse_screen(
    sid: str,
    raw: Any,
    path: Path,
    diagnostics: list[Diagnostic],
) -> Page | Modal | Dashboard | None:
    if not isinstance(raw, dict):
        diagnostics.append(
            Diagnostic(
                message=f"screen '{sid}' must be a mapping",
                path=f"screens.{sid}",
                file=str(path.name),
            )
        )
        return None
    kind = raw.get("kind", "page")
    cls = _SCREEN_KIND_MAP.get(kind)
    if cls is None:
        diagnostics.append(
            Diagnostic(
                message=f"unknown screen kind '{kind}' (expected page|modal|dashboard)",
                path=f"screens.{sid}.kind",
                file=str(path.name),
            )
        )
        return None
    try:
        return cls.model_validate(raw)
    except ValidationError as exc:
        for err in exc.errors():
            diagnostics.append(
                Diagnostic(
                    message=err["msg"],
                    path=f"screens.{sid}." + ".".join(str(p) for p in err["loc"]),
                    file=str(path.name),
                )
            )
        return None
