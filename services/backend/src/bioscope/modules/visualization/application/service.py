"""Compile validated scenes from authorized claims only."""

from __future__ import annotations

from bioscope.modules.evidence.infrastructure.repository import EvidenceRepository
from bioscope.modules.visualization.infrastructure.repository import SceneRepository
from bioscope.scenes.compiler import SceneCompiler


class SceneService:
    def __init__(
        self,
        repository: SceneRepository,
        evidence_repository: EvidenceRepository,
        compiler: SceneCompiler,
    ) -> None:
        self._repository = repository
        self._evidence_repository = evidence_repository
        self._compiler = compiler

    async def compile(
        self, *, run_id: str, claim_ids: list[str], include_general_skin_scene: bool = False
    ) -> list[str]:
        claims = []
        for claim_id in claim_ids:
            claim = await self._evidence_repository.get_claim(claim_id)
            if claim is not None:
                claims.append(claim)
        specs = self._compiler.compile(
            claims, include_general_skin_scene=include_general_skin_scene
        )
        for spec in specs:
            await self._repository.save(run_id=run_id, spec=spec)
        return [str(spec["scene_id"]) for spec in specs]
