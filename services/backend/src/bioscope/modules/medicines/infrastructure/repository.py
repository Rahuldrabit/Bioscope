"""Owner-safe candidate confirmation persistence."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import insert, select, update
from sqlalchemy.engine import RowMapping

from bioscope.modules.medicines.domain.models import ConfirmedMedication, MedicineCandidate
from bioscope.modules.sessions.infrastructure.repository import SessionRepository
from bioscope.shared.domain.errors import (
    EntityConfirmationRequired,
    ResourceConflict,
    ResourceForbidden,
)
from bioscope.shared.domain.ids import new_id
from bioscope.shared.infrastructure.db import Database
from bioscope.shared.infrastructure.models import (
    confirmed_medications,
    medicine_candidates,
    sessions,
)


class MedicineRepository:
    def __init__(self, database: Database, sessions_repository: SessionRepository) -> None:
        self._database = database
        self._sessions = sessions_repository

    async def create_candidate(
        self,
        *,
        session_id: str,
        owner_id: str,
        label: str,
        ingredients: tuple[str, ...],
        asset_id: str | None,
        provenance: str,
    ) -> MedicineCandidate:
        await self._sessions.get(session_id=session_id, owner_id=owner_id)
        candidate = MedicineCandidate(
            id=new_id("medcand"),
            session_id=session_id,
            asset_id=asset_id,
            label=label,
            ingredients=ingredients,
            status="CANDIDATE",
            provenance=provenance,
            created_at=datetime.now(UTC),
        )
        async with self._database.session() as session:
            await session.execute(
                insert(medicine_candidates).values(
                    id=candidate.id,
                    session_id=candidate.session_id,
                    asset_id=candidate.asset_id,
                    label=candidate.label,
                    ingredients=json.dumps(candidate.ingredients),
                    status=candidate.status,
                    provenance=candidate.provenance,
                    created_at=candidate.created_at,
                )
            )
            await session.commit()
        return candidate

    async def list_candidates(self, *, session_id: str, owner_id: str) -> list[MedicineCandidate]:
        await self._sessions.get(session_id=session_id, owner_id=owner_id)
        async with self._database.session() as session:
            rows = await session.execute(
                select(medicine_candidates)
                .where(medicine_candidates.c.session_id == session_id)
                .order_by(medicine_candidates.c.created_at.desc())
            )
            records = rows.mappings().all()
        return [_to_candidate(record) for record in records]

    async def list_confirmed(self, *, session_id: str, owner_id: str) -> list[ConfirmedMedication]:
        await self._sessions.get(session_id=session_id, owner_id=owner_id)
        async with self._database.session() as session:
            rows = await session.execute(
                select(confirmed_medications)
                .where(confirmed_medications.c.session_id == session_id)
                .order_by(confirmed_medications.c.confirmed_at.desc())
            )
            records = rows.mappings().all()
        return [_to_confirmed(record) for record in records]

    async def confirm(
        self,
        *,
        session_id: str,
        candidate_id: str,
        owner_id: str,
        expected_session_version: int,
    ) -> ConfirmedMedication:
        await self._sessions.get(session_id=session_id, owner_id=owner_id)
        async with self._database.session() as session:
            candidate_row = await session.execute(
                select(medicine_candidates).where(
                    medicine_candidates.c.id == candidate_id,
                    medicine_candidates.c.session_id == session_id,
                )
            )
            candidate = candidate_row.mappings().first()
            if candidate is None:
                raise ResourceForbidden()
            if candidate["status"] != "CANDIDATE":
                raise EntityConfirmationRequired()
            version_update = await session.execute(
                update(sessions)
                .where(
                    sessions.c.id == session_id,
                    sessions.c.owner_id == owner_id,
                    sessions.c.version == expected_session_version,
                )
                .values(version=sessions.c.version + 1)
            )
            if int(getattr(version_update, "rowcount", 0) or 0) != 1:
                raise ResourceConflict("The session changed. Refresh and confirm again.")
            record = ConfirmedMedication(
                id=new_id("med"),
                session_id=session_id,
                candidate_id=candidate_id,
                label=str(candidate["label"]),
                ingredients=tuple(json.loads(str(candidate["ingredients"]))),
                confirmed_at=datetime.now(UTC),
            )
            await session.execute(
                insert(confirmed_medications).values(
                    id=record.id,
                    session_id=record.session_id,
                    candidate_id=record.candidate_id,
                    label=record.label,
                    ingredients=json.dumps(record.ingredients),
                    confirmed_by=owner_id,
                    confirmed_at=record.confirmed_at,
                )
            )
            await session.execute(
                update(medicine_candidates)
                .where(medicine_candidates.c.id == candidate_id)
                .values(status="CONFIRMED")
            )
            await session.commit()
        return record


def _to_candidate(row: RowMapping) -> MedicineCandidate:
    return MedicineCandidate(
        id=str(row["id"]),
        session_id=str(row["session_id"]),
        asset_id=str(row["asset_id"]) if row["asset_id"] is not None else None,
        label=str(row["label"]),
        ingredients=tuple(json.loads(str(row["ingredients"]))),
        status=str(row["status"]),
        provenance=str(row["provenance"]),
        created_at=row["created_at"],
    )


def _to_confirmed(row: RowMapping) -> ConfirmedMedication:
    return ConfirmedMedication(
        id=str(row["id"]),
        session_id=str(row["session_id"]),
        candidate_id=str(row["candidate_id"]) if row["candidate_id"] is not None else None,
        label=str(row["label"]),
        ingredients=tuple(json.loads(str(row["ingredients"]))),
        confirmed_at=row["confirmed_at"],
    )
