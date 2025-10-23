"""
Contract test for PUT /conversations/{id} endpoint
Tests the conversation update API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestConversationsUpdateContract:
    """Contract tests for PUT /conversations/{id} endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for AI service"""
        return "http://localhost:8002/api/v1"
    
    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        return "valid_access_token_here"
    
    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return "invalid_access_token_here"
    
    @pytest.fixture
    def valid_conversation_id(self) -> str:
        """Valid conversation ID for testing"""
        return "conversation_123"
    
    @pytest.fixture
    def invalid_conversation_id(self) -> str:
        """Invalid conversation ID for testing"""
        return "invalid_conversation_id"
    
    @pytest.fixture
    def nonexistent_conversation_id(self) -> str:
        """Non-existent conversation ID for testing"""
        return "nonexistent_conversation_456"
    
    @pytest.fixture
    def forbidden_conversation_id(self) -> str:
        """Conversation ID owned by another user for testing 403"""
        return "forbidden_999"
    
    @pytest.fixture
    def valid_update_data(self) -> Dict[str, Any]:
        """Valid conversation update request data"""
        return {
            "title": "Updated Conversation Title",
            "status": "paused",
            "settings": {
                "voice_enabled": False,
                "emotion_detection": True,
                "response_length": "long",
                "formality_level": "formal"
            }
        }
    
    @pytest.fixture
    def partial_update_data(self) -> Dict[str, Any]:
        """Partial conversation update request data"""
        return {
            "title": "New Title Only"
        }
    
    @pytest.fixture
    def invalid_update_data(self) -> Dict[str, Any]:
        """Invalid conversation update request data"""
        return {
            "title": "",  # Empty title
            "status": "invalid_status",  # Invalid status
            "settings": "invalid_json"  # Should be object
        }
    
    @pytest.mark.asyncio
    async def test_update_conversation_success_returns_200_and_updated_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test successful conversation update returns 200 with updated conversation data"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
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
            
            # Should contain conversation ID (UUID string)
            assert "id" in data
            assert isinstance(data["id"], str)
            # ID should be a valid UUID string (normalized from conversation_123)
            
            # Should contain updated data
            assert data["title"] == valid_update_data["title"]
            assert data["status"] == valid_update_data["status"]
            
            # Should contain updated settings data
            assert "settings" in data
            assert isinstance(data["settings"], dict)
            assert data["settings"]["voice_enabled"] == valid_update_data["settings"]["voice_enabled"]
            assert data["settings"]["emotion_detection"] == valid_update_data["settings"]["emotion_detection"]
            assert data["settings"]["response_length"] == valid_update_data["settings"]["response_length"]
            assert data["settings"]["formality_level"] == valid_update_data["settings"]["formality_level"]
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            assert "last_message_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)
            assert isinstance(data["last_message_at"], str)
    
    @pytest.mark.asyncio
    async def test_update_conversation_partial_success_returns_200(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str,
        partial_update_data: Dict[str, Any]
    ):
        """Test partial conversation update returns 200 with updated data"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
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
            assert data["title"] == partial_update_data["title"]
            
            # Other fields should remain unchanged
            assert "status" in data
            assert "settings" in data
            assert "companion_id" in data
    
    @pytest.mark.asyncio
    async def test_update_conversation_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_conversation_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
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
    async def test_update_conversation_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_conversation_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
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
    async def test_update_conversation_nonexistent_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_conversation_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test updating non-existent conversation returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{nonexistent_conversation_id}",
                json=valid_update_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
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
    async def test_update_conversation_unauthorized_access_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str,
        forbidden_conversation_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test updating conversation owned by another user returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{forbidden_conversation_id}",
                json=valid_update_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
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
    async def test_update_conversation_invalid_data_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str,
        invalid_update_data: Dict[str, Any]
    ):
        """Test invalid update data returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
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
    async def test_update_conversation_empty_request_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test empty request body returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
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
    async def test_update_conversation_wrong_content_type_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test wrong content type returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
                data=valid_update_data,  # Send as form data instead of JSON
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_conversation_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test conversation update response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
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
    async def test_update_conversation_immutable_fields(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test that immutable fields cannot be updated"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
                json={
                    "id": "new_id",  # Should not be updatable
                    "created_at": "2023-01-01T00:00:00Z",  # Should not be updatable
                    "companion_id": "new_companion",  # Should not be updatable
                    "title": "UpdatedTitle"  # This should be updatable
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
                assert data["companion_id"] != "new_companion"
                # Updatable field should be changed
                assert data["title"] == "UpdatedTitle"
    
    @pytest.mark.asyncio
    async def test_update_conversation_updated_at_timestamp(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test that updated_at timestamp is updated after successful update"""
        async with httpx.AsyncClient() as client:
            # First, get current conversation data
            get_response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if get_response.status_code == 200:
                original_data = get_response.json()
                original_updated_at = original_data["updated_at"]
                
                # Update conversation
                update_response = await client.put(
                    f"{base_url}/conversations/{valid_conversation_id}",
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
    
    @pytest.mark.asyncio
    async def test_update_conversation_validation_rules(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test conversation update validation rules"""
        test_cases = [
            # Empty title
            {"title": ""},
            # Title too long
            {"title": "x" * 256},
            # Invalid status
            {"status": "invalid_status"},
            # Invalid settings values
            {"settings": {"voice_enabled": "invalid_boolean"}},
        ]
        
        for test_data in test_cases:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{base_url}/conversations/{valid_conversation_id}",
                    json=test_data,
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                # Should return 422 Validation Error
                assert response.status_code == 422
                
                # Should return validation error details
                data = response.json()
                assert isinstance(data, dict)
                assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_update_conversation_status_transitions(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test conversation status transitions"""
        valid_statuses = ["active", "paused", "ended", "archived"]
        
        for status in valid_statuses:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{base_url}/conversations/{valid_conversation_id}",
                    json={"status": status},
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                # Should return 200 OK for valid status
                assert response.status_code == 200
                
                data = response.json()
                assert data["status"] == status
    
    @pytest.mark.asyncio
    async def test_update_conversation_settings_validation(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test conversation settings validation"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
                json={
                    "settings": {
                        "voice_enabled": "invalid_boolean",  # Invalid boolean
                        "emotion_detection": 123,  # Invalid boolean
                        "response_length": "invalid_length",  # Invalid enum
                        "formality_level": "invalid_level"  # Invalid enum
                    }
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 422 Validation Error
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_update_conversation_archived_conversation(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test updating archived conversation"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/conversations/{valid_conversation_id}",
                json={
                    "title": "Updated Title",
                    "status": "archived"
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                assert data["status"] == "archived"
                assert data["title"] == "Updated Title"
            else:
                # Or 403 if archived conversations cannot be updated
                assert response.status_code == 403
