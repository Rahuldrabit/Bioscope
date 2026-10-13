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


class AuthenticationRequired(AppError):
    def __init__(self) -> None:
        super().__init__(
            code="AUTHENTICATION_REQUIRED",
            message="An authenticated identity is required for this action.",
            status_code=401,
        )


class ResourceForbidden(AppError):
    def __init__(self) -> None:
        super().__init__(
            code="RESOURCE_FORBIDDEN",
            message="You do not have access to this resource.",
            status_code=403,
        )


class ResourceConflict(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code="STATE_CONFLICT", message=message, status_code=409)


class EntityConfirmationRequired(AppError):
    def __init__(self) -> None:
        super().__init__(
            code="ENTITY_CONFIRMATION_REQUIRED",
            message="Please confirm an identity before continuing.",
            status_code=409,
        )


class UploadRejected(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code="UPLOAD_REJECTED", message=message, status_code=422)


class EvidenceInsufficient(AppError):
    def __init__(self, message: str = "Evidence is insufficient for this request.") -> None:
        super().__init__(code="INSUFFICIENT_EVIDENCE", message=message, status_code=422)


class SourceUnavailable(AppError):
    def __init__(self) -> None:
        super().__init__(
            code="SOURCE_UNAVAILABLE",
            message="The requested scientific source is currently unavailable.",
            status_code=503,
            retryable=True,
        )


class PolicyRestricted(AppError):
    def __init__(
        self, message: str = "This request is restricted by the educational safety policy."
    ) -> None:
        super().__init__(code="POLICY_RESTRICTED", message=message, status_code=422)


class InvalidPlan(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code="INVALID_PLAN", message=message, status_code=422)


class RunCancelled(AppError):
    def __init__(self) -> None:
        super().__init__(code="RUN_CANCELLED", message="The run was cancelled.", status_code=409)
