"""Public candidate and confirmation schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AddMedicineCandidateRequest(BaseModel):
    label: str = Field(min_length=1, max_length=160)


class ConfirmCandidateRequest(BaseModel):
    candidate_id: str
    expected_session_version: int = Field(ge=1)


class MedicineCandidateResponse(BaseModel):
    id: str
    session_id: str
    asset_id: str | None
    label: str
    ingredients: tuple[str, ...]
    status: str
    provenance: str
    created_at: datetime


class ConfirmedMedicationResponse(BaseModel):
    id: str
    session_id: str
    candidate_id: str | None
    label: str
    ingredients: tuple[str, ...]
    confirmed_at: datetime


class EntityCandidatesResponse(BaseModel):
    candidates: list[MedicineCandidateResponse]
    confirmed: list[ConfirmedMedicationResponse]
