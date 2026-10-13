"""Candidate identity routes with explicit user confirmation."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status

from bioscope.modules.medicines.api.schemas import (
    AddMedicineCandidateRequest,
    ConfirmCandidateRequest,
    ConfirmedMedicationResponse,
    EntityCandidatesResponse,
    MedicineCandidateResponse,
)
from bioscope.modules.medicines.application.service import MedicineIntakeService
from bioscope.modules.medicines.infrastructure.repository import MedicineRepository
from bioscope.shared.security.auth import Actor, current_actor

router = APIRouter(prefix="/api/v1/sessions/{session_id}", tags=["medicines"])


def _repository(request: Request) -> MedicineRepository:
    return request.app.state.container.medicine_repository


def _service(request: Request) -> MedicineIntakeService:
    return request.app.state.container.medicine_intake_service


@router.post(
    "/medicine-items",
    response_model=MedicineCandidateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_medicine_item(
    session_id: str,
    payload: AddMedicineCandidateRequest,
    actor: Actor = Depends(current_actor),
    service: MedicineIntakeService = Depends(_service),
) -> MedicineCandidateResponse:
    candidate = await service.add_text_candidate(
        session_id=session_id, owner_id=actor.subject, raw_text=payload.label
    )
    return MedicineCandidateResponse.model_validate(candidate, from_attributes=True)


@router.get("/entity-candidates", response_model=EntityCandidatesResponse)
async def list_entity_candidates(
    session_id: str,
    actor: Actor = Depends(current_actor),
    repository: MedicineRepository = Depends(_repository),
) -> EntityCandidatesResponse:
    candidates = await repository.list_candidates(session_id=session_id, owner_id=actor.subject)
    confirmed = await repository.list_confirmed(session_id=session_id, owner_id=actor.subject)
    return EntityCandidatesResponse(
        candidates=[
            MedicineCandidateResponse.model_validate(item, from_attributes=True)
            for item in candidates
        ],
        confirmed=[
            ConfirmedMedicationResponse.model_validate(item, from_attributes=True)
            for item in confirmed
        ],
    )


@router.post("/confirm-entities", response_model=ConfirmedMedicationResponse)
async def confirm_entity(
    session_id: str,
    payload: ConfirmCandidateRequest,
    actor: Actor = Depends(current_actor),
    repository: MedicineRepository = Depends(_repository),
) -> ConfirmedMedicationResponse:
    confirmed = await repository.confirm(
        session_id=session_id,
        candidate_id=payload.candidate_id,
        owner_id=actor.subject,
        expected_session_version=payload.expected_session_version,
    )
    return ConfirmedMedicationResponse.model_validate(confirmed, from_attributes=True)
