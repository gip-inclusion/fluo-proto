"""Pydantic models for the Flux DSL.

The DSL describes a clickable prototype as a tree of actors, flows, screens,
tabs, and blocks. YAML is parsed into these models in :mod:`web.dsl.loader`,
edges between them are resolved in :mod:`web.dsl.validate`, and a Mermaid
graph is emitted from them in :mod:`web.dsl.graph`.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class _Strict(BaseModel):
    """Base for all DSL models: extra keys are errors."""

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


class Diagnostic(BaseModel):
    """A schema or edge-resolution problem surfaced to the user."""

    level: Literal["error", "warning"] = "error"
    message: str
    path: str = ""
    file: str = ""


# ---------------------------------------------------------------------------
# Actors and menu
# ---------------------------------------------------------------------------


class Actor(_Strict):
    label: str
    org: str | None = None


class MenuItem(_Strict):
    """A nav entry shown in the offcanvas drawer for a flow."""

    id: str
    label: str
    icon: str  # Remix Icon class, e.g. "ri-dashboard-line"


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


class Action(_Strict):
    """A button: either navigates (``to``), opens a modal (``opens``), or no-op."""

    label: str
    to: str | None = None
    opens: str | None = None

    @model_validator(mode="after")
    def _exclusive(self) -> Action:
        if self.to and self.opens:
            raise ValueError("Action: `to` and `opens` are mutually exclusive")
        return self


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------


class Tab(_Strict):
    label: str
    description: str
    badge: str | None = None
    to: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Page/modal body blocks
# ---------------------------------------------------------------------------


class Search(_Strict):
    placeholder: str = ""
    to: str | None = None


class FilterBar(_Strict):
    filters: list[str]


class Table(_Strict):
    count: int = 5
    rows_to: str | None = None


class Box(_Strict):
    title: str
    fields: int = 3
    kind: Literal["info", "form", "note", "action"] = "info"
    edit_to: str | None = None


# Body-block YAML form is `- search: {...}` (single-key dict). We tag each
# variant with a class attribute so the loader can dispatch on the YAML key.

PageBlock = Search | FilterBar | Table | Box

_PAGE_BLOCK_BY_KEY: dict[str, type[_Strict]] = {
    "search": Search,
    "filter_bar": FilterBar,
    "table": Table,
    "box": Box,
}


# ---------------------------------------------------------------------------
# Dashboard blocks
# ---------------------------------------------------------------------------


class KpiTile(_Strict):
    label: str
    value: int | str
    to: str | None = None


class KpiRow(_Strict):
    tiles: list[KpiTile]


class Card(_Strict):
    title: str
    kind: Literal["list", "feed", "empty"] = "list"
    rows: int = 5
    to: str | None = None


DashboardBlock = Search | KpiRow | Card

_DASHBOARD_BLOCK_BY_KEY: dict[str, type[_Strict]] = {
    "search": Search,
    "kpi_row": KpiRow,
    "card": Card,
}


def _coerce_block(raw: Any, key_map: dict[str, type[_Strict]], where: str) -> Any:
    """Turn a single-key dict like ``{search: {...}}`` into the matching model."""
    if isinstance(raw, _Strict):
        return raw
    if not isinstance(raw, dict) or len(raw) != 1:
        raise ValueError(f"{where}: each block must be a single-key dict (one of {sorted(key_map)})")
    [(key, payload)] = raw.items()
    if key not in key_map:
        raise ValueError(f"{where}: unknown block kind '{key}'; expected one of {sorted(key_map)}")
    if payload is None:
        payload = {}
    return key_map[key].model_validate(payload)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------


class _ScreenBase(_Strict):
    title: str
    nav_item: str | None = None
    actions: list[Action] = Field(default_factory=list)


class Page(_ScreenBase):
    kind: Literal["page"] = "page"
    prevstep_to: str | None = None
    body: list[PageBlock] = Field(default_factory=list)
    tabs: dict[str, Tab] | None = None

    @field_validator("body", mode="before")
    @classmethod
    def _parse_body(cls, v: Any) -> Any:
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError("Page.body must be a list")
        return [_coerce_block(item, _PAGE_BLOCK_BY_KEY, "Page.body") for item in v]


class Modal(_ScreenBase):
    kind: Literal["modal"] = "modal"
    body: list[PageBlock] = Field(default_factory=list)

    @field_validator("body", mode="before")
    @classmethod
    def _parse_body(cls, v: Any) -> Any:
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError("Modal.body must be a list")
        return [_coerce_block(item, _PAGE_BLOCK_BY_KEY, "Modal.body") for item in v]


class Dashboard(_ScreenBase):
    kind: Literal["dashboard"] = "dashboard"
    blocks: list[DashboardBlock] = Field(default_factory=list)

    @field_validator("blocks", mode="before")
    @classmethod
    def _parse_blocks(cls, v: Any) -> Any:
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError("Dashboard.blocks must be a list")
        return [_coerce_block(item, _DASHBOARD_BLOCK_BY_KEY, "Dashboard.blocks") for item in v]


Screen = Annotated[Page | Modal | Dashboard, Field(discriminator="kind")]


# ---------------------------------------------------------------------------
# Flow + composed top-level model
# ---------------------------------------------------------------------------


class Flow(_Strict):
    id: str
    actor: str
    entry: str
    menu: list[MenuItem] = Field(default_factory=list)


class FluxConfig(_Strict):
    """Shape of ``flows/flux.yaml``."""

    actors: dict[str, Actor]
    flows: list[str]


class FluxModel(BaseModel):
    """Composed in-memory view of all loaded YAML.

    Built by the loader after parsing ``flux.yaml`` plus each per-flow file.
    Screens are namespaced by flow: a ``to: candidatures_list`` resolves
    within the current flow only.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    actors: dict[str, Actor]
    flows: dict[str, Flow]  # keyed by Flow.id
    # screens keyed by (flow_id, screen_id); built by the loader.
    screens: dict[tuple[str, str], Page | Modal | Dashboard]

    def screen(self, flow_id: str, screen_id: str) -> Page | Modal | Dashboard | None:
        return self.screens.get((flow_id, screen_id))

    def screens_in(self, flow_id: str) -> dict[str, Page | Modal | Dashboard]:
        return {sid: s for (fid, sid), s in self.screens.items() if fid == flow_id}
