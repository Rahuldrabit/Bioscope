"""Owner-scoped session repository using SQLAlchemy Core."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import RowMapping

from bioscope.modules.sessions.domain.models import ExplorationSession, SessionMessage
from bioscope.shared.domain.errors import ResourceForbidden
from bioscope.shared.domain.ids import new_id
from bioscope.shared.infrastructure.db import Database
from bioscope.shared.infrastructure.models import (
    confirmed_medications,
    medicine_candidates,
    messages,
    reliability_reports,
    run_claims,
    run_events,
    scenes,
    sessions,
    users,
    verification_reports,
    workflow_runs,
    workflow_tasks,
)


class SessionRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def create(self, *, owner_id: str, title: str) -> ExplorationSession:
        now = datetime.now(UTC)
        record = ExplorationSession(
            id=new_id("sess"), owner_id=owner_id, title=title, version=1, created_at=now
        )
        async with self._database.session() as session:
            existing_user = await session.scalar(select(users.c.id).where(users.c.id == owner_id))
            if existing_user is None:
                await session.execute(insert(users).values(id=owner_id))
            await session.execute(
                insert(sessions).values(
                    id=record.id,
                    owner_id=record.owner_id,
                    title=record.title,
                    risk_scope="EDUCATION",
                    version=record.version,
                    created_at=record.created_at,
                )
            )
            await session.commit()
        return record

    async def get(self, *, session_id: str, owner_id: str) -> ExplorationSession:
        async with self._database.session() as session:
            row = await session.execute(
                select(sessions).where(
                    sessions.c.id == session_id,
                    sessions.c.owner_id == owner_id,
                    sessions.c.deleted_at.is_(None),
                )
            )
            record = row.mappings().first()
        if record is None:
            raise ResourceForbidden()
        return _to_session(record)

    async def list(self, *, owner_id: str) -> Sequence[ExplorationSession]:
        async with self._database.session() as session:
            rows = await session.execute(
                select(sessions)
                .where(sessions.c.owner_id == owner_id, sessions.c.deleted_at.is_(None))
                .order_by(sessions.c.created_at.desc())
            )
            records = rows.mappings().all()
        return [_to_session(record) for record in records]

    async def add_message(self, *, session_id: str, owner_id: str, content: str) -> SessionMessage:
        await self.get(session_id=session_id, owner_id=owner_id)
        record = SessionMessage(
            id=new_id("msg"),
            session_id=session_id,
            role="user",
            content=content,
            created_at=datetime.now(UTC),
        )
        async with self._database.session() as session:
            await session.execute(
                insert(messages).values(
                    id=record.id,
                    session_id=record.session_id,
                    role=record.role,
                    content=record.content,
                    created_at=record.created_at,
                )
            )
            await session.commit()
        return record

    async def delete(self, *, session_id: str, owner_id: str) -> None:
        await self.get(session_id=session_id, owner_id=owner_id)
        async with self._database.session() as session:
            run_ids = select(workflow_runs.c.id).where(
                workflow_runs.c.session_id == session_id,
                workflow_runs.c.owner_id == owner_id,
            )
            await session.execute(
                delete(reliability_reports).where(reliability_reports.c.run_id.in_(run_ids))
            )
            await session.execute(delete(scenes).where(scenes.c.run_id.in_(run_ids)))
            await session.execute(
                delete(verification_reports).where(verification_reports.c.run_id.in_(run_ids))
            )
            await session.execute(delete(run_events).where(run_events.c.run_id.in_(run_ids)))
            await session.execute(
                delete(workflow_tasks).where(workflow_tasks.c.run_id.in_(run_ids))
            )
            await session.execute(delete(run_claims).where(run_claims.c.run_id.in_(run_ids)))
            await session.execute(delete(workflow_runs).where(workflow_runs.c.id.in_(run_ids)))
            await session.execute(
                delete(confirmed_medications).where(
                    confirmed_medications.c.session_id == session_id
                )
            )
            await session.execute(
                delete(medicine_candidates).where(medicine_candidates.c.session_id == session_id)
            )
            await session.execute(delete(messages).where(messages.c.session_id == session_id))
            await session.execute(
                update(sessions)
                .where(sessions.c.id == session_id, sessions.c.owner_id == owner_id)
                .values(deleted_at=datetime.now(UTC), version=sessions.c.version + 1)
            )
            await session.commit()


def _to_session(row: RowMapping) -> ExplorationSession:
    return ExplorationSession(
        id=str(row["id"]),
        owner_id=str(row["owner_id"]),
        title=str(row["title"]),
        version=int(row["version"]),
        created_at=row["created_at"],
    )
