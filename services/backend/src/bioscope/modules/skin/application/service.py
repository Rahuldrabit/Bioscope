"""Fail-closed skin photo handling without a classifier."""

from __future__ import annotations

from bioscope.modules.safety.application.policy import EducationalSafetyPolicy
from bioscope.modules.skin.domain.models import SkinObservationResult
from bioscope.modules.uploads.infrastructure.repository import AssetRepository
from bioscope.shared.domain.errors import PolicyRestricted, ResourceConflict


class SkinObservationService:
    def __init__(
        self,
        assets: AssetRepository,
        safety_policy: EducationalSafetyPolicy,
        *,
        enabled: bool,
    ) -> None:
        self._assets = assets
        self._safety_policy = safety_policy
        self._enabled = enabled

    async def observe(
        self, *, session_id: str, owner_id: str, asset_id: str, question: str
    ) -> SkinObservationResult:
        if not self._enabled:
            raise PolicyRestricted(
                "Skin photo observation is disabled until this opt-in feature is enabled."
            )
        asset = await self._assets.get(asset_id=asset_id, owner_id=owner_id)
        if asset.session_id != session_id or asset.status != "READY":
            raise ResourceConflict("A ready image belonging to this private session is required.")
        verdict = self._safety_policy.preflight(question)
        if verdict.status == "SAFETY_ESCALATION":
            return SkinObservationResult(
                status="SAFETY_ESCALATION",
                image_analysis_performed=False,
                visible_observations=[],
                limitations=[
                    "The uploaded photo was not used to establish a diagnosis or urgent condition."
                ],
                patient_specific_molecular_state="UNKNOWN",
                guidance=verdict.message,
            )
        return SkinObservationResult(
            status="OBSERVATION_UNAVAILABLE",
            image_analysis_performed=False,
            visible_observations=[],
            limitations=[
                "No automated visual-description or diagnostic model is configured.",
                "A photo cannot establish a skin diagnosis or reveal a person's molecular state.",
                "This educational feature does not provide treatment, dosing, or "
                "medication-change advice.",
            ],
            patient_specific_molecular_state="UNKNOWN",
            guidance=(
                "The image remains private to this session. Seek professional care for symptoms "
                "that are concerning, persistent, worsening, or otherwise need assessment."
            ),
        )
