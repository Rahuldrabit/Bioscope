"""Safe upload completion and deletion orchestration."""

from __future__ import annotations

from bioscope.modules.uploads.domain.models import Asset
from bioscope.modules.uploads.infrastructure.repository import AssetRepository
from bioscope.shared.domain.errors import UploadRejected
from bioscope.shared.infrastructure.object_store import LocalPrivateObjectStore
from bioscope.shared.security.uploads import validate_image_upload


class UploadService:
    def __init__(
        self,
        repository: AssetRepository,
        object_store: LocalPrivateObjectStore,
        max_upload_mb: int,
    ) -> None:
        self._repository = repository
        self._object_store = object_store
        self._max_upload_mb = max_upload_mb

    async def complete(
        self,
        *,
        asset_id: str,
        owner_id: str,
        upload_token: str,
        content: bytes,
        content_type: str,
    ) -> Asset:
        asset = await self._repository.get(asset_id=asset_id, owner_id=owner_id)
        if content_type != asset.mime_type:
            raise UploadRejected("Uploaded content type differs from the approved intent.")
        validate_image_upload(
            content=content,
            content_type=content_type,
            max_upload_mb=self._max_upload_mb,
        )
        completed, storage_key = await self._repository.complete(
            asset_id=asset_id,
            owner_id=owner_id,
            upload_token=upload_token,
            content=content,
        )
        try:
            await self._object_store.put(storage_key, content)
        except Exception:
            # Metadata exists but never reports READY unless the storage write succeeded.
            await self._repository.delete(asset_id=asset_id, owner_id=owner_id)
            raise
        return completed

    async def delete(self, *, asset_id: str, owner_id: str) -> None:
        storage_key = await self._repository.delete(asset_id=asset_id, owner_id=owner_id)
        await self._object_store.delete(storage_key)

    async def delete_session_assets(self, *, session_id: str, owner_id: str) -> None:
        storage_keys = await self._repository.delete_for_session(
            session_id=session_id, owner_id=owner_id
        )
        for storage_key in storage_keys:
            await self._object_store.delete(storage_key)
