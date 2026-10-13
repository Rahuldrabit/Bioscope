"""Transactional workflow state, event, task, and claim persistence."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import func, insert, select, update
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from bioscope.modules.agent_workflows.domain.models import RunEvent, WorkflowRun
from bioscope.modules.agent_workflows.domain.plans import TaskSpec
from bioscope.modules.sessions.infrastructure.repository import SessionRepository
from bioscope.shared.domain.errors import ResourceForbidden
from bioscope.shared.domain.ids import new_id
from bioscope.shared.infrastructure.db import Database
from bioscope.shared.infrastructure.models import (
    run_claims,
    run_events,
    verification_reports,
    workflow_runs,
    workflow_tasks,
)


class WorkflowRepository:
    def __init__(self, database: Database, sessions_repository: SessionRepository) -> None:
        self._database = database
        self._sessions = sessions_repository

    async def create(
        self, *, session_id: str, owner_id: str, question: str, message_id: str | None
    ) -> WorkflowRun:
        await self._sessions.get(session_id=session_id, owner_id=owner_id)
        now = datetime.now(UTC)
        run = WorkflowRun(
            id=new_id("run"),
            session_id=session_id,
            owner_id=owner_id,
            status="RECEIVED",
            created_at=now,
            updated_at=now,
        )
        async with self._database.session() as session:
            await session.execute(
                insert(workflow_runs).values(
                    id=run.id,
                    session_id=run.session_id,
                    owner_id=run.owner_id,
                    message_id=message_id,
                    question=question,
                    status=run.status,
                    policy_version="education-policy-2026-10",
                    created_at=run.created_at,
                    updated_at=run.updated_at,
                )
            )
            await self._append_event_in_session(
                session,
                run_id=run.id,
                event_type="run.received",
                payload={"phase": "RECEIVED"},
            )
            await session.commit()
        return run

    async def get(self, *, run_id: str, owner_id: str) -> WorkflowRun:
        async with self._database.session() as session:
            result = await session.execute(
                select(workflow_runs).where(
                    workflow_runs.c.id == run_id, workflow_runs.c.owner_id == owner_id
                )
            )
            row = result.mappings().first()
        if row is None:
            raise ResourceForbidden()
        return _to_run(row)

    async def internal(self, run_id: str) -> tuple[WorkflowRun, str]:
        async with self._database.session() as session:
            result = await session.execute(
                select(workflow_runs).where(workflow_runs.c.id == run_id)
            )
            row = result.mappings().first()
        if row is None:
            raise ResourceForbidden()
        return _to_run(row), str(row["question"])

    async def transition(
        self, *, run_id: str, status: str, event_type: str, payload: dict[str, object]
    ) -> None:
        async with self._database.session() as session:
            await session.execute(
                update(workflow_runs)
                .where(workflow_runs.c.id == run_id)
                .values(status=status, updated_at=datetime.now(UTC))
            )
            await self._append_event_in_session(
                session,
                run_id=run_id,
                event_type=event_type,
                payload=payload,
            )
            await session.commit()

    async def record_plan(self, *, run_id: str, tasks: list[TaskSpec]) -> None:
        async with self._database.session() as session:
            for task in tasks:
                await session.execute(
                    insert(workflow_tasks).values(
                        id=task.task_id,
                        run_id=run_id,
                        kind=task.skill_id,
                        depends_on_json=json.dumps(task.depends_on),
                        status="PENDING",
                        attempt=0,
                        max_retries=task.max_retries,
                    )
                )
            await session.commit()

    async def task_started(self, *, task_id: str) -> None:
        async with self._database.session() as session:
            await session.execute(
                update(workflow_tasks)
                .where(workflow_tasks.c.id == task_id)
                .values(status="RUNNING", attempt=workflow_tasks.c.attempt + 1)
            )
            await session.commit()

    async def task_completed(self, *, task_id: str, output_ref: str) -> None:
        async with self._database.session() as session:
            await session.execute(
                update(workflow_tasks)
                .where(workflow_tasks.c.id == task_id)
                .values(status="COMPLETED", output_ref=output_ref)
            )
            await session.commit()

    async def link_claim(self, *, run_id: str, claim_id: str) -> None:
        async with self._database.session() as session:
            await session.execute(insert(run_claims).values(run_id=run_id, claim_id=claim_id))
            await session.commit()

    async def add_verification(
        self, *, run_id: str, claim_id: str, verdict: str, reason: str
    ) -> None:
        async with self._database.session() as session:
            await session.execute(
                insert(verification_reports).values(
                    id=new_id("verify"),
                    run_id=run_id,
                    claim_id=claim_id,
                    verdict=verdict,
                    reason=reason,
                    source_snapshot_ids_json="[]",
                )
            )
            await session.commit()

    async def events(self, *, run_id: str, owner_id: str, after_sequence: int) -> list[RunEvent]:
        await self.get(run_id=run_id, owner_id=owner_id)
        async with self._database.session() as session:
            result = await session.execute(
                select(run_events)
                .where(run_events.c.run_id == run_id, run_events.c.sequence > after_sequence)
                .order_by(run_events.c.sequence)
            )
            rows = result.mappings().all()
        return [_to_event(row) for row in rows]

    async def claim_ids(self, *, run_id: str, owner_id: str) -> list[str]:
        await self.get(run_id=run_id, owner_id=owner_id)
        async with self._database.session() as session:
            result = await session.execute(
                select(run_claims.c.claim_id).where(run_claims.c.run_id == run_id)
            )
            return [str(value) for value in result.scalars().all()]

    async def cancel(self, *, run_id: str, owner_id: str) -> WorkflowRun:
        run = await self.get(run_id=run_id, owner_id=owner_id)
        if run.status in {"READY", "LIMITED_ANSWER", "SAFETY_ESCALATION", "CANCELLED"}:
            return run
        await self.transition(
            run_id=run_id,
            status="CANCELLED",
            event_type="run.cancelled",
            payload={"phase": "CANCELLED"},
        )
        return await self.get(run_id=run_id, owner_id=owner_id)

    async def _append_event_in_session(
        self,
        session: AsyncSession,
        *,
        run_id: str,
        event_type: str,
        payload: dict[str, object],
    ) -> None:
        max_sequence = await session.scalar(
            select(func.max(run_events.c.sequence)).where(run_events.c.run_id == run_id)
        )
        await session.execute(
            insert(run_events).values(
                id=new_id("runevt"),
                run_id=run_id,
                sequence=int(max_sequence or 0) + 1,
                event_type=event_type,
                payload_json=json.dumps(payload),
                occurred_at=datetime.now(UTC),
            )
        )


def _to_run(row: RowMapping) -> WorkflowRun:
    return WorkflowRun(
        id=str(row["id"]),
        session_id=str(row["session_id"]),
        owner_id=str(row["owner_id"]),
        status=str(row["status"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _to_event(row: RowMapping) -> RunEvent:
    return RunEvent(
        id=str(row["id"]),
        run_id=str(row["run_id"]),
        sequence=int(row["sequence"]),
        event_type=str(row["event_type"]),
        payload=json.loads(str(row["payload_json"])),
        occurred_at=row["occurred_at"],
    )
