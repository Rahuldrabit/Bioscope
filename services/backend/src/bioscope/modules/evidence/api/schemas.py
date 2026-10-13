"""Public provenance API schemas."""

from __future__ import annotations

from pydantic import BaseModel


class SourceResponse(BaseModel):
    id: str
    provider: str
    stable_url: str
    citation: str
    license_policy: str
    provenance: str
    status: str


class EntityResponse(BaseModel):
    id: str
    entity_type: str
    label: str
    organism: str
    provenance: str


class ClaimSourceResponse(BaseModel):
    id: str
    provider: str
    stable_url: str
    citation: str
    provenance: str
    status: str
    snapshot_id: str
    release_version: str


class ClaimResponse(BaseModel):
    id: str
    subject_entity_id: str
    subject_label: str
    predicate: str
    object_entity_id: str
    context: dict[str, object]
    status: str
    provenance: str
    source: ClaimSourceResponse
