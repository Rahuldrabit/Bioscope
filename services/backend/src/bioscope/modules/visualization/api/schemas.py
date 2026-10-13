"""Public scene transport schemas."""

from __future__ import annotations

from pydantic import BaseModel


class SceneListItem(BaseModel):
    id: str
    kind: str
    status: str


class SceneListResponse(BaseModel):
    items: list[SceneListItem]


class SceneSpecResponse(BaseModel):
    schema_version: str
    scene_id: str
    kind: str
    title: str
    epistemic_label: str
    claim_ids: list[str]
    elements: list[dict[str, str]]
    relations: list[dict[str, str]]
    fallback: dict[str, str]
    structure: dict[str, str] | None = None
    asset_ref: dict[str, str] | None = None

    model_config = {"extra": "forbid"}
