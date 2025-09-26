"""
Contract test for PUT /users/me endpoint
Tests the user profile update API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any
from datetime import datetime, timedelta, timezone

# Import JWT helpers for token generation
from backend.shared.src.security.security import create_access_token


class TestPutUsersMe:
    """Contract tests for PUT /users/me endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for auth service"""
        return "http://localhost:8001"
    
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
    
    @pytest.fixture
    def valid_update_data(self) -> Dict[str, Any]:
        """Valid user update data (only allowed fields)"""
        return {
            "first_name": "Updated",
            "last_name": "User"
        }
    
    @pytest.fixture
    def invalid_update_data(self) -> Dict[str, Any]:
        """Invalid user update data for validation testing"""
        return {
            "first_name": "",  # Empty string should fail validation
            "last_name": "A",  # Too short
            "email": "invalid-email"  # Invalid email format
        }
    
    @pytest.fixture
    def password_update_data(self) -> Dict[str, Any]:
        """Data attempting to update password (should be rejected)"""
        return {
            "first_name": "Updated",
            "last_name": "User",
            "password": "newpassword123"  # Should be rejected
        }
    
    @pytest.fixture
    def restricted_field_data(self) -> Dict[str, Any]:
        """Data attempting to update restricted fields (should be rejected)"""
        return {
            "first_name": "Updated",
            "last_name": "User",
            "id": "new-id-123",  # Should be rejected
            "created_at": "2023-01-01T00:00:00Z",  # Should be rejected
            "is_active": False  # Should be rejected
        }

    @pytest.mark.asyncio
    async def test_put_user_me_success_returns_200_and_updated_data(
        self, 
        auth_base_url: str, 
        valid_access_token: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test successful user profile update returns 200 with updated data"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                },
                json=valid_update_data
            )
            
            # Should return 200 OK
            assert response.status_code == 200
            
            # Should return JSON response
            data = response.json()
            assert isinstance(data, dict)
            
            # Should contain updated fields
            assert "id" in data
            assert isinstance(data["id"], (str, int))
            
            assert "email" in data
            # Email should remain unchanged (not updatable)
            assert isinstance(data["email"], str) and len(data["email"]) > 0
            
            assert "first_name" in data
            assert data["first_name"] == valid_update_data["first_name"]
            
            assert "last_name" in data
            assert data["last_name"] == valid_update_data["last_name"]
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            
            # Should not contain sensitive fields
            sensitive_fields = ["password", "password_hash", "hashed_password", "salt"]
            for field in sensitive_fields:
                assert field not in data, f"Sensitive field exposed: {field}"

    @pytest.mark.asyncio
    async def test_put_user_me_invalid_data_returns_422(
        self, 
        auth_base_url: str, 
        valid_access_token: str,
        invalid_update_data: Dict[str, Any]
    ):
        """Test invalid data returns 422 validation error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                },
                json=invalid_update_data
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], (list, dict))

    @pytest.mark.asyncio
    async def test_put_user_me_missing_auth_returns_401(
        self, 
        auth_base_url: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{auth_base_url}/users/me",
                headers={"Content-Type": "application/json"},
                json=valid_update_data
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
    async def test_put_user_me_invalid_token_returns_401(
        self, 
        auth_base_url: str, 
        invalid_access_token: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {invalid_access_token}",
                    "Content-Type": "application/json"
                },
                json=valid_update_data
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
    async def test_put_user_me_expired_token_returns_401(
        self, 
        auth_base_url: str, 
        expired_access_token: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test expired access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {expired_access_token}",
                    "Content-Type": "application/json"
                },
                json=valid_update_data
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
    async def test_put_user_me_password_update_rejected(
        self, 
        auth_base_url: str, 
        valid_access_token: str,
        password_update_data: Dict[str, Any]
    ):
        """Test that password update is rejected (422 or 400)"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                },
                json=password_update_data
            )
            
            # Should return 422 (validation error) or 400 (bad request)
            assert response.status_code in [400, 422]
            
            # Should return error message about password update not allowed
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], (str, list))

    @pytest.mark.asyncio
    async def test_put_user_me_restricted_fields_rejected(
        self, 
        auth_base_url: str, 
        valid_access_token: str,
        restricted_field_data: Dict[str, Any]
    ):
        """Test that restricted fields (id, created_at, is_active) are rejected"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                },
                json=restricted_field_data
            )
            
            # Should return 422 (validation error) or 400 (bad request)
            assert response.status_code in [400, 422]
            
            # Should return error message about restricted fields
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], (str, list))

    @pytest.mark.asyncio
    async def test_put_user_me_partial_update_allowed(
        self, 
        auth_base_url: str, 
        valid_access_token: str
    ):
        """Test that partial updates (only some fields) are allowed"""
        partial_data = {
            "first_name": "OnlyFirstName"
            # Only updating first_name, not last_name or email
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{auth_base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                },
                json=partial_data
            )
            
            # Should return 200 OK for partial update
            assert response.status_code == 200
            
            # Should return updated data
            data = response.json()
            assert isinstance(data, dict)
            assert data["first_name"] == partial_data["first_name"]