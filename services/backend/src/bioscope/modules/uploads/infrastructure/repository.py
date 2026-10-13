"""Owner-scoped asset metadata persistence."""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import insert, select, update
from sqlalchemy.engine import RowMapping

from bioscope.modules.sessions.infrastructure.repository import SessionRepository
from bioscope.modules.uploads.domain.models import Asset
from bioscope.shared.domain.errors import ResourceForbidden, UploadRejected
from bioscope.shared.domain.ids import new_id
from bioscope.shared.infrastructure.db import Database
from bioscope.shared.infrastructure.models import assets
from bioscope.shared.security.uploads import ALLOWED_IMAGE_MIME_TYPES


class AssetRepository:
    def __init__(self, database: Database, sessions: SessionRepository) -> None:
        self._database = database
        self._sessions = sessions

    async def create_intent(
        self,
        *,
        session_id: str,
        owner_id: str,
        filename: str,
        content_type: str,
        consent_sensitive_processing: bool,
        retention_days: int,
    ) -> tuple[Asset, str]:
        await self._sessions.get(session_id=session_id, owner_id=owner_id)
        if not consent_sensitive_processing:
            raise UploadRejected("Sensitive-image processing consent is required before upload.")
        if content_type not in ALLOWED_IMAGE_MIME_TYPES:
            raise UploadRejected("Only JPEG, PNG, and WebP images are accepted.")
        asset_id = new_id("asset")
        token = secrets.token_urlsafe(32)
        now = datetime.now(UTC)
        record = Asset(
            id=asset_id,
            session_id=session_id,
            owner_id=owner_id,
            original_filename=_safe_filename(filename),
            mime_type=content_type,
            byte_size=0,
            status="PENDING_UPLOAD",
            consent_sensitive_processing=True,
            retention_deadline=now + timedelta(days=retention_days),
            created_at=now,
        )
        async with self._database.session() as session:
            await session.execute(
                insert(assets).values(
                    id=record.id,
                    session_id=record.session_id,
                    owner_id=record.owner_id,
                    original_filename=record.original_filename,
                    mime_type=record.mime_type,
                    byte_size=0,
                    sha256=None,
                    storage_key=f"{asset_id}.bin",
                    status=record.status,
                    upload_token_hash=_token_hash(token),
                    consent_sensitive_processing=record.consent_sensitive_processing,
                    retention_deadline=record.retention_deadline,
                    created_at=record.created_at,
                )
            )
            await session.commit()
        return record, token

    async def get(self, *, asset_id: str, owner_id: str) -> Asset:
        async with self._database.session() as session:
            result = await session.execute(
                select(assets).where(
                    assets.c.id == asset_id,
                    assets.c.owner_id == owner_id,
                    assets.c.deleted_at.is_(None),
                )
            )
            row = result.mappings().first()
        if row is None:
            raise ResourceForbidden()
        return _to_asset(row)

    async def complete(
        self,
        *,
        asset_id: str,
        owner_id: str,
        upload_token: str,
        content: bytes,
    ) -> tuple[Asset, str]:
        async with self._database.session() as session:
            result = await session.execute(
                select(assets).where(
                    assets.c.id == asset_id,
                    assets.c.owner_id == owner_id,
                    assets.c.deleted_at.is_(None),
                )
            )
            row = result.mappings().first()
            if row is None or row["upload_token_hash"] != _token_hash(upload_token):
                raise ResourceForbidden()
            if row["status"] != "PENDING_UPLOAD":
                raise UploadRejected("This upload is no longer awaiting content.")
            digest = hashlib.sha256(content).hexdigest()
            await session.execute(
                update(assets)
                .where(assets.c.id == asset_id)
                .values(
                    byte_size=len(content),
                    sha256=digest,
                    status="READY",
                    upload_token_hash=None,
                )
            )
            await session.commit()
        completed = await self.get(asset_id=asset_id, owner_id=owner_id)
        return completed, str(row["storage_key"])

    async def delete(self, *, asset_id: str, owner_id: str) -> str:
        async with self._database.session() as session:
            result = await session.execute(
                select(assets.c.storage_key).where(
                    assets.c.id == asset_id,
                    assets.c.owner_id == owner_id,
                    assets.c.deleted_at.is_(None),
                )
            )
            storage_key = result.scalar_one_or_none()
            if storage_key is None:
                raise ResourceForbidden()
            await session.execute(
                update(assets)
                .where(assets.c.id == asset_id)
                .values(status="DELETED", deleted_at=datetime.now(UTC))
            )
            await session.commit()
        return str(storage_key)

    async def delete_for_session(self, *, session_id: str, owner_id: str) -> list[str]:
        async with self._database.session() as session:
            result = await session.execute(
                select(assets.c.storage_key).where(
                    assets.c.session_id == session_id,
                    assets.c.owner_id == owner_id,
                    assets.c.deleted_at.is_(None),
                )
            )
            keys = [str(value) for value in result.scalars().all()]
            await session.execute(
                update(assets)
                .where(assets.c.session_id == session_id, assets.c.owner_id == owner_id)
                .values(status="DELETED", deleted_at=datetime.now(UTC))
            )
            await session.commit()
        return keys


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _safe_filename(value: str) -> str:
    filename = value.rsplit("/", maxsplit=1)[-1].rsplit("\\", maxsplit=1)[-1].strip()
    if not filename or len(filename) > 160:
        raise UploadRejected("The uploaded file name is invalid.")
    return filename


def _to_asset(row: RowMapping) -> Asset:
    return Asset(
        id=str(row["id"]),
        session_id=str(row["session_id"]),
        owner_id=str(row["owner_id"]),
        original_filename=str(row["original_filename"]),
        mime_type=str(row["mime_type"]),
        byte_size=int(row["byte_size"]),
        status=str(row["status"]),
        consent_sensitive_processing=bool(row["consent_sensitive_processing"]),
        retention_deadline=row["retention_deadline"],
        created_at=row["created_at"],
    )
