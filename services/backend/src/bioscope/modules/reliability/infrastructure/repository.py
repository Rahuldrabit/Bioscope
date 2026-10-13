"""Owner-scoped storage for reliability reports."""

from __future__ import annotations

import json

from sqlalchemy import insert, select

from bioscope.modules.reliability.domain.models import ClaimAssessment, ReliabilityReport
from bioscope.shared.domain.errors import ResourceForbidden
from bioscope.shared.infrastructure.db import Database
from bioscope.shared.infrastructure.models import reliability_reports, workflow_runs


class ReliabilityRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def save(self, report: ReliabilityReport) -> None:
        async with self._database.session() as session:
            await session.execute(
                insert(reliability_reports).values(
                    id=report.id,
                    run_id=report.run_id,
                    schema_version="1.0",
                    assessment_mode=report.assessment_mode,
                    dimensions_json=json.dumps(report.dimensions),
                    claim_assessments_json=json.dumps(
                        [item.as_dict() for item in report.claim_assessments]
                    ),
                    unsupported_claim_ids_json=json.dumps(report.unsupported_claim_ids),
                    critical_gaps_json=json.dumps(report.critical_gaps),
                    overall_probability=None,
                    calibration_model_version=None,
                    disclaimer=report.disclaimer,
                )
            )
            await session.commit()

    async def get_for_run(self, *, run_id: str, owner_id: str) -> ReliabilityReport:
        async with self._database.session() as session:
            result = await session.execute(
                select(reliability_reports)
                .join(workflow_runs, workflow_runs.c.id == reliability_reports.c.run_id)
                .where(
                    reliability_reports.c.run_id == run_id,
                    workflow_runs.c.owner_id == owner_id,
                )
                .order_by(reliability_reports.c.created_at.desc())
            )
            row = result.mappings().first()
        if row is None:
            raise ResourceForbidden()
        return ReliabilityReport(
            id=str(row["id"]),
            run_id=str(row["run_id"]),
            assessment_mode=str(row["assessment_mode"]),
            dimensions=json.loads(str(row["dimensions_json"])),
            claim_assessments=[
                ClaimAssessment(
                    claim_id=str(item["claim_id"]),
                    verdict=str(item["verdict"]),
                    reason=str(item["reason"]),
                )
                for item in json.loads(str(row["claim_assessments_json"]))
            ],
            unsupported_claim_ids=list(json.loads(str(row["unsupported_claim_ids_json"]))),
            critical_gaps=list(json.loads(str(row["critical_gaps_json"]))),
            overall_probability=None,
            calibration_model_version=None,
            disclaimer=str(row["disclaimer"]),
        )
