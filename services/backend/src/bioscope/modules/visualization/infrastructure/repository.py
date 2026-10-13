"""Owner-scoped scene persistence and lookup."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import insert, select, update

from bioscope.shared.domain.errors import EvidenceInsufficient, ResourceForbidden
from bioscope.shared.infrastructure.db import Database
from bioscope.shared.infrastructure.models import run_claims, scenes, workflow_runs


class SceneRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def save(self, *, run_id: str, spec: dict[str, Any]) -> None:
        async with self._database.session() as session:
            await session.execute(
                insert(scenes).values(
                    id=spec["scene_id"],
                    run_id=run_id,
                    schema_version=spec["schema_version"],
                    kind=spec["kind"],
                    spec_json=json.dumps(spec),
                    approval_status="APPROVED",
                )
            )
            await session.commit()

    async def list_for_run(self, *, run_id: str, owner_id: str) -> list[dict[str, Any]]:
        async with self._database.session() as session:
            result = await session.execute(
                select(scenes.c.id, scenes.c.kind, scenes.c.approval_status)
                .join(workflow_runs, workflow_runs.c.id == scenes.c.run_id)
                .where(scenes.c.run_id == run_id, workflow_runs.c.owner_id == owner_id)
            )
            rows = result.mappings().all()
        return [
            {"id": str(row["id"]), "kind": str(row["kind"]), "status": str(row["approval_status"])}
            for row in rows
        ]

    async def get(self, *, scene_id: str, owner_id: str) -> dict[str, Any]:
        async with self._database.session() as session:
            result = await session.execute(
                select(scenes.c.spec_json, scenes.c.approval_status)
                .join(workflow_runs, workflow_runs.c.id == scenes.c.run_id)
                .where(scenes.c.id == scene_id, workflow_runs.c.owner_id == owner_id)
            )
            row = result.mappings().first()
        if row is None:
            raise ResourceForbidden()
        if str(row["approval_status"]) != "APPROVED":
            raise EvidenceInsufficient("This scene is stale because a source was invalidated.")
        return json.loads(str(row["spec_json"]))

    async def mark_stale_for_claims(self, claim_ids: list[str]) -> int:
        if not claim_ids:
            return 0
        async with self._database.session() as session:
            affected_runs = select(run_claims.c.run_id).where(run_claims.c.claim_id.in_(claim_ids))
            existing = await session.execute(
                select(scenes.c.id, scenes.c.spec_json).where(scenes.c.run_id.in_(affected_runs))
            )
            scene_ids = [
                str(row["id"])
                for row in existing.mappings().all()
                if set(json.loads(str(row["spec_json"])).get("claim_ids", [])) & set(claim_ids)
            ]
            await session.execute(
                update(scenes)
                .where(scenes.c.id.in_(scene_ids))
                .values(approval_status="STALE")
            )
            await session.commit()
        return len(scene_ids)
