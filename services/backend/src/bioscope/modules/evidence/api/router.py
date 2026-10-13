"""Read-only public-science evidence routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from bioscope.modules.evidence.api.schemas import ClaimResponse, EntityResponse, SourceResponse
from bioscope.modules.evidence.infrastructure.repository import EvidenceRepository
from bioscope.shared.domain.errors import ResourceForbidden

router = APIRouter(tags=["evidence"])


def _repository(request: Request) -> EvidenceRepository:
    return request.app.state.container.evidence_repository


@router.get("/api/v1/claims/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: str, repository: EvidenceRepository = Depends(_repository)
) -> ClaimResponse:
    claim = await repository.get_claim(claim_id)
    if claim is None:
        raise ResourceForbidden()
    return ClaimResponse.model_validate(claim)


@router.get("/api/v1/sources/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: str, repository: EvidenceRepository = Depends(_repository)
) -> SourceResponse:
    source = await repository.get_source(source_id)
    if source is None:
        raise ResourceForbidden()
    return SourceResponse.model_validate(source)


@router.get("/api/v1/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str, repository: EvidenceRepository = Depends(_repository)
) -> EntityResponse:
    entity = await repository.get_entity(entity_id)
    if entity is None:
        raise ResourceForbidden()
    return EntityResponse.model_validate(entity)
