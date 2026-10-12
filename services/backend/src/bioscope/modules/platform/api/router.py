"""Health endpoints kept separate from infrastructure implementation details."""

from fastapi import APIRouter, Request

from bioscope.shared.api.schemas import ErrorEnvelope, HealthResponse
from bioscope.shared.domain.errors import DependencyUnavailable

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/live", response_model=HealthResponse, summary="Process liveness")
async def live() -> HealthResponse:
    """Report whether this HTTP process can serve requests, without checking dependencies."""

    return HealthResponse(status="live")


@router.get(
    "/ready",
    response_model=HealthResponse,
    responses={503: {"model": ErrorEnvelope}},
    summary="Dependency readiness",
)
async def ready(request: Request) -> HealthResponse:
    """Report whether required Phase 0 dependencies can be reached."""

    if not await request.app.state.container.is_ready():
        raise DependencyUnavailable()
    return HealthResponse(status="ready")
