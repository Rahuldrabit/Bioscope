"""Workflow records with redacted, user-visible state only."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class WorkflowRun:
    id: str
    session_id: str
    owner_id: str
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class RunEvent:
    id: str
    run_id: str
    sequence: int
    event_type: str
    payload: dict[str, object]
    occurred_at: datetime
