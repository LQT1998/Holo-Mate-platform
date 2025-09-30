"""
Contract test for POST /auth/register

Payload:
  { "email": "user@example.com", "password": "secret123" }

Expect:
  - HTTP 201
  - JSON has fields: id, email
  - MUST NOT contain password

This test is expected to be RED until the endpoint is implemented.
"""

from __future__ import annotations

import httpx
import pytest


@pytest.fixture
def base_url() -> str:
    # Convention: auth service at localhost:8001
    return "http://localhost:8001/api/v1"


@pytest.mark.asyncio
async def test_auth_register_returns_201_and_user_without_password(base_url: str):
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        payload = {"email": "user@example.com", "password": "secret123"}
        resp = await client.post("/auth/register", json=payload)

        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data and data["id"]
        assert data.get("email") == payload["email"]
        assert "password" not in data


