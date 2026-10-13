"""Static skill descriptors; no generated code or dynamic imports."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SkillDescriptor(BaseModel):
    skill_id: str
    version: str
    description: str
    required_permissions: list[str] = Field(default_factory=list)
    max_runtime_seconds: int = Field(ge=1, le=30)
    max_calls_per_run: int = Field(ge=1, le=5)
    risk_tier: Literal["education", "health_sensitive", "restricted"]
