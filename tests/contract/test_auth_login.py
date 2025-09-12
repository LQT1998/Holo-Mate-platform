"""
Contract test for POST /auth/login endpoint
Tests the authentication login API contract before implementation
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Tuple

from shared_lib.models.user import User
from app.security import get_password_hash

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Fixture to create a user and return the user object."""
    password = "validpassword123"
    user = User(
        email="test@example.com", 
        username="testuser",
        hashed_password=get_password_hash(password), 
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

class TestAuthLogin:
    
    async def test_login_success_returns_200_and_tokens(
        self, 
        client: TestClient, 
        test_user: User
    ):
        login_data = {"email_or_username": test_user.email, "password": "validpassword123"}
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_login_invalid_credentials_returns_401(self, client: TestClient, test_user: User):
        invalid_data = {"email_or_username": test_user.email, "password": "wrongpassword"}
        response = client.post("/auth/login", json=invalid_data)
        assert response.status_code == 401

    async def test_login_nonexistent_user_returns_401(self, client: TestClient):
        nonexistent_user_data = {
            "email_or_username": "nonexistent@example.com",
            "password": "somepassword"
        }
        response = client.post("/auth/login", json=nonexistent_user_data)
        assert response.status_code == 401

    async def test_login_inactive_user_returns_401(
        self, client: TestClient, db_session: AsyncSession, test_user: User
    ):
        test_user.is_active = False
        db_session.add(test_user)
        await db_session.commit()

        login_data = {"email_or_username": test_user.email, "password": "validpassword123"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401

    async def test_login_missing_fields_returns_422(self, client: TestClient):
        response = client.post("/auth/login", json={"email_or_username": "test@example.com"})
        assert response.status_code == 422
        
        response = client.post("/auth/login", json={"password": "password"})
        assert response.status_code == 422
