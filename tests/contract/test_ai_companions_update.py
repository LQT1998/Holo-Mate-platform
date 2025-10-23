"""
Contract test for PUT /ai-companions/{id} endpoint
Tests the AI companion update API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any
import uuid
from datetime import datetime, timedelta, timezone

# Import JWT helpers for token generation
from backend.shared.src.security.security import create_access_token


class TestPutAICompanionsUpdate:
    """Contract tests for PUT /ai-companions/{id} endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for AI service"""
        return "http://localhost:8002/api/v1"
    
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
        from backend.ai_service.src.config import settings
        secret = settings.JWT_SECRET or "dev-secret"
        return jwt.encode(token_data, secret, algorithm="HS256")
    
    @pytest.fixture
    def valid_companion_id(self) -> str:
        """Valid companion ID for testing"""
        return "companion_123"
    
    @pytest.fixture
    def nonexistent_companion_id(self) -> str:
        """Non-existent companion ID for testing 404"""
        return "nonexistent_companion_456"
    
    @pytest.fixture
    def forbidden_companion_id(self) -> str:
        """Companion ID owned by another user for testing 403"""
        return "forbidden_999"
    
    @pytest.fixture
    def valid_update_data(self) -> Dict[str, Any]:
        """Valid companion update data"""
        return {
            "name": "Updated Companion",
            "description": "An updated AI Companion for testing",
            "personality": {
                "traits": ["friendly", "helpful", "professional"],
                "communication_style": "formal",
                "humor_level": 0.5,
                "empathy_level": 0.8,
            },
            "preferences": {
                "conversation_topics": ["technology", "business", "science"],
                "response_length": "long",
                "formality_level": "formal",
            },
            "status": "active"
        }
    
    @pytest.fixture
    def invalid_update_data(self) -> Dict[str, Any]:
        """Invalid companion update data for validation testing"""
        return {
            "name": "",  # Empty name should fail validation
            "description": "A" * 1001,  # Too long description
            "personality": {
                "traits": [],  # Empty traits should fail
                "communication_style": "invalid_style",  # Invalid enum value
                "humor_level": 1.5,  # Out of range (0-1)
                "empathy_level": -0.1,  # Out of range (0-1)
            },
            "preferences": {
                "conversation_topics": [],  # Empty topics should fail
                "response_length": "invalid_length",  # Invalid enum value
                "formality_level": "invalid_level",  # Invalid enum value
            },
            "status": "invalid_status"  # Invalid enum value
        }
    
    @pytest.fixture
    def restricted_field_data(self) -> Dict[str, Any]:
        """Data attempting to update restricted fields (should be rejected)"""
        return {
            "name": "Updated Companion",
            "description": "Updated description",
            "id": "new-id-123",  # Should be rejected
            "user_id": "new-user-id",  # Should be rejected
            "created_at": "2023-01-01T00:00:00Z",  # Should be rejected
            "updated_at": "2023-01-01T00:00:00Z",  # Should be rejected
        }

    @pytest.mark.asyncio
    async def test_put_companion_success_returns_200_and_updated_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test successful companion update returns 200 with updated data"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
            # In DEV, id is normalized to a stable UUID derived from input
            expected_id = uuid.uuid5(uuid.NAMESPACE_URL, f"dev:ai-companion:{valid_companion_id}")
            assert data["id"] == str(expected_id)
            
            assert "user_id" in data
            assert data["user_id"] == "00000000-0000-0000-0000-000000000000"  # User ID should not change
            
            assert "name" in data
            assert data["name"] == valid_update_data["name"]
            
            assert "description" in data
            assert data["description"] == valid_update_data["description"]
            
            assert "personality" in data
            assert data["personality"] == valid_update_data["personality"]
            
            assert "preferences" in data
            assert data["preferences"] == valid_update_data["preferences"]
            
            assert "status" in data
            assert data["status"] == valid_update_data["status"]
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            
            # Should not contain sensitive fields
            sensitive_fields = ["password", "password_hash", "hashed_password", "salt"]
            for field in sensitive_fields:
                assert field not in data, f"Sensitive field exposed: {field}"

    @pytest.mark.asyncio
    async def test_put_companion_invalid_data_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str,
        invalid_update_data: Dict[str, Any]
    ):
        """Test invalid data returns 422 validation error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_put_companion_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_put_companion_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_put_companion_expired_token_returns_401(
        self, 
        base_url: str, 
        expired_access_token: str,
        valid_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test expired access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_put_companion_unauthorized_access_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str,
        forbidden_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test accessing companion owned by another user returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{forbidden_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                },
                json=valid_update_data
            )
            
            # Should return 403 Forbidden
            assert response.status_code == 403
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0

    @pytest.mark.asyncio
    async def test_put_companion_nonexistent_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test non-existent companion returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{nonexistent_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                },
                json=valid_update_data
            )
            
            # Should return 404 Not Found
            assert response.status_code == 404
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0

    @pytest.mark.asyncio
    async def test_put_companion_restricted_fields_rejected(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str,
        restricted_field_data: Dict[str, Any]
    ):
        """Test that restricted fields (id, user_id, created_at) are rejected"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_put_companion_partial_update_allowed(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test that partial updates are allowed (only some fields provided)"""
        partial_update_data = {
            "name": "Partially Updated Companion",
            "status": "inactive"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                },
                json=partial_update_data
            )
            
            # Should return 200 OK
            assert response.status_code == 200
            
            # Should return JSON response
            data = response.json()
            assert isinstance(data, dict)
            
            # Should contain updated fields
            assert "name" in data
            assert data["name"] == partial_update_data["name"]
            
            assert "status" in data
            assert data["status"] == partial_update_data["status"]
            
            # Other fields should still be present (not necessarily updated)
            assert "id" in data
            assert "user_id" in data
            assert "description" in data
            assert "created_at" in data
            assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_put_companion_empty_payload_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test empty payload returns 422 validation error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                },
                json={}
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], (str, list, dict))