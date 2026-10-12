"""Stable, transport-independent error concepts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AppError(Exception):
    """A safe error that can be translated to the public API envelope."""

    code: str
    message: str
    status_code: int
    retryable: bool = False
    details: dict[str, Any] = field(default_factory=dict)


class DependencyUnavailable(AppError):
    def __init__(self) -> None:
        super().__init__(
            code="DEPENDENCY_UNAVAILABLE",
            message="A required service is temporarily unavailable.",
            status_code=503,
            retryable=True,
        )
