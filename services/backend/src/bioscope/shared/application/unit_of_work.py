"""Transactional port used by later vertical slices."""

from __future__ import annotations

from typing import Protocol


class UnitOfWork(Protocol):
    """Application code depends on this port instead of database sessions."""

    async def __aenter__(self) -> UnitOfWork: ...

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
