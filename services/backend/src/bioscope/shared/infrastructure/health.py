"""Small, injectable readiness probes for required network dependencies."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse


class ReadinessProbe(Protocol):
    async def ping(self) -> bool: ...


@dataclass(frozen=True)
class TcpReadinessProbe:
    host: str
    port: int
    timeout_seconds: float = 1.0

    @classmethod
    def from_url(cls, url: str, default_port: int) -> TcpReadinessProbe:
        parsed = urlparse(url)
        if not parsed.hostname:
            raise ValueError("Readiness probe URL must include a host")
        return cls(host=parsed.hostname, port=parsed.port or default_port)

    async def ping(self) -> bool:
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout_seconds,
            )
            writer.close()
            await writer.wait_closed()
        except (OSError, TimeoutError):
            return False
        return True
