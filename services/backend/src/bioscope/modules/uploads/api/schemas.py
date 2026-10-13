"""Public upload transport schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CreateUploadIntentRequest(BaseModel):
    session_id: str
    filename: str = Field(min_length=1, max_length=160)
    content_type: str
    consent_sensitive_processing: bool


class UploadIntentResponse(BaseModel):
    asset_id: str
    upload_token: str
    content_endpoint: str
    expires_in_seconds: int = 900


class AssetResponse(BaseModel):
    id: str
    session_id: str
    original_filename: str
    mime_type: str
    byte_size: int
    status: str
    consent_sensitive_processing: bool
    retention_deadline: datetime
    created_at: datetime
