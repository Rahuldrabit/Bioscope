"""Opaque identifier helpers shared by bounded domains."""

from __future__ import annotations

from uuid import uuid4


def new_id(prefix: str) -> str:
    """Create an opaque, non-sequential public identifier."""

    return f"{prefix}_{uuid4().hex}"
