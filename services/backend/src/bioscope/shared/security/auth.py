"""Development-safe request identity extraction.

Production identity is deliberately not implemented until an OIDC issuer and audience are supplied.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from bioscope.bootstrap.settings import Settings
from bioscope.shared.domain.errors import AuthenticationRequired


@dataclass(frozen=True, slots=True)
class Actor:
    subject: str
    role: str = "user"


def current_actor(request: Request) -> Actor:
    """Return a local-only actor without accepting identities in production."""

    settings: Settings = request.app.state.container.settings
    if settings.app_env in {"staging", "production"}:
        raise AuthenticationRequired()
    subject = request.headers.get("X-Demo-User-ID", "demo-user").strip()
    if not subject or len(subject) > 80 or not subject.replace("-", "").replace("_", "").isalnum():
        raise AuthenticationRequired()
    return Actor(subject=subject)
