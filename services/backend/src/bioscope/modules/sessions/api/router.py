"""Owner-scoped private session routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status

from bioscope.modules.sessions.api.schemas import (
    AddMessageRequest,
    CreateSessionRequest,
    MessageResponse,
    SessionListResponse,
    SessionResponse,
)
from bioscope.modules.sessions.application.service import SessionDeletionService
from bioscope.modules.sessions.infrastructure.repository import SessionRepository
from bioscope.shared.security.auth import Actor, current_actor

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


def _repository(request: Request) -> SessionRepository:
    return request.app.state.container.session_repository


def _deletion_service(request: Request) -> SessionDeletionService:
    return request.app.state.container.session_deletion_service


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: CreateSessionRequest,
    actor: Actor = Depends(current_actor),
    repository: SessionRepository = Depends(_repository),
) -> SessionResponse:
    record = await repository.create(owner_id=actor.subject, title=payload.title.strip())
    return SessionResponse.model_validate(record, from_attributes=True)


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    actor: Actor = Depends(current_actor),
    repository: SessionRepository = Depends(_repository),
) -> SessionListResponse:
    records = await repository.list(owner_id=actor.subject)
    return SessionListResponse(
        items=[SessionResponse.model_validate(item, from_attributes=True) for item in records]
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    actor: Actor = Depends(current_actor),
    repository: SessionRepository = Depends(_repository),
) -> SessionResponse:
    record = await repository.get(session_id=session_id, owner_id=actor.subject)
    return SessionResponse.model_validate(record, from_attributes=True)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    actor: Actor = Depends(current_actor),
    service: SessionDeletionService = Depends(_deletion_service),
) -> None:
    await service.delete(session_id=session_id, owner_id=actor.subject)


@router.post(
    "/{session_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_message(
    session_id: str,
    payload: AddMessageRequest,
    actor: Actor = Depends(current_actor),
    repository: SessionRepository = Depends(_repository),
) -> MessageResponse:
    record = await repository.add_message(
        session_id=session_id, owner_id=actor.subject, content=payload.content.strip()
    )
    return MessageResponse.model_validate(record, from_attributes=True)
