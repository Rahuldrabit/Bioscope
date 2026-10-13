"""Strict task-DAG validation for workflow plans."""

from __future__ import annotations

from pydantic import BaseModel, Field

from bioscope.shared.domain.errors import InvalidPlan


class TaskSpec(BaseModel):
    task_id: str = Field(pattern=r"^task_[a-z0-9_]+$")
    skill_id: str
    depends_on: list[str] = Field(default_factory=list)
    timeout_ms: int = Field(ge=100, le=30_000)
    max_retries: int = Field(ge=0, le=2)


class TaskPlan(BaseModel):
    schema_version: str = "1.0"
    tasks: list[TaskSpec] = Field(min_length=1, max_length=10)


def validate_plan(plan: TaskPlan, allowed_skill_ids: frozenset[str]) -> None:
    by_id = {task.task_id: task for task in plan.tasks}
    if len(by_id) != len(plan.tasks):
        raise InvalidPlan("Task IDs must be unique.")
    for task in plan.tasks:
        if task.skill_id not in allowed_skill_ids:
            raise InvalidPlan("The workflow requested an unknown skill.")
        if task.task_id in task.depends_on:
            raise InvalidPlan("A task cannot depend on itself.")
        if any(dependency not in by_id for dependency in task.depends_on):
            raise InvalidPlan("A task depends on a missing prerequisite.")
    _assert_acyclic(by_id)


def _assert_acyclic(tasks: dict[str, TaskSpec]) -> None:
    visited: set[str] = set()
    active: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in active:
            raise InvalidPlan("The workflow task graph contains a cycle.")
        if task_id in visited:
            return
        active.add(task_id)
        for dependency in tasks[task_id].depends_on:
            visit(dependency)
        active.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        visit(task_id)
