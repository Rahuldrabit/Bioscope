"""A restricted observation response, never a disease assertion."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class SkinObservationResult:
    status: str
    image_analysis_performed: bool
    visible_observations: list[str]
    limitations: list[str]
    patient_specific_molecular_state: str
    guidance: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
