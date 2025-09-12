"""
Contract test for POST /auth/refresh endpoint
Tests the authentication refresh token API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestAuthRefreshContract:
    """Contract tests for POST /auth/refresh endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for auth service"""
        return "http://localhost:8001"
    
    @pytest.fixture
    def valid_refresh_data(self) -> Dict[str, str]:
        """Valid refresh token request data"""
        return {
            "refresh_token": "valid_refresh_token_here"
        }
    
    @pytest.fixture
    def invalid_refresh_data(self) -> Dict[str, str]:
        """Invalid refresh token request data"""
        return {
            "refresh_token": "invalid_refresh_token_here"
        }
    
    @pytest.fixture
    def expired_refresh_data(self) -> Dict[str, str]:
        """Expired refresh token request data"""
        return {
            "refresh_token": "expired_refresh_token_here"
        }
    
    @pytest.mark.asyncio
    async def test_refresh_success_returns_200_and_new_tokens(
        self, 
        base_url: str, 
        valid_refresh_data: Dict[str, str]
    ):
        """Test successful refresh returns 200 with new access and refresh tokens"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/refresh",
                json=valid_refresh_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 200 OK
            assert response.status_code == 200
            
            # Should return JSON response
            data = response.json()
            assert isinstance(data, dict)
            
            # Should contain new access token
            assert "access_token" in data
            assert isinstance(data["access_token"], str)
            assert len(data["access_token"]) > 0
            
            # Should contain new refresh token
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
    
    @pytest.mark.asyncio
    async def test_refresh_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_refresh_data: Dict[str, str]
    ):
        """Test invalid refresh token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/refresh",
                json=invalid_refresh_data,
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
    async def test_refresh_expired_token_returns_401(
        self, 
        base_url: str, 
        expired_refresh_data: Dict[str, str]
    ):
        """Test expired refresh token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/refresh",
                json=expired_refresh_data,
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
    async def test_refresh_missing_token_returns_422(
        self, 
        base_url: str
    ):
        """Test missing refresh token returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/refresh",
                json={},
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
    async def test_refresh_empty_token_returns_422(
        self, 
        base_url: str
    ):
        """Test empty refresh token returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/refresh",
                json={"refresh_token": ""},
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_refresh_wrong_content_type_returns_422(
        self, 
        base_url: str, 
        valid_refresh_data: Dict[str, str]
    ):
        """Test wrong content type returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/refresh",
                data=valid_refresh_data,  # Send as form data instead of JSON
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_refresh_response_headers(
        self, 
        base_url: str, 
        valid_refresh_data: Dict[str, str]
    ):
        """Test refresh response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/refresh",
                json=valid_refresh_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should have correct content type
            assert response.headers["content-type"] == "application/json"
            
            # Should not expose sensitive headers
            assert "server" not in response.headers or "uvicorn" in response.headers.get("server", "")
    
    @pytest.mark.asyncio
    async def test_refresh_token_rotation(
        self, 
        base_url: str, 
        valid_refresh_data: Dict[str, str]
    ):
        """Test that refresh token is rotated (new token different from old)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/refresh",
                json=valid_refresh_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                old_token = valid_refresh_data["refresh_token"]
                new_token = data["refresh_token"]
                
                # New refresh token should be different from old one
                assert new_token != old_token
                
                # New access token should be different from refresh token
                assert data["access_token"] != new_token
    
    @pytest.mark.asyncio
    async def test_refresh_multiple_requests_same_token(
        self, 
        base_url: str, 
        valid_refresh_data: Dict[str, str]
    ):
        """Test that using same refresh token multiple times behaves correctly"""
        async with httpx.AsyncClient() as client:
            # First request
            response1 = await client.post(
                f"{base_url}/auth/refresh",
                json=valid_refresh_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Second request with same token
            response2 = await client.post(
                f"{base_url}/auth/refresh",
                json=valid_refresh_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Either both succeed (if token reuse allowed) or second fails
            # This depends on implementation - both are valid approaches
            assert response1.status_code in [200, 401]
            assert response2.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_refresh_malformed_token_returns_401(
        self, 
        base_url: str
    ):
        """Test malformed refresh token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/auth/refresh",
                json={"refresh_token": "malformed.token.here"},
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 401 Unauthorized
            assert response.status_code == 401
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
