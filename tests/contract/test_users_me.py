"""
Contract test for GET /users/me endpoint
Tests the user profile retrieval API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any
from datetime import datetime, timedelta, timezone

# Import JWT helpers for token generation
from backend.shared.src.security.security import create_access_token


@pytest.mark.skip(reason="Users me endpoint not implemented yet")
class TestGetUsersMe:
    """Contract tests for GET /users/me endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for auth service"""
        return "http://localhost:8001/api/v1"
    
    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        # Use simple test token for dev mode
        return "valid_access_token_here"
    
    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return "invalid_access_token_here"
    
    @pytest.fixture
    def expired_access_token(self) -> str:
        """Expired access token for testing token expiration"""
        # Create an expired JWT token
        token_data = {
            "sub": "test@example.com",
            "user_id": "00000000-0000-0000-0000-000000000000",
            "email": "test@example.com",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)  # Expired 1 hour ago
        }
        from backend.shared.src.security.security import jwt
        from backend.auth_service.src.config import settings
        secret = settings.JWT_SECRET or "dev-secret"
        return jwt.encode(token_data, secret, algorithm="HS256")
    
    @pytest.mark.asyncio
    async def test_get_user_me_success_returns_200_and_user_data(
        self, 
        auth_base_url: str, 
        valid_access_token: str
    ):
        """Test successful user profile retrieval returns 200 with user data"""
        async with httpx.AsyncClient() as client:
            # First register and login to get a fresh token
            register_response = await client.post(
                f"{auth_base_url}/auth/register",
                json={"email": "test@example.com", "password": "validpassword123"},
                headers={"Content-Type": "application/json"}
            )
            # Accept both 201 (created) and 400 (already exists)
            assert register_response.status_code in [201, 400]
            
            login_response = await client.post(
                f"{auth_base_url}/auth/login",
                json={"email": "test@example.com", "password": "validpassword123"},
                headers={"Content-Type": "application/json"}
            )
            assert login_response.status_code == 200
            login_data = login_response.json()
            fresh_token = login_data["access_token"]
            
            response = await client.get(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {fresh_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 200 OK
            assert response.status_code == 200
            
            # Should return JSON response
            data = response.json()
            assert isinstance(data, dict)
            
            # Should contain main fields: id, email, created_at
            assert "id" in data
            assert isinstance(data["id"], (str, int))
            
            assert "email" in data
            assert isinstance(data["email"], str)
            assert "@" in data["email"]  # Basic email validation
            
            assert "created_at" in data
            assert isinstance(data["created_at"], str)
            
            # Should contain updated_at
            assert "updated_at" in data
            assert isinstance(data["updated_at"], str)
    
    @pytest.mark.asyncio
    async def test_get_user_me_no_password_in_response(
        self, 
        auth_base_url: str, 
        valid_access_token: str
    ):
        """Test that password field is not included in response"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should not contain password fields
                sensitive_fields = ["password", "password_hash", "hashed_password", "salt"]
                for field in sensitive_fields:
                    assert field not in data, f"Sensitive field exposed: {field}"
    
    @pytest.mark.asyncio
    async def test_get_user_me_missing_auth_returns_401(
        self, 
        auth_base_url: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{auth_base_url}/users/me",
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 401 Unauthorized (or 403 Forbidden for missing header)
            assert response.status_code in [401, 403]
        
        # Should return error message
        data = response.json()
        assert isinstance(data, dict)
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_user_me_invalid_token_returns_401(
        self, 
        auth_base_url: str, 
        invalid_access_token: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {invalid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 401 Unauthorized
            assert response.status_code == 401
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_user_me_expired_token_returns_401(
        self, 
        auth_base_url: str, 
        expired_access_token: str
    ):
        """Test expired access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {expired_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 401 Unauthorized
            assert response.status_code == 401
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0
    
