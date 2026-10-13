"""Explicit skill registry with server-owned implementations only."""

from __future__ import annotations

from bioscope.shared.domain.errors import InvalidPlan
from bioscope.skills.contracts import SkillDescriptor


class SkillRegistry:
    def __init__(self, descriptors: list[SkillDescriptor]) -> None:
        self._descriptors = {descriptor.skill_id: descriptor for descriptor in descriptors}

    def get(self, skill_id: str) -> SkillDescriptor:
        descriptor = self._descriptors.get(skill_id)
        if descriptor is None:
            raise InvalidPlan("The workflow requested an unknown skill.")
        return descriptor

    def ids(self) -> frozenset[str]:
        return frozenset(self._descriptors)


def builtin_skill_registry() -> SkillRegistry:
    return SkillRegistry(
        [
            SkillDescriptor(
                skill_id="demo.create_evidence",
                version="1.0",
                description=(
                    "Create an explicitly synthetic evidence fixture for local workflow tests."
                ),
                required_permissions=["confirmed_entity"],
                max_runtime_seconds=5,
                max_calls_per_run=3,
                risk_tier="education",
            )
        ]
    )
