"""CORS middleware configuration for FastAPI applications."""

from __future__ import annotations
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware


def setup_cors_middleware(
    app,
    allow_origins: Optional[List[str]] = None,
    allow_credentials: bool = True,
    allow_methods: Optional[List[str]] = None,
    allow_headers: Optional[List[str]] = None,
    expose_headers: Optional[List[str]] = None,
    max_age: int = 86400,
) -> None:
    """Attach a secure and optimized CORS middleware to a FastAPI app."""
    
    # Default allowed origins (development + production)
    if allow_origins is None:
        allow_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
            "https://holomate.dev",
            "https://www.holomate.dev",
        ]
    
    # Default methods
    if allow_methods is None:
        allow_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    
    # Default allowed headers
    if allow_headers is None:
        allow_headers = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRFToken",
        ]
    
    # Default exposed headers
    if expose_headers is None:
        expose_headers = ["X-Total-Count", "X-Page-Count", "X-Current-Page"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        expose_headers=expose_headers,
        max_age=max_age,
    )
