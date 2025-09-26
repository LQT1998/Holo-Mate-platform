"""Integration tests for JWT authentication middleware."""

from __future__ import annotations

import os
import sys
from datetime import timedelta
from typing import AsyncGenerator

import httpx
import pytest
import pytest_asyncio

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from backend.auth_service.main import create_app
from backend.shared.src.security.jwt import create_access_token


@pytest_asyncio.fixture(scope="function")
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    app = create_app()
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_missing_token_returns_401(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/auth/profile")
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


@pytest.mark.asyncio
async def test_invalid_token_returns_401(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/auth/profile", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert response.json().get("detail") == "Invalid authentication credentials"


@pytest.mark.asyncio
async def test_valid_token_sets_request_state_user(http_client: httpx.AsyncClient) -> None:
    token = create_access_token({"sub": "test-user"}, expires_delta=timedelta(minutes=1))
    response = await http_client.get(
        "/auth/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json().get("user", {}).get("sub") == "test-user"

