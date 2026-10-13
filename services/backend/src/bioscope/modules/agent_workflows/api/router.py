"""Owner-scoped workflow routes and replayable SSE events."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, BackgroundTasks, Depends, Header, Request, status
from fastapi.responses import StreamingResponse

from bioscope.modules.agent_workflows.api.schemas import (
    RunClaimsResponse,
    RunEventResponse,
    RunResponse,
    StartRunRequest,
)
from bioscope.modules.agent_workflows.application.runner import WorkflowRunner
from bioscope.modules.agent_workflows.domain.models import WorkflowRun
from bioscope.modules.agent_workflows.infrastructure.repository import WorkflowRepository
from bioscope.shared.security.auth import Actor, current_actor

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


def _repository(request: Request) -> WorkflowRepository:
    return request.app.state.container.workflow_repository


def _runner(request: Request) -> WorkflowRunner:
    return request.app.state.container.workflow_runner


def _response(run: WorkflowRun) -> RunResponse:
    return RunResponse(
        id=run.id,
        session_id=run.session_id,
        status=run.status,
        created_at=run.created_at,
        updated_at=run.updated_at,
        events_url=f"/api/v1/runs/{run.id}/events",
    )


@router.post("", response_model=RunResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_run(
    payload: StartRunRequest,
    background_tasks: BackgroundTasks,
    actor: Actor = Depends(current_actor),
    repository: WorkflowRepository = Depends(_repository),
    runner: WorkflowRunner = Depends(_runner),
) -> RunResponse:
    run = await repository.create(
        session_id=payload.session_id,
        owner_id=actor.subject,
        question=payload.question,
        message_id=payload.message_id,
    )
    background_tasks.add_task(runner.execute, run.id)
    return _response(run)


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: str,
    actor: Actor = Depends(current_actor),
    repository: WorkflowRepository = Depends(_repository),
) -> RunResponse:
    return _response(await repository.get(run_id=run_id, owner_id=actor.subject))


@router.post("/{run_id}/cancel", response_model=RunResponse)
async def cancel_run(
    run_id: str,
    actor: Actor = Depends(current_actor),
    repository: WorkflowRepository = Depends(_repository),
) -> RunResponse:
    return _response(await repository.cancel(run_id=run_id, owner_id=actor.subject))


@router.get("/{run_id}/claims", response_model=RunClaimsResponse)
async def get_run_claims(
    run_id: str,
    actor: Actor = Depends(current_actor),
    repository: WorkflowRepository = Depends(_repository),
) -> RunClaimsResponse:
    return RunClaimsResponse(
        claim_ids=await repository.claim_ids(run_id=run_id, owner_id=actor.subject)
    )


@router.get("/{run_id}/events")
async def stream_events(
    run_id: str,
    actor: Actor = Depends(current_actor),
    repository: WorkflowRepository = Depends(_repository),
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
) -> StreamingResponse:
    after = int(last_event_id) if last_event_id and last_event_id.isdigit() else 0
    events = await repository.events(run_id=run_id, owner_id=actor.subject, after_sequence=after)

    async def event_stream() -> AsyncIterator[str]:
        for event in events:
            payload = RunEventResponse(
                event_id=event.id,
                run_id=event.run_id,
                sequence=event.sequence,
                type=event.event_type,
                occurred_at=event.occurred_at,
                payload=event.payload,
            ).model_dump(mode="json")
            yield (
                f"id: {event.sequence}\nevent: {event.event_type}\ndata: {json.dumps(payload)}\n\n"
            )

    return StreamingResponse(event_stream(), media_type="text/event-stream")
