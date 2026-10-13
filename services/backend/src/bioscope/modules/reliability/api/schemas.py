"""Public reliability response schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ClaimAssessmentResponse(BaseModel):
    claim_id: str
    verdict: str
    reason: str
    numeric_probability: None = None


class ReliabilityReportResponse(BaseModel):
    id: str
    schema_version: str
    run_id: str
    assessment_mode: str
    dimensions: dict[str, str]
    claim_assessments: list[ClaimAssessmentResponse]
    unsupported_claim_ids: list[str]
    critical_gaps: list[str]
    overall_probability: None = None
    calibration_model_version: None = None
    disclaimer: str
