"""Deterministic local workflow runner.

It is deliberately provider-neutral: user text never selects code, URLs, or skills.
"""

from __future__ import annotations

from dataclasses import dataclass

from bioscope.modules.agent_workflows.domain.plans import TaskPlan, TaskSpec, validate_plan
from bioscope.modules.agent_workflows.infrastructure.repository import WorkflowRepository
from bioscope.modules.medicines.infrastructure.repository import MedicineRepository
from bioscope.modules.reliability.application.service import ReliabilityService
from bioscope.modules.safety.application.policy import EducationalSafetyPolicy
from bioscope.modules.visualization.application.service import SceneService
from bioscope.skills.executor import SkillExecutor
from bioscope.skills.registry import SkillRegistry


@dataclass(frozen=True, slots=True)
class DeterministicFakeLLM:
    """Test/demo planner that emits only server-authored task shapes."""

    def propose(self, medicine_count: int) -> TaskPlan:
        return TaskPlan(
            tasks=[
                TaskSpec(
                    task_id=f"task_demo_evidence_{index}",
                    skill_id="demo.create_evidence",
                    timeout_ms=5_000,
                    max_retries=0,
                )
                for index in range(medicine_count)
            ]
        )


class WorkflowRunner:
    def __init__(
        self,
        repository: WorkflowRepository,
        medicines: MedicineRepository,
        registry: SkillRegistry,
        executor: SkillExecutor,
        safety_policy: EducationalSafetyPolicy,
        scene_service: SceneService,
        reliability_service: ReliabilityService,
    ) -> None:
        self._repository = repository
        self._medicines = medicines
        self._registry = registry
        self._executor = executor
        self._safety_policy = safety_policy
        self._scene_service = scene_service
        self._reliability_service = reliability_service
        self._planner = DeterministicFakeLLM()

    async def execute(self, run_id: str) -> None:
        run, question = await self._repository.internal(run_id)
        confirmed = await self._medicines.list_confirmed(
            session_id=run.session_id, owner_id=run.owner_id
        )
        if not confirmed:
            await self._repository.transition(
                run_id=run_id,
                status="WAITING_FOR_CONFIRMATION",
                event_type="run.waiting_for_confirmation",
                payload={"phase": "WAITING_FOR_CONFIRMATION"},
            )
            return
        verdict = self._safety_policy.preflight(question)
        if verdict.status != "ALLOWED":
            event_type = (
                "run.safety_escalation" if verdict.status == "SAFETY_ESCALATION" else "run.limited"
            )
            await self._repository.transition(
                run_id=run_id,
                status=verdict.status,
                event_type=event_type,
                payload={"phase": verdict.status, "message": verdict.message},
            )
            return
        plan = self._planner.propose(len(confirmed))
        validate_plan(plan, self._registry.ids())
        await self._repository.record_plan(run_id=run_id, tasks=plan.tasks)
        await self._repository.transition(
            run_id=run_id,
            status="RUNNING",
            event_type="run.progress",
            payload={"phase": "RUNNING", "completed_tasks": 0, "total_tasks": len(plan.tasks)},
        )
        claim_ids: list[str] = []
        for index, (task, medicine) in enumerate(zip(plan.tasks, confirmed, strict=True), start=1):
            current, _ = await self._repository.internal(run_id)
            if current.status == "CANCELLED":
                return
            await self._repository.task_started(task_id=task.task_id)
            claim_id = await self._executor.execute_demo_evidence(
                skill_id=task.skill_id,
                medicine_label=medicine.label,
            )
            await self._repository.task_completed(task_id=task.task_id, output_ref=claim_id)
            await self._repository.link_claim(run_id=run_id, claim_id=claim_id)
            claim_ids.append(claim_id)
            await self._repository.add_verification(
                run_id=run_id,
                claim_id=claim_id,
                verdict="DEMO_ONLY",
                reason=(
                    "Synthetic fixture is visible for software testing and "
                    "is not biomedical evidence."
                ),
            )
            await self._repository.transition(
                run_id=run_id,
                status="VERIFYING",
                event_type="run.evidence_ready",
                payload={
                    "phase": "VERIFYING",
                    "completed_tasks": index,
                    "total_tasks": len(plan.tasks),
                },
            )
        scene_ids = await self._scene_service.compile(
            run_id=run_id,
            claim_ids=claim_ids,
            include_general_skin_scene="skin" in question.lower(),
        )
        if scene_ids:
            await self._repository.transition(
                run_id=run_id,
                status="COMPILING",
                event_type="run.scene_ready",
                payload={"phase": "COMPILING", "scene_ids": scene_ids},
            )
        await self._repository.transition(
            run_id=run_id,
            status="RELIABILITY_CHECK",
            event_type="run.progress",
            payload={"phase": "RELIABILITY_CHECK"},
        )
        report = await self._reliability_service.assess(
            run_id=run_id, claim_ids=claim_ids, scene_ids=scene_ids
        )
        await self._repository.transition(
            run_id=run_id,
            status="LIMITED_ANSWER",
            event_type="run.limited",
            payload={
                "phase": "LIMITED_ANSWER",
                "message": (
                    "Only synthetic demo evidence is available; "
                    "no scientific conclusion is released."
                ),
                "reliability_report_id": report.id,
            },
        )
