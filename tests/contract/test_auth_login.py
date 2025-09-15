"""
Contract test for POST /auth/login endpoint
Tests the authentication login API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestAuthLoginContract:
    """Contract tests for POST /auth/login endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for auth service"""
        return "http://localhost:8001"
    
    @pytest.fixture
    def valid_login_data(self) -> Dict[str, str]:
        """Valid login request data"""
        return {
            "email": "test@example.com",
            "password": "validpassword123"
        }
    
    @pytest.fixture
    def invalid_login_data(self) -> Dict[str, str]:
        """Invalid login request data"""
        return {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    
    @pytest.fixture
    def malformed_login_data(self) -> Dict[str, Any]:
        """Malformed login request data"""
        return {
            "email": "invalid-email",
            "password": ""
        }
    
    @pytest.mark.asyncio
    async def test_login_success_returns_200_and_tokens(
        self, 
        base_url: str, 
        valid_login_data: Dict[str, str]
    ):
        """Test successful login returns 200 with access and refresh tokens"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/login",
                json=valid_login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 200 OK
            assert response.status_code == 200
            
            # Should return JSON response
            data = response.json()
            assert isinstance(data, dict)
            
            # Should contain access token
            assert "access_token" in data
            assert isinstance(data["access_token"], str)
            assert len(data["access_token"]) > 0
            
            # Should contain refresh token
            assert "refresh_token" in data
            assert isinstance(data["refresh_token"], str)
            assert len(data["refresh_token"]) > 0
            
            # Should contain token type
            assert "token_type" in data
            assert data["token_type"] == "bearer"
            
            # Should contain expiration info
            assert "expires_in" in data
            assert isinstance(data["expires_in"], int)
            assert data["expires_in"] > 0
            
            # Should contain user info
            assert "user" in data
            user = data["user"]
            assert isinstance(user, dict)
            assert "id" in user
            assert "email" in user
            assert user["email"] == valid_login_data["email"]
            assert "created_at" in user
            assert "updated_at" in user
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials_returns_401(
        self, 
        base_url: str, 
        invalid_login_data: Dict[str, str]
    ):
        """Test invalid credentials returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/login",
                json=invalid_login_data,
                headers={"Content-Type": "application/json"}
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
    async def test_login_malformed_data_returns_422(
        self, 
        base_url: str, 
        malformed_login_data: Dict[str, Any]
    ):
        """Test malformed request data returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/login",
                json=malformed_login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], list)
            assert len(data["detail"]) > 0
    
    @pytest.mark.asyncio
    async def test_login_missing_email_returns_422(
        self, 
        base_url: str
    ):
        """Test missing email field returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/login",
                json={"password": "somepassword"},
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_login_missing_password_returns_422(
        self, 
        base_url: str
    ):
        """Test missing password field returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/login",
                json={"email": "test@example.com"},
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_login_empty_request_returns_422(
        self, 
        base_url: str
    ):
        """Test empty request body returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/login",
                json={},
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_login_wrong_content_type_returns_422(
        self, 
        base_url: str, 
        valid_login_data: Dict[str, str]
    ):
        """Test wrong content type returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/login",
                data=valid_login_data,  # Send as form data instead of JSON
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user_returns_401(
        self, 
        base_url: str
    ):
        """Test login with non-existent user returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/login",
                json={
                    "email": "nonexistent@example.com",
                    "password": "somepassword"
                },
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 401 Unauthorized
            assert response.status_code == 401
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_login_response_headers(
        self, 
        base_url: str, 
        valid_login_data: Dict[str, str]
    ):
        """Test login response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/login",
                json=valid_login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should have correct content type
            assert response.headers["content-type"] == "application/json"
            
            # Should not expose sensitive headers
            assert "server" not in response.headers or "uvicorn" in response.headers.get("server", "")
    
    @pytest.mark.asyncio
    async def test_login_rate_limiting_headers(
        self, 
        base_url: str, 
        valid_login_data: Dict[str, str]
    ):
        """Test login response includes rate limiting headers"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/login",
                json=valid_login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should include rate limiting headers (if implemented)
            # These are optional but good practice
            if "X-RateLimit-Limit" in response.headers:
                assert response.headers["X-RateLimit-Limit"].isdigit()
            if "X-RateLimit-Remaining" in response.headers:
                assert response.headers["X-RateLimit-Remaining"].isdigit()
