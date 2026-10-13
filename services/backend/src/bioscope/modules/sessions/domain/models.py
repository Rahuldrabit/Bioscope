"""Immutable session-facing domain records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ExplorationSession:
    id: str
    owner_id: str
    title: str
    version: int
    created_at: datetime


@dataclass(frozen=True, slots=True)
class SessionMessage:
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime
