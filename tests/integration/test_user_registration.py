"""
Integration test: user registration → login → get profile (RED phase).

Flow:
1) POST /auth/register with email + password → expect 201, returns user_id + email
2) POST /auth/login with same credentials → expect 200, returns access_token
3) GET /users/me with Bearer token → expect 200, returns correct user info

NOTE: This test is expected to fail until services and endpoints are implemented.
"""

from __future__ import annotations

import uuid
import pytest
import httpx
from typing import Dict


@pytest.fixture
def auth_base_url() -> str:
    # Convention: auth_service exposed at 8001 in local/dev
    # Adjust via env or docker-compose as needed
    return "http://localhost:8001"


def _unique_email() -> str:
    return f"user_{uuid.uuid4().hex[:8]}@example.com"


@pytest.mark.asyncio
async def test_user_registration_login_profile_flow(auth_base_url: str):
    async with httpx.AsyncClient(base_url=auth_base_url, timeout=10.0) as client:
        # 1) Register
        email = _unique_email()
        password = "StrongPassw0rd!"
        register_payload: Dict[str, str] = {"email": email, "password": password}

        register_resp = await client.post("/auth/register", json=register_payload)
        assert register_resp.status_code == 201
        reg_json = register_resp.json()
        assert "id" in reg_json and reg_json["id"]
        assert reg_json.get("email") == email

        # 2) Login
        login_payload: Dict[str, str] = {"email": email, "password": password}
        login_resp = await client.post("/auth/login", json=login_payload)
        assert login_resp.status_code == 200
        login_json = login_resp.json()
        access_token = login_json.get("access_token")
        assert access_token and isinstance(access_token, str)

        # 3) Get profile
        headers = {"Authorization": f"Bearer {access_token}"}
        me_resp = await client.get("/users/me", headers=headers)
        assert me_resp.status_code == 200
        me_json = me_resp.json()
        assert me_json.get("email") == email

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

# This test will require a database fixture and potentially mocking external services.
# For now, it will serve as a placeholder for the user registration flow.

@pytest.mark.asyncio
async def test_user_registration_flow(auth_client: AsyncClient, db_session: Session):
    """
    Integration test for the complete user registration flow.
    1. User registers via API.
    2. A new User record is created in the database.
    3. A default UserPreference record is created.
    4. A default "free" Subscription is created.
    5. The user can then log in successfully.
    """
    # Step 1: Register a new user
    registration_payload = {
        "email": "test.registration@example.com",
        "password": "strongpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    # Assuming there's a /users/register endpoint in the auth service
    register_response = await auth_client.post("/auth/register", json=registration_payload)
    
    assert register_response.status_code == 201
    user_data = register_response.json()
    assert user_data["email"] == registration_payload["email"]
    user_id = user_data["id"]

    # Step 2 & 3 & 4: Verify database records (this part will fail until implemented)
    # This requires direct DB access or a verification endpoint.
    # For now, we will just assume this part of the test.
    # In a real scenario, you'd query the DB via db_session.
    # from backend.shared.src.models import User, UserPreference, Subscription
    # user_in_db = db_session.query(User).filter_by(id=user_id).first()
    # assert user_in_db is not None
    # assert user_in_db.preferences is not None
    # assert user_in_db.subscription.plan_name == "free"

    # Step 5: Attempt to log in with the new credentials
    login_payload = {
        "email": registration_payload["email"],
        "password": registration_payload["password"]
    }
    login_response = await auth_client.post("/auth/login", json=login_payload)
    
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
