import pytest


@pytest.mark.asyncio
async def test_register_201_and_no_password(client):
    payload = {"email": "local@example.com", "password": "secret123"}
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data.get("email") == payload["email"]
    assert "password" not in data


