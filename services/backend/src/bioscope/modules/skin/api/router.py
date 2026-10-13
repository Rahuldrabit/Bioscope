"""Private opt-in skin observation endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from bioscope.modules.skin.api.schemas import (
    CreateSkinObservationRequest,
    SkinObservationResponse,
)
from bioscope.modules.skin.application.service import SkinObservationService
from bioscope.shared.security.auth import Actor, current_actor

router = APIRouter(prefix="/api/v1/sessions", tags=["skin-observations"])


def _service(request: Request) -> SkinObservationService:
    return request.app.state.container.skin_observation_service


@router.post("/{session_id}/skin-observations", response_model=SkinObservationResponse)
async def create_skin_observation(
    session_id: str,
    payload: CreateSkinObservationRequest,
    actor: Actor = Depends(current_actor),
    service: SkinObservationService = Depends(_service),
) -> SkinObservationResponse:
    result = await service.observe(
        session_id=session_id,
        owner_id=actor.subject,
        asset_id=payload.asset_id,
        question=payload.question,
    )
    return SkinObservationResponse.model_validate(result.as_dict())
