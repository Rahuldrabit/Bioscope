"""Typed, non-probabilistic reliability report values."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class ClaimAssessment:
    claim_id: str
    verdict: str
    reason: str
    numeric_probability: None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ReliabilityReport:
    id: str
    run_id: str
    assessment_mode: str
    dimensions: dict[str, str]
    claim_assessments: list[ClaimAssessment]
    unsupported_claim_ids: list[str]
    critical_gaps: list[str]
    overall_probability: None
    calibration_model_version: None
    disclaimer: str

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "schema_version": "1.0",
            "run_id": self.run_id,
            "assessment_mode": self.assessment_mode,
            "dimensions": self.dimensions,
            "claim_assessments": [item.as_dict() for item in self.claim_assessments],
            "unsupported_claim_ids": self.unsupported_claim_ids,
            "critical_gaps": self.critical_gaps,
            "overall_probability": self.overall_probability,
            "calibration_model_version": self.calibration_model_version,
            "disclaimer": self.disclaimer,
        }
