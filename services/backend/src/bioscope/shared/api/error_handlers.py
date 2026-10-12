"""Consistent, privacy-safe FastAPI error responses."""

from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from bioscope.shared.api.schemas import ErrorDetail, ErrorEnvelope
from bioscope.shared.domain.errors import AppError

logger = logging.getLogger(__name__)


def trace_id_for(request: Request) -> str:
    """Use an opaque supplied request ID or generate one; never use payload data."""

    return request.headers.get("X-Request-ID", str(uuid4()))


def error_response(
    *,
    request: Request,
    status_code: int,
    code: str,
    message: str,
    retryable: bool = False,
    details: dict[str, object] | None = None,
    trace_id: str | None = None,
) -> JSONResponse:
    resolved_trace_id = trace_id or trace_id_for(request)
    envelope = ErrorEnvelope(
        error=ErrorDetail(
            code=code,
            message=message,
            retryable=retryable,
            details=details or {},
            trace_id=resolved_trace_id,
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=envelope.model_dump(mode="json"),
        headers={"X-Request-ID": resolved_trace_id},
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register only safe, standardized error serialization."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, error: AppError) -> JSONResponse:
        return error_response(
            request=request,
            status_code=error.status_code,
            code=error.code,
            message=error.message,
            retryable=error.retryable,
            details=error.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        return error_response(
            request=request,
            status_code=422,
            code="VALIDATION_ERROR",
            message="The request could not be validated.",
            details={"fields": [item["loc"] for item in error.errors()]},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, error: StarletteHTTPException) -> JSONResponse:
        if error.status_code == 404:
            code, message = "RESOURCE_NOT_FOUND", "The requested resource was not found."
        else:
            code, message = "HTTP_ERROR", "The request could not be completed."
        return error_response(
            request=request,
            status_code=error.status_code,
            code=code,
            message=message,
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, error: Exception) -> JSONResponse:
        trace_id = trace_id_for(request)
        logger.exception("Unhandled application error", extra={"trace_id": trace_id})
        return error_response(
            request=request,
            status_code=500,
            code="INTERNAL_ERROR",
            message="The request could not be completed.",
            trace_id=trace_id,
        )
