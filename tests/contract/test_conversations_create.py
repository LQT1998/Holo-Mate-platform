"""
Contract test for POST /conversations endpoint
Tests the conversation creation API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestConversationsCreateContract:
    """Contract tests for POST /conversations endpoint"""
    
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
    def valid_conversation_data(self) -> Dict[str, Any]:
        """Valid conversation creation request data"""
        return {
            "title": "My First Conversation",
            "companion_id": "companion_123",
            "initial_message": "Hello, how are you today?",
            "settings": {
                "voice_enabled": True,
                "emotion_detection": True,
                "response_length": "medium",
                "formality_level": "casual"
            }
        }
    
    @pytest.fixture
    def minimal_conversation_data(self) -> Dict[str, Any]:
        """Minimal conversation creation request data"""
        return {
            "companion_id": "companion_123"
        }
    
    @pytest.fixture
    def invalid_conversation_data(self) -> Dict[str, Any]:
        """Invalid conversation creation request data"""
        return {
            "title": "",  # Empty title
            "companion_id": "",  # Empty companion ID
            "initial_message": "x" * 5001,  # Message too long
            "settings": "invalid_json"  # Should be object
        }
    
    @pytest.mark.asyncio
    async def test_create_conversation_success_returns_201_and_conversation_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_data: Dict[str, Any]
    ):
        """Test successful conversation creation returns 201 with conversation data"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json=valid_conversation_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 201 Created
            assert response.status_code == 201
            
            # Should return JSON response
            data = response.json()
            assert isinstance(data, dict)
            
            # Should contain conversation ID
            assert "id" in data
            assert isinstance(data["id"], (str, int))
            
            # Should contain provided data
            assert data["title"] == valid_conversation_data["title"]
            assert data["companion_id"] == valid_conversation_data["companion_id"]
            
            # Should contain settings data
            assert "settings" in data
            assert isinstance(data["settings"], dict)
            assert data["settings"]["voice_enabled"] == valid_conversation_data["settings"]["voice_enabled"]
            assert data["settings"]["emotion_detection"] == valid_conversation_data["settings"]["emotion_detection"]
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            assert "last_message_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)
            assert isinstance(data["last_message_at"], str)
            
            # Should contain status
            assert "status" in data
            assert data["status"] in ["active", "paused", "ended", "archived"]
            
            # Should contain initial message if provided
            if "initial_message" in valid_conversation_data:
                assert "initial_message" in data
                assert data["initial_message"] == valid_conversation_data["initial_message"]
    
    @pytest.mark.asyncio
    async def test_create_conversation_minimal_data_success_returns_201(
        self, 
        base_url: str, 
        valid_access_token: str,
        minimal_conversation_data: Dict[str, Any]
    ):
        """Test conversation creation with minimal data returns 201"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json=minimal_conversation_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 201 Created
            assert response.status_code == 201
            
            # Should return JSON response
            data = response.json()
            assert isinstance(data, dict)
            
            # Should contain provided data
            assert data["companion_id"] == minimal_conversation_data["companion_id"]
            
            # Should have default values for optional fields
            assert "title" in data
            assert "settings" in data
            assert "status" in data
    
    @pytest.mark.asyncio
    async def test_create_conversation_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_conversation_data: Dict[str, Any]
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json=valid_conversation_data,
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
    async def test_create_conversation_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_conversation_data: Dict[str, Any]
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json=valid_conversation_data,
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
    async def test_create_conversation_invalid_data_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_conversation_data: Dict[str, Any]
    ):
        """Test invalid conversation data returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json=invalid_conversation_data,
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
    async def test_create_conversation_missing_required_fields_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test missing required fields returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json={},  # Empty request
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
    async def test_create_conversation_nonexistent_companion_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test creating conversation with non-existent companion returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json={
                    "companion_id": "nonexistent_companion_456",
                    "title": "Test Conversation"
                },
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
    async def test_create_conversation_unauthorized_companion_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test creating conversation with companion owned by another user returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json={
                    "companion_id": "other_user_companion_789",
                    "title": "Test Conversation"
                },
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
    async def test_create_conversation_wrong_content_type_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_data: Dict[str, Any]
    ):
        """Test wrong content type returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                data=valid_conversation_data,  # Send as form data instead of JSON
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_conversation_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_data: Dict[str, Any]
    ):
        """Test conversation creation response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json=valid_conversation_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 201:
                # Should have correct content type
                assert response.headers["content-type"] == "application/json"
                
                # Should include Location header with new resource URL
                assert "Location" in response.headers
                location = response.headers["Location"]
                assert f"/conversations/" in location
                
                # Should not expose sensitive headers
                assert "server" not in response.headers or "uvicorn" in response.headers.get("server", "")
    
    @pytest.mark.asyncio
    async def test_create_conversation_validation_rules(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversation creation validation rules"""
        test_cases = [
            # Empty title
            {"title": "", "companion_id": "companion_123"},
            # Title too long
            {"title": "x" * 256, "companion_id": "companion_123"},
            # Invalid companion ID format
            {"title": "Valid Title", "companion_id": ""},
            # Invalid settings values
            {"title": "Valid Title", "companion_id": "companion_123", "settings": {"voice_enabled": "invalid"}},
            # Message too long
            {"title": "Valid Title", "companion_id": "companion_123", "initial_message": "x" * 5001},
        ]
        
        for test_data in test_cases:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/conversations",
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
    async def test_create_conversation_settings_validation(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversation settings validation"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json={
                    "title": "Test Conversation",
                    "companion_id": "companion_123",
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
    async def test_create_conversation_subscription_limits(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_data: Dict[str, Any]
    ):
        """Test conversation creation respects subscription limits"""
        # This test assumes the user has reached their conversation limit
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json=valid_conversation_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 403 Forbidden if limit exceeded
            if response.status_code == 403:
                data = response.json()
                assert isinstance(data, dict)
                assert "detail" in data
                assert "limit" in data["detail"].lower() or "quota" in data["detail"].lower()
            else:
                # Or 201 if within limits
                assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_create_conversation_auto_title_generation(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversation creation with auto-generated title"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json={
                    "companion_id": "companion_123",
                    "initial_message": "Hello, how are you today?"
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                
                # Should have auto-generated title
                assert "title" in data
                assert isinstance(data["title"], str)
                assert len(data["title"]) > 0
                
                # Title should be based on initial message or companion
                assert data["title"] != ""
    
    @pytest.mark.asyncio
    async def test_create_conversation_initial_message_processing(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversation creation processes initial message"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json={
                    "title": "Test Conversation",
                    "companion_id": "companion_123",
                    "initial_message": "Hello, this is my first message!"
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                
                # Should contain initial message
                assert "initial_message" in data
                assert data["initial_message"] == "Hello, this is my first message!"
                
                # Should have last_message_at timestamp
                assert "last_message_at" in data
                assert isinstance(data["last_message_at"], str)
    
    @pytest.mark.asyncio
    async def test_create_conversation_default_settings(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversation creation with default settings"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations",
                json={
                    "title": "Test Conversation",
                    "companion_id": "companion_123"
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                
                # Should have default settings
                assert "settings" in data
                assert isinstance(data["settings"], dict)
                
                # Should have default values
                assert "voice_enabled" in data["settings"]
                assert "emotion_detection" in data["settings"]
                assert "response_length" in data["settings"]
                assert "formality_level" in data["settings"]
