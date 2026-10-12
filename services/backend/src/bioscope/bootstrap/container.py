"""Dependency assembly for the modular monolith."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from bioscope.bootstrap.settings import Settings
from bioscope.shared.infrastructure.db import Database
from bioscope.shared.infrastructure.health import ReadinessProbe, TcpReadinessProbe


class ApplicationContainer:
    """Owns infrastructure lifecycle; use cases receive ports, not this container."""

    def __init__(
        self,
        settings: Settings,
        dependency_probes: Sequence[ReadinessProbe] | None = None,
    ) -> None:
        self.settings = settings
        self.database = Database(settings.database_url)
        self.dependency_probes = list(dependency_probes) if dependency_probes is not None else [
            TcpReadinessProbe.from_url(settings.redis_url, 6379),
            TcpReadinessProbe.from_url(
                settings.s3_endpoint,
                443 if settings.s3_endpoint.startswith("https://") else 80,
            ),
        ]

    async def is_ready(self) -> bool:
        """Check required Phase 0 dependencies without returning implementation details."""

        checks = await asyncio.gather(
            self.database.ping(),
            *(probe.ping() for probe in self.dependency_probes),
        )
        return all(checks)

    async def close(self) -> None:
        await self.database.close()
