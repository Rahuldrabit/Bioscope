"""Immutable asset records that never expose a storage path to API clients."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Asset:
    id: str
    session_id: str
    owner_id: str
    original_filename: str
    mime_type: str
    byte_size: int
    status: str
    consent_sensitive_processing: bool
    retention_deadline: datetime
    created_at: datetime
