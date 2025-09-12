"""
Contract test for GET /users/me endpoint
Tests the user profile retrieval API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestUsersMeContract:
    """Contract tests for GET /users/me endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for auth service"""
        return "http://localhost:8001"
    
    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        return "valid_access_token_here"
    
    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return "invalid_access_token_here"
    
    @pytest.fixture
    def expired_access_token(self) -> str:
        """Expired access token for testing token expiration"""
        return "expired_access_token_here"
    
    @pytest.mark.asyncio
    async def test_get_user_me_success_returns_200_and_user_data(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test successful user profile retrieval returns 200 with user data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 200 OK
            assert response.status_code == 200
            
            # Should return JSON response
            data = response.json()
            assert isinstance(data, dict)
            
            # Should contain user ID
            assert "id" in data
            assert isinstance(data["id"], (str, int))
            
            # Should contain email
            assert "email" in data
            assert isinstance(data["email"], str)
            assert "@" in data["email"]  # Basic email validation
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)
            
            # Should contain user profile fields
            assert "first_name" in data
            assert "last_name" in data
            assert isinstance(data["first_name"], (str, type(None)))
            assert isinstance(data["last_name"], (str, type(None)))
            
            # Should contain subscription info
            assert "subscription" in data
            subscription = data["subscription"]
            assert isinstance(subscription, dict)
            assert "plan" in subscription
            assert "status" in subscription
            assert "expires_at" in subscription
    
    @pytest.mark.asyncio
    async def test_get_user_me_missing_auth_returns_401(
        self, 
        base_url: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/users/me",
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
    async def test_get_user_me_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/users/me",
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
        base_url: str, 
        expired_access_token: str
    ):
        """Test expired access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/users/me",
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
    
    @pytest.mark.asyncio
    async def test_get_user_me_malformed_auth_header_returns_401(
        self, 
        base_url: str
    ):
        """Test malformed authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/users/me",
                headers={
                    "Authorization": "InvalidFormat token_here",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 401 Unauthorized
            assert response.status_code == 401
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_get_user_me_wrong_auth_scheme_returns_401(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test wrong authorization scheme returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/users/me",
                headers={
                    "Authorization": f"Basic {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 401 Unauthorized
            assert response.status_code == 401
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_get_user_me_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test user profile response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                # Should have correct content type
                assert response.headers["content-type"] == "application/json"
                
                # Should not expose sensitive headers
                assert "server" not in response.headers or "uvicorn" in response.headers.get("server", "")
    
    @pytest.mark.asyncio
    async def test_get_user_me_user_data_structure(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test user data structure is complete and properly formatted"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Required fields should be present
                required_fields = [
                    "id", "email", "created_at", "updated_at", 
                    "first_name", "last_name", "subscription"
                ]
                for field in required_fields:
                    assert field in data, f"Missing required field: {field}"
                
                # Subscription should have required fields
                subscription_fields = ["plan", "status", "expires_at"]
                for field in subscription_fields:
                    assert field in data["subscription"], f"Missing subscription field: {field}"
                
                # Email should be valid format
                email = data["email"]
                assert "@" in email
                assert "." in email.split("@")[1]  # Basic domain validation
                
                # Timestamps should be ISO format
                import re
                iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
                assert re.match(iso_pattern, data["created_at"])
                assert re.match(iso_pattern, data["updated_at"])
    
    @pytest.mark.asyncio
    async def test_get_user_me_privacy_fields(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test that sensitive fields are not exposed in user profile"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Sensitive fields should not be present
                sensitive_fields = ["password", "password_hash", "salt", "secret"]
                for field in sensitive_fields:
                    assert field not in data, f"Sensitive field exposed: {field}"
                
                # Should not expose internal IDs or tokens
                internal_fields = ["refresh_token", "api_key", "internal_id"]
                for field in internal_fields:
                    assert field not in data, f"Internal field exposed: {field}"
    
    @pytest.mark.asyncio
    async def test_get_user_me_caching_headers(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test that user profile response includes appropriate caching headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                # Should include cache control headers
                if "Cache-Control" in response.headers:
                    cache_control = response.headers["Cache-Control"]
                    # Should not cache user profile data
                    assert "no-cache" in cache_control or "no-store" in cache_control
                
                # Should include ETag for conditional requests
                if "ETag" in response.headers:
                    etag = response.headers["ETag"]
                    assert isinstance(etag, str)
                    assert len(etag) > 0
