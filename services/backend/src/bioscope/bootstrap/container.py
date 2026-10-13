"""Dependency assembly for the modular monolith."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from bioscope.bootstrap.settings import Settings
from bioscope.connectors.chembl.client import ChEMBLClient
from bioscope.modules.agent_workflows.application.runner import WorkflowRunner
from bioscope.modules.agent_workflows.infrastructure.repository import WorkflowRepository
from bioscope.modules.evidence.application.service import EvidenceService
from bioscope.modules.evidence.application.source_lifecycle import SourceLifecycleService
from bioscope.modules.evidence.infrastructure.repository import EvidenceRepository
from bioscope.modules.medicines.application.service import MedicineIntakeService
from bioscope.modules.medicines.infrastructure.repository import MedicineRepository
from bioscope.modules.reliability.application.service import ReliabilityService
from bioscope.modules.reliability.infrastructure.repository import ReliabilityRepository
from bioscope.modules.safety.application.policy import EducationalSafetyPolicy
from bioscope.modules.sessions.application.service import SessionDeletionService
from bioscope.modules.sessions.infrastructure.repository import SessionRepository
from bioscope.modules.skin.application.service import SkinObservationService
from bioscope.modules.uploads.application.service import UploadService
from bioscope.modules.uploads.infrastructure.repository import AssetRepository
from bioscope.modules.visualization.application.service import SceneService
from bioscope.modules.visualization.infrastructure.repository import SceneRepository
from bioscope.scenes.compiler import SceneCompiler
from bioscope.shared.infrastructure.db import Database
from bioscope.shared.infrastructure.health import ReadinessProbe, TcpReadinessProbe
from bioscope.shared.infrastructure.object_store import LocalPrivateObjectStore
from bioscope.skills.executor import SkillExecutor
from bioscope.skills.registry import builtin_skill_registry


class ApplicationContainer:
    """Owns infrastructure lifecycle; use cases receive ports, not this container."""

    def __init__(
        self,
        settings: Settings,
        dependency_probes: Sequence[ReadinessProbe] | None = None,
    ) -> None:
        self.settings = settings
        self.database = Database(settings.database_url)
        self.object_store = LocalPrivateObjectStore(settings.local_asset_dir)
        self.session_repository = SessionRepository(self.database)
        self.asset_repository = AssetRepository(self.database, self.session_repository)
        self.upload_service = UploadService(
            self.asset_repository,
            self.object_store,
            settings.max_upload_mb,
        )
        self.session_deletion_service = SessionDeletionService(
            self.session_repository,
            self.upload_service,
        )
        self.medicine_repository = MedicineRepository(self.database, self.session_repository)
        self.medicine_intake_service = MedicineIntakeService(self.medicine_repository)
        self.evidence_repository = EvidenceRepository(self.database)
        self.evidence_service = EvidenceService(self.evidence_repository)
        self.chembl_client = ChEMBLClient(enabled=settings.enable_external_sources)
        self.skill_registry = builtin_skill_registry()
        self.skill_executor = SkillExecutor(self.skill_registry, self.evidence_service)
        self.safety_policy = EducationalSafetyPolicy()
        self.skin_observation_service = SkinObservationService(
            self.asset_repository,
            self.safety_policy,
            enabled=settings.enable_skin_image_upload,
        )
        self.scene_repository = SceneRepository(self.database)
        self.scene_service = SceneService(
            self.scene_repository,
            self.evidence_repository,
            SceneCompiler(),
        )
        self.source_lifecycle_service = SourceLifecycleService(
            self.evidence_repository, self.scene_repository
        )
        self.reliability_repository = ReliabilityRepository(self.database)
        self.reliability_service = ReliabilityService(self.reliability_repository)
        self.workflow_repository = WorkflowRepository(self.database, self.session_repository)
        self.workflow_runner = WorkflowRunner(
            self.workflow_repository,
            self.medicine_repository,
            self.skill_registry,
            self.skill_executor,
            self.safety_policy,
            self.scene_service,
            self.reliability_service,
        )
        self.dependency_probes = (
            list(dependency_probes)
            if dependency_probes is not None
            else [
                TcpReadinessProbe.from_url(settings.redis_url, 6379),
                TcpReadinessProbe.from_url(
                    settings.s3_endpoint,
                    443 if settings.s3_endpoint.startswith("https://") else 80,
                ),
            ]
        )

    async def is_ready(self) -> bool:
        """Check required Phase 0 dependencies without returning implementation details."""

        checks = await asyncio.gather(
            self.database.ping(),
            *(probe.ping() for probe in self.dependency_probes),
        )
        return all(checks)

    async def close(self) -> None:
        await self.database.close()
