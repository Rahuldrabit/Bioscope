"""FastAPI application factory for BioScope."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bioscope.bootstrap.container import ApplicationContainer
from bioscope.bootstrap.lifespan import application_lifespan
from bioscope.bootstrap.settings import Settings, get_settings
from bioscope.modules.agent_workflows.api.router import router as workflows_router
from bioscope.modules.evidence.api.router import router as evidence_router
from bioscope.modules.medicines.api.router import router as medicines_router
from bioscope.modules.platform.api.router import router as health_router
from bioscope.modules.reliability.api.router import router as reliability_router
from bioscope.modules.sessions.api.router import router as sessions_router
from bioscope.modules.skin.api.router import router as skin_router
from bioscope.modules.uploads.api.router import router as uploads_router
from bioscope.modules.visualization.api.router import router as scenes_router
from bioscope.shared.api.error_handlers import register_error_handlers


def create_app(
    settings: Settings | None = None,
    container: ApplicationContainer | None = None,
) -> FastAPI:
    """Build an app with validated settings and dependency-injected infrastructure."""

    resolved_settings = settings or get_settings()
    app = FastAPI(
        title="BioScope AI API",
        version="0.1.0",
        description=(
            "Educational biomedical exploration API. Local demo identity and fixtures are clearly "
            "labeled; it does not provide diagnosis, treatment, or medication advice."
        ),
        lifespan=application_lifespan,
    )
    app.state.container = container or ApplicationContainer(resolved_settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "Idempotency-Key", "X-Request-ID"],
    )
    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(sessions_router)
    app.include_router(skin_router)
    app.include_router(uploads_router)
    app.include_router(medicines_router)
    app.include_router(evidence_router)
    app.include_router(workflows_router)
    app.include_router(reliability_router)
    app.include_router(scenes_router)
    return app


app = create_app()
