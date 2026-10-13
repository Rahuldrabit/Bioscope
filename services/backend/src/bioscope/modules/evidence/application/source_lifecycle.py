"""Explicit source invalidation coordination."""

from __future__ import annotations

from bioscope.modules.evidence.infrastructure.repository import EvidenceRepository
from bioscope.modules.visualization.infrastructure.repository import SceneRepository


class SourceLifecycleService:
    def __init__(self, evidence: EvidenceRepository, scenes: SceneRepository) -> None:
        self._evidence = evidence
        self._scenes = scenes

    async def retract_source(self, source_id: str) -> int:
        claim_ids = await self._evidence.deprecate_source(source_id)
        return await self._scenes.mark_stale_for_claims(claim_ids)
