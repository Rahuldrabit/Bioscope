"""Public workflow transport schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StartRunRequest(BaseModel):
    session_id: str
    question: str = Field(min_length=1, max_length=4_000)
    message_id: str | None = None


class RunResponse(BaseModel):
    id: str
    session_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    events_url: str


class RunEventResponse(BaseModel):
    event_id: str
    run_id: str
    sequence: int
    type: str
    occurred_at: datetime
    payload: dict[str, object]


class RunClaimsResponse(BaseModel):
    claim_ids: list[str]
