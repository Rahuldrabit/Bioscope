"""Owner-scoped reliability report endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from bioscope.modules.reliability.api.schemas import ReliabilityReportResponse
from bioscope.modules.reliability.infrastructure.repository import ReliabilityRepository
from bioscope.shared.security.auth import Actor, current_actor

router = APIRouter(tags=["reliability"])


def _repository(request: Request) -> ReliabilityRepository:
    return request.app.state.container.reliability_repository


@router.get("/api/v1/runs/{run_id}/reliability", response_model=ReliabilityReportResponse)
async def get_reliability(
    run_id: str,
    actor: Actor = Depends(current_actor),
    repository: ReliabilityRepository = Depends(_repository),
) -> ReliabilityReportResponse:
    return ReliabilityReportResponse.model_validate(
        (await repository.get_for_run(run_id=run_id, owner_id=actor.subject)).as_dict()
    )
