"""Error handling middleware for FastAPI applications."""

from __future__ import annotations

import logging
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException

from shared.src.config import settings  # ✅ import once

logger = logging.getLogger(__name__)


async def error_handling_middleware(request: Request, call_next: Callable):
    """Global error handling middleware.
    
    Features:
    - Unified JSON error responses
    - Detailed logging (with path, client, method)
    - Environment-aware masking (prod vs dev)
    - Handles FastAPI/Starlette & generic exceptions
    """
    try:
        response = await call_next(request)
        return response

    except HTTPException as e:
        # Keep original FastAPI HTTPException details
        logger.warning(f"HTTP {e.status_code}: {e.detail} ({request.method} {request.url.path})")
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail, "error_type": type(e).__name__},
        )

    except RequestValidationError as e:
        # Validation error (e.g., invalid body/query params)
        logger.warning(f"Validation error: {str(e)} ({request.method} {request.url.path})")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": e.errors(), "error_type": "RequestValidationError"},
        )

    except Exception as e:
        # Log critical unexpected errors
        logger.exception(
            f"Unhandled exception in {request.method} {request.url.path}: {str(e)}",
            extra={
                "client": request.client.host if request.client else "unknown",
                "path": request.url.path,
            },
        )

        # Build safe response
        error_detail = {
            "detail": "Internal server error",
            "error_type": type(e).__name__,
        }

        if settings.ENV.lower() == "dev":
            error_detail["message"] = str(e)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_detail,
        )
