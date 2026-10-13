"""SceneSpec contracts shared by compiler and HTTP API."""

from __future__ import annotations

from typing import Literal, TypedDict

RendererKind = Literal["interaction_network", "evidence_table", "molecular_structure", "skin_layer"]


class SceneSpec(TypedDict):
    schema_version: str
    scene_id: str
    kind: RendererKind
    title: str
    epistemic_label: str
    claim_ids: list[str]
    elements: list[dict[str, str]]
    relations: list[dict[str, str]]
    fallback: dict[str, str]
