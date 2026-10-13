"""Cross-resource session deletion orchestration."""

from __future__ import annotations

from typing import Protocol

from bioscope.modules.sessions.infrastructure.repository import SessionRepository


class SessionAssetCleaner(Protocol):
    async def delete_session_assets(self, *, session_id: str, owner_id: str) -> None: ...


class SessionDeletionService:
    def __init__(self, repository: SessionRepository, asset_cleaner: SessionAssetCleaner) -> None:
        self._repository = repository
        self._asset_cleaner = asset_cleaner

    async def delete(self, *, session_id: str, owner_id: str) -> None:
        # Authorize before child cleanup, then remove private blobs before the soft delete.
        await self._repository.get(session_id=session_id, owner_id=owner_id)
        await self._asset_cleaner.delete_session_assets(session_id=session_id, owner_id=owner_id)
        await self._repository.delete(session_id=session_id, owner_id=owner_id)
