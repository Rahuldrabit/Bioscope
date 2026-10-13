"""Private asset upload and metadata routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status

from bioscope.modules.uploads.api.schemas import (
    AssetResponse,
    CreateUploadIntentRequest,
    UploadIntentResponse,
)
from bioscope.modules.uploads.application.service import UploadService
from bioscope.modules.uploads.infrastructure.repository import AssetRepository
from bioscope.shared.security.auth import Actor, current_actor

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


def _repository(request: Request) -> AssetRepository:
    return request.app.state.container.asset_repository


def _service(request: Request) -> UploadService:
    return request.app.state.container.upload_service


@router.post(
    "/upload-intents",
    response_model=UploadIntentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_upload_intent(
    payload: CreateUploadIntentRequest,
    request: Request,
    actor: Actor = Depends(current_actor),
    repository: AssetRepository = Depends(_repository),
) -> UploadIntentResponse:
    asset, token = await repository.create_intent(
        session_id=payload.session_id,
        owner_id=actor.subject,
        filename=payload.filename,
        content_type=payload.content_type,
        consent_sensitive_processing=payload.consent_sensitive_processing,
        retention_days=request.app.state.container.settings.asset_retention_days,
    )
    return UploadIntentResponse(
        asset_id=asset.id,
        upload_token=token,
        content_endpoint=f"/api/v1/assets/{asset.id}/content",
    )


@router.post("/{asset_id}/content", response_model=AssetResponse)
async def upload_content(
    asset_id: str,
    request: Request,
    file: UploadFile = File(...),
    upload_token: str = Form(...),
    actor: Actor = Depends(current_actor),
    service: UploadService = Depends(_service),
) -> AssetResponse:
    content = await file.read()
    asset = await service.complete(
        asset_id=asset_id,
        owner_id=actor.subject,
        upload_token=upload_token,
        content=content,
        content_type=file.content_type or "",
    )
    await request.app.state.container.medicine_intake_service.recognize_demo_fixture(
        session_id=asset.session_id,
        owner_id=actor.subject,
        asset_id=asset.id,
        filename=asset.original_filename,
    )
    return AssetResponse.model_validate(asset, from_attributes=True)


@router.post("/{asset_id}/complete", response_model=AssetResponse)
async def complete_upload(
    asset_id: str,
    actor: Actor = Depends(current_actor),
    repository: AssetRepository = Depends(_repository),
) -> AssetResponse:
    """Return validated metadata after the private content endpoint has completed."""

    asset = await repository.get(asset_id=asset_id, owner_id=actor.subject)
    return AssetResponse.model_validate(asset, from_attributes=True)


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    actor: Actor = Depends(current_actor),
    repository: AssetRepository = Depends(_repository),
) -> AssetResponse:
    asset = await repository.get(asset_id=asset_id, owner_id=actor.subject)
    return AssetResponse.model_validate(asset, from_attributes=True)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: str,
    actor: Actor = Depends(current_actor),
    service: UploadService = Depends(_service),
) -> None:
    await service.delete(asset_id=asset_id, owner_id=actor.subject)
