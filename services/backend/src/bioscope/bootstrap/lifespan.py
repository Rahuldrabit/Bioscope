"""FastAPI lifespan management."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from bioscope.bootstrap.container import ApplicationContainer


@asynccontextmanager
async def application_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create long-lived adapters once and dispose of them predictably."""

    container: ApplicationContainer = app.state.container
    try:
        yield
    finally:
        await container.close()
