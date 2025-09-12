"""
Contract test for PUT /users/me endpoint
Tests the user profile update API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestUsersUpdateContract:
    """Contract tests for PUT /users/me endpoint"""
    
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
    def valid_update_data(self) -> Dict[str, Any]:
        """Valid user update request data"""
        return {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "preferences": {
                "language": "en",
                "timezone": "UTC",
                "notifications": True
            }
        }
    
    @pytest.fixture
    def partial_update_data(self) -> Dict[str, Any]:
        """Partial user update request data"""
        return {
            "first_name": "Jane"
        }
    
    @pytest.fixture
    def invalid_update_data(self) -> Dict[str, Any]:
        """Invalid user update request data"""
        return {
            "email": "invalid-email-format",
            "first_name": "",  # Empty string
            "preferences": "invalid_json"  # Should be object
        }
    
    @pytest.mark.asyncio
    async def test_update_user_success_returns_200_and_updated_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test successful user update returns 200 with updated user data"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                json=valid_update_data,
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
            
            # Should contain updated user data
            assert "id" in data
            assert "email" in data
            assert data["email"] == valid_update_data["email"]
            assert data["first_name"] == valid_update_data["first_name"]
            assert data["last_name"] == valid_update_data["last_name"]
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)
            
            # Should contain preferences
            assert "preferences" in data
            assert isinstance(data["preferences"], dict)
            assert data["preferences"]["language"] == valid_update_data["preferences"]["language"]
            assert data["preferences"]["timezone"] == valid_update_data["preferences"]["timezone"]
            assert data["preferences"]["notifications"] == valid_update_data["preferences"]["notifications"]
    
    @pytest.mark.asyncio
    async def test_update_user_partial_success_returns_200(
        self, 
        base_url: str, 
        valid_access_token: str,
        partial_update_data: Dict[str, Any]
    ):
        """Test partial user update returns 200 with updated data"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                json=partial_update_data,
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
            
            # Should contain updated field
            assert data["first_name"] == partial_update_data["first_name"]
    
    @pytest.mark.asyncio
    async def test_update_user_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                json=valid_update_data,
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
    async def test_update_user_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                json=valid_update_data,
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
    async def test_update_user_invalid_data_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_update_data: Dict[str, Any]
    ):
        """Test invalid update data returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                json=invalid_update_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
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
    async def test_update_user_empty_request_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test empty request body returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                json={},
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_update_user_wrong_content_type_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test wrong content type returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                data=valid_update_data,  # Send as form data instead of JSON
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_user_email_already_exists_returns_409(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test updating to existing email returns 409 Conflict"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                json={"email": "existing@example.com"},
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 409 Conflict
            assert response.status_code == 409
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0
    
    @pytest.mark.asyncio
    async def test_update_user_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test user update response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                json=valid_update_data,
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
    async def test_update_user_immutable_fields(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test that immutable fields cannot be updated"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                json={
                    "id": "new_id",  # Should not be updatable
                    "created_at": "2023-01-01T00:00:00Z",  # Should not be updatable
                    "first_name": "John"  # This should be updatable
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                # Immutable fields should not be changed
                assert data["id"] != "new_id"
                assert data["created_at"] != "2023-01-01T00:00:00Z"
                # Updatable field should be changed
                assert data["first_name"] == "John"
    
    @pytest.mark.asyncio
    async def test_update_user_password_change_not_allowed(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test that password cannot be changed via this endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/users/me",
                json={
                    "password": "newpassword123",
                    "first_name": "John"
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 422 Validation Error (password not allowed)
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_update_user_updated_at_timestamp(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test that updated_at timestamp is updated after successful update"""
        async with httpx.AsyncClient() as client:
            # First, get current user data
            get_response = await client.get(
                f"{base_url}/users/me",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if get_response.status_code == 200:
                original_data = get_response.json()
                original_updated_at = original_data["updated_at"]
                
                # Update user
                update_response = await client.put(
                    f"{base_url}/users/me",
                    json=valid_update_data,
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if update_response.status_code == 200:
                    updated_data = update_response.json()
                    new_updated_at = updated_data["updated_at"]
                    
                    # Updated timestamp should be different
                    assert new_updated_at != original_updated_at
                    
                    # Should be more recent
                    from datetime import datetime
                    original_time = datetime.fromisoformat(original_updated_at.replace('Z', '+00:00'))
                    new_time = datetime.fromisoformat(new_updated_at.replace('Z', '+00:00'))
                    assert new_time > original_time
