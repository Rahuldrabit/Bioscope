"""FastAPI application factory for BioScope."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bioscope.bootstrap.container import ApplicationContainer
from bioscope.bootstrap.lifespan import application_lifespan
from bioscope.bootstrap.settings import Settings, get_settings
from bioscope.modules.platform.api.router import router as health_router
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
            "Phase 0 platform API. It provides health and platform contracts only; "
            "it does not perform biomedical inference."
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
    return app


app = create_app()
