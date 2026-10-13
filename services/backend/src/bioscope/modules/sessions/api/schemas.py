"""Public session transport schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)


class SessionResponse(BaseModel):
    id: str
    title: str
    version: int
    created_at: datetime


class SessionListResponse(BaseModel):
    items: list[SessionResponse]


class AddMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4_000)


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime
