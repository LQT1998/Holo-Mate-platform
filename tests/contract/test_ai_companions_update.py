"""
Contract test for PUT /ai-companions/{id} endpoint
Tests the AI companion update API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestAICompanionsUpdateContract:
    """Contract tests for PUT /ai-companions/{id} endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for AI service"""
        return "http://localhost:8002"
    
    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        return "valid_access_token_here"
    
    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return "invalid_access_token_here"
    
    @pytest.fixture
    def valid_companion_id(self) -> str:
        """Valid companion ID for testing"""
        return "companion_123"
    
    @pytest.fixture
    def invalid_companion_id(self) -> str:
        """Invalid companion ID for testing"""
        return "invalid_companion_id"
    
    @pytest.fixture
    def nonexistent_companion_id(self) -> str:
        """Non-existent companion ID for testing"""
        return "nonexistent_companion_456"
    
    @pytest.fixture
    def valid_update_data(self) -> Dict[str, Any]:
        """Valid AI companion update request data"""
        return {
            "name": "Alice Updated",
            "description": "An updated friendly AI assistant with enhanced personality",
            "personality": {
                "traits": ["friendly", "helpful", "curious", "witty"],
                "communication_style": "casual",
                "humor_level": 0.8,
                "empathy_level": 0.9
            },
            "voice_profile": {
                "voice_id": "voice_456",
                "speed": 1.1,
                "pitch": 0.6,
                "volume": 0.9
            },
            "character_asset": {
                "model_id": "character_789",
                "animations": ["idle", "talking", "listening", "laughing"],
                "emotions": ["happy", "sad", "excited", "calm", "surprised"]
            },
            "preferences": {
                "conversation_topics": ["technology", "science", "art", "music"],
                "response_length": "long",
                "formality_level": "casual"
            }
        }
    
    @pytest.fixture
    def partial_update_data(self) -> Dict[str, Any]:
        """Partial AI companion update request data"""
        return {
            "name": "Alice Renamed",
            "description": "Updated description only"
        }
    
    @pytest.fixture
    def invalid_update_data(self) -> Dict[str, Any]:
        """Invalid AI companion update request data"""
        return {
            "name": "",  # Empty name
            "description": "A companion with invalid data",
            "personality": "invalid_json",  # Should be object
            "voice_profile": {
                "voice_id": "",  # Empty voice ID
                "speed": 5.0,  # Invalid speed
                "pitch": -1.0  # Invalid pitch
            }
        }
    
    @pytest.mark.asyncio
    async def test_update_companion_success_returns_200_and_updated_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test successful AI companion update returns 200 with updated companion data"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
            
            # Should contain companion ID
            assert "id" in data
            assert data["id"] == valid_companion_id
            
            # Should contain updated data
            assert data["name"] == valid_update_data["name"]
            assert data["description"] == valid_update_data["description"]
            
            # Should contain updated personality data
            assert "personality" in data
            assert isinstance(data["personality"], dict)
            assert data["personality"]["traits"] == valid_update_data["personality"]["traits"]
            assert data["personality"]["communication_style"] == valid_update_data["personality"]["communication_style"]
            assert data["personality"]["humor_level"] == valid_update_data["personality"]["humor_level"]
            assert data["personality"]["empathy_level"] == valid_update_data["personality"]["empathy_level"]
            
            # Should contain updated voice profile data
            assert "voice_profile" in data
            assert isinstance(data["voice_profile"], dict)
            assert data["voice_profile"]["voice_id"] == valid_update_data["voice_profile"]["voice_id"]
            assert data["voice_profile"]["speed"] == valid_update_data["voice_profile"]["speed"]
            assert data["voice_profile"]["pitch"] == valid_update_data["voice_profile"]["pitch"]
            assert data["voice_profile"]["volume"] == valid_update_data["voice_profile"]["volume"]
            
            # Should contain updated character asset data
            assert "character_asset" in data
            assert isinstance(data["character_asset"], dict)
            assert data["character_asset"]["model_id"] == valid_update_data["character_asset"]["model_id"]
            assert data["character_asset"]["animations"] == valid_update_data["character_asset"]["animations"]
            assert data["character_asset"]["emotions"] == valid_update_data["character_asset"]["emotions"]
            
            # Should contain updated preferences data
            assert "preferences" in data
            assert isinstance(data["preferences"], dict)
            assert data["preferences"]["conversation_topics"] == valid_update_data["preferences"]["conversation_topics"]
            assert data["preferences"]["response_length"] == valid_update_data["preferences"]["response_length"]
            assert data["preferences"]["formality_level"] == valid_update_data["preferences"]["formality_level"]
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)
            
            # Should contain status
            assert "status" in data
            assert data["status"] in ["active", "inactive", "training", "error"]
    
    @pytest.mark.asyncio
    async def test_update_companion_partial_success_returns_200(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str,
        partial_update_data: Dict[str, Any]
    ):
        """Test partial AI companion update returns 200 with updated data"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
            
            # Should contain updated fields
            assert data["name"] == partial_update_data["name"]
            assert data["description"] == partial_update_data["description"]
            
            # Other fields should remain unchanged
            assert "personality" in data
            assert "voice_profile" in data
            assert "character_asset" in data
            assert "preferences" in data
    
    @pytest.mark.asyncio
    async def test_update_companion_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_update_companion_invalid_token_returns_401(
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
    async def test_update_companion_nonexistent_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test updating non-existent companion returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{nonexistent_companion_id}",
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
    async def test_update_companion_unauthorized_access_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test updating companion owned by another user returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_update_companion_invalid_data_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str,
        invalid_update_data: Dict[str, Any]
    ):
        """Test invalid update data returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_update_companion_empty_request_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test empty request body returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_update_companion_wrong_content_type_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test wrong content type returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
                data=valid_update_data,  # Send as form data instead of JSON
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_companion_duplicate_name_returns_409(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test updating to duplicate name returns 409 Conflict"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
                json={
                    "name": "ExistingCompanion",
                    "description": "Updated description"
                },
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
    async def test_update_companion_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test companion update response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_update_companion_immutable_fields(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test that immutable fields cannot be updated"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/ai-companions/{valid_companion_id}",
                json={
                    "id": "new_id",  # Should not be updatable
                    "created_at": "2023-01-01T00:00:00Z",  # Should not be updatable
                    "name": "UpdatedName"  # This should be updatable
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
                assert data["name"] == "UpdatedName"
    
    @pytest.mark.asyncio
    async def test_update_companion_updated_at_timestamp(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test that updated_at timestamp is updated after successful update"""
        async with httpx.AsyncClient() as client:
            # First, get current companion data
            get_response = await client.get(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if get_response.status_code == 200:
                original_data = get_response.json()
                original_updated_at = original_data["updated_at"]
                
                # Update companion
                update_response = await client.put(
                    f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_update_companion_validation_rules(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion update validation rules"""
        test_cases = [
            # Empty name
            {"name": "", "description": "Valid description"},
            # Name too long
            {"name": "x" * 256, "description": "Valid description"},
            # Description too long
            {"name": "ValidName", "description": "x" * 2001},
            # Invalid personality values
            {"name": "ValidName", "description": "Valid description", "personality": {"humor_level": 2.0}},
            # Invalid voice profile values
            {"name": "ValidName", "description": "Valid description", "voice_profile": {"speed": -1.0}},
        ]
        
        for test_data in test_cases:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{base_url}/ai-companions/{valid_companion_id}",
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
