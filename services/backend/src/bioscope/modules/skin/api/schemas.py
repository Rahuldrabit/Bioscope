"""Public non-diagnostic skin observation schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateSkinObservationRequest(BaseModel):
    asset_id: str
    question: str = Field(min_length=1, max_length=2_000)


class SkinObservationResponse(BaseModel):
    status: str
    image_analysis_performed: bool
    visible_observations: list[str]
    limitations: list[str]
    patient_specific_molecular_state: str
    guidance: str
