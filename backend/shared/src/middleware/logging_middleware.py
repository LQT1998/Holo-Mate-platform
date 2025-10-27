"""Request/response logging middleware for FastAPI applications."""

from __future__ import annotations

import logging
import time
from fastapi import Request, Response
from starlette.types import ASGIApp

from shared.src.config import settings  # Để xác định môi trường (dev/prod)

logger = logging.getLogger("uvicorn.access")


async def request_logging_middleware(request: Request, call_next):
    """Efficient request/response logging middleware.
    
    Features:
    - Logs method, path, status, time
    - Skips static/docs endpoints
    - Environment-aware verbosity
    - Low overhead (function-style)
    """
    # Skip docs and static routes
    if request.url.path.startswith(("/docs", "/openapi", "/static")):
        return await call_next(request)

    start_time = time.perf_counter()

    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path
    query = f"?{request.url.query}" if request.url.query else ""
    full_path = f"{path}{query}"

    # Optional: user ID from auth header (for trace)
    user_id = None
    if "authorization" in request.headers:
        token = request.headers.get("authorization", "")
        user_id = token[-6:]  # ví dụ: hiển thị phần cuối token để ẩn danh

    # Log request
    if settings.ENV.lower() == "dev":
        logger.info(f"➡️  {method} {full_path} | Client: {client_ip} | User: {user_id or 'anon'}")

    try:
        response: Response = await call_next(request)
    except Exception as e:
        duration = (time.perf_counter() - start_time) * 1000
        logger.exception(
            f"💥 {method} {full_path} failed after {duration:.1f}ms: {type(e).__name__}",
            extra={"client_ip": client_ip, "path": path},
        )
        raise

    duration = (time.perf_counter() - start_time) * 1000
    status_code = response.status_code

    # Structured log (can integrate with JSON logger / ELK / Loki)
    log_msg = f"⬅️  {method} {full_path} | {status_code} | {duration:.1f}ms | {client_ip}"

    if status_code >= 500:
        logger.error(log_msg)
    elif status_code >= 400:
        logger.warning(log_msg)
    else:
        if settings.ENV.lower() == "dev":
            logger.info(log_msg)

    return response
