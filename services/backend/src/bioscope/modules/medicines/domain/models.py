"""Medicine candidates are never equivalent to confirmed identities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class MedicineCandidate:
    id: str
    session_id: str
    asset_id: str | None
    label: str
    ingredients: tuple[str, ...]
    status: str
    provenance: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ConfirmedMedication:
    id: str
    session_id: str
    candidate_id: str | None
    label: str
    ingredients: tuple[str, ...]
    confirmed_at: datetime
