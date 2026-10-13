"""Assess evidence coverage without creating false numeric precision."""

from __future__ import annotations

from bioscope.modules.reliability.domain.models import ClaimAssessment, ReliabilityReport
from bioscope.modules.reliability.infrastructure.repository import ReliabilityRepository
from bioscope.shared.domain.ids import new_id


class ReliabilityService:
    def __init__(self, repository: ReliabilityRepository) -> None:
        self._repository = repository

    async def assess(
        self, *, run_id: str, claim_ids: list[str], scene_ids: list[str]
    ) -> ReliabilityReport:
        assessments = [
            ClaimAssessment(
                claim_id=claim_id,
                verdict="INSUFFICIENT",
                reason=(
                    "The current fixture is synthetic software-test data and is not "
                    "biomedical evidence."
                ),
            )
            for claim_id in claim_ids
        ]
        report = ReliabilityReport(
            id=new_id("reliability"),
            run_id=run_id,
            assessment_mode="EVIDENCE_STATUS_ONLY",
            dimensions={
                "entity_identity": "USER_CONFIRMED",
                "source_strength": "SYNTHETIC_TEST_FIXTURE",
                "causal_chain": "NOT_ESTABLISHED",
                "individual_applicability": "NOT_ASSESSED",
                "visual_fidelity": "SCHEMATIC_VALIDATED" if scene_ids else "NO_SCENE_RELEASED",
            },
            claim_assessments=assessments,
            unsupported_claim_ids=claim_ids,
            critical_gaps=[
                "No live or curated biomedical source has been approved for this fixture.",
                "No patient-specific biological measurements are available.",
            ],
            overall_probability=None,
            calibration_model_version=None,
            disclaimer=(
                "Educational workflow status only; this is not a diagnosis, treatment "
                "recommendation, or calibrated reliability estimate."
            ),
        )
        await self._repository.save(report)
        return report
