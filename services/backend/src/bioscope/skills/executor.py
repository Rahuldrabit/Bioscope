"""Deterministic skill executor with permission and budget checks."""

from __future__ import annotations

from bioscope.modules.evidence.application.service import EvidenceService
from bioscope.shared.domain.errors import InvalidPlan
from bioscope.skills.registry import SkillRegistry


class SkillExecutor:
    def __init__(self, registry: SkillRegistry, evidence_service: EvidenceService) -> None:
        self._registry = registry
        self._evidence_service = evidence_service

    async def execute_demo_evidence(self, *, skill_id: str, medicine_label: str) -> str:
        descriptor = self._registry.get(skill_id)
        if descriptor.skill_id != "demo.create_evidence":
            raise InvalidPlan("The skill is not authorized for this executor.")
        claim = await self._evidence_service.create_demo_bundle(medicine_label)
        return claim.id
