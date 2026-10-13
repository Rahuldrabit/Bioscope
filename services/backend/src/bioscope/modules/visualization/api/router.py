"""Owner-scoped validated scene retrieval routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from bioscope.modules.visualization.api.schemas import (
    SceneListItem,
    SceneListResponse,
    SceneSpecResponse,
)
from bioscope.modules.visualization.infrastructure.repository import SceneRepository
from bioscope.shared.security.auth import Actor, current_actor

router = APIRouter(tags=["scenes"])


def _repository(request: Request) -> SceneRepository:
    return request.app.state.container.scene_repository


@router.get("/api/v1/runs/{run_id}/scenes", response_model=SceneListResponse)
async def list_scenes(
    run_id: str,
    actor: Actor = Depends(current_actor),
    repository: SceneRepository = Depends(_repository),
) -> SceneListResponse:
    items = await repository.list_for_run(run_id=run_id, owner_id=actor.subject)
    return SceneListResponse(items=[SceneListItem.model_validate(item) for item in items])


@router.get("/api/v1/scenes/{scene_id}", response_model=SceneSpecResponse)
async def get_scene(
    scene_id: str,
    actor: Actor = Depends(current_actor),
    repository: SceneRepository = Depends(_repository),
) -> SceneSpecResponse:
    spec = await repository.get(scene_id=scene_id, owner_id=actor.subject)
    return SceneSpecResponse.model_validate(spec)
