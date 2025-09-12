"""
Contract test for POST /streaming/chat endpoint
Tests the streaming chat start API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestStreamingStartContract:
    """Contract tests for POST /streaming/chat endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for streaming service"""
        return "http://localhost:8003"
    
    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        return "valid_access_token_here"
    
    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return "invalid_access_token_here"
    
    @pytest.fixture
    def valid_streaming_data(self) -> Dict[str, Any]:
        """Valid streaming chat start request data"""
        return {
            "conversation_id": "conversation_123",
            "companion_id": "companion_456",
            "device_id": "device_789",
            "streaming_config": {
                "voice_enabled": True,
                "emotion_detection": True,
                "response_format": "audio",
                "sample_rate": 44100,
                "channels": 1,
                "bit_depth": 16
            },
            "audio_settings": {
                "noise_reduction": True,
                "echo_cancellation": True,
                "auto_gain_control": True
            }
        }
    
    @pytest.fixture
    def minimal_streaming_data(self) -> Dict[str, Any]:
        """Minimal streaming chat start request data"""
        return {
            "conversation_id": "conversation_123",
            "companion_id": "companion_456"
        }
    
    @pytest.fixture
    def invalid_streaming_data(self) -> Dict[str, Any]:
        """Invalid streaming chat start request data"""
        return {
            "conversation_id": "",  # Empty conversation ID
            "companion_id": "",  # Empty companion ID
            "device_id": "invalid_device",  # Invalid device
            "streaming_config": "invalid_json"  # Should be object
        }
    
    @pytest.mark.asyncio
    async def test_start_streaming_success_returns_201_and_session_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_streaming_data: Dict[str, Any]
    ):
        """Test successful streaming chat start returns 201 with session data"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json=valid_streaming_data,
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
            
            # Should contain session ID
            assert "session_id" in data
            assert isinstance(data["session_id"], (str, int))
            
            # Should contain streaming info
            assert "websocket_url" in data
            assert isinstance(data["websocket_url"], str)
            assert data["websocket_url"].startswith("ws://") or data["websocket_url"].startswith("wss://")
            
            # Should contain provided data
            assert data["conversation_id"] == valid_streaming_data["conversation_id"]
            assert data["companion_id"] == valid_streaming_data["companion_id"]
            assert data["device_id"] == valid_streaming_data["device_id"]
            
            # Should contain streaming config
            assert "streaming_config" in data
            assert isinstance(data["streaming_config"], dict)
            assert data["streaming_config"]["voice_enabled"] == valid_streaming_data["streaming_config"]["voice_enabled"]
            assert data["streaming_config"]["emotion_detection"] == valid_streaming_data["streaming_config"]["emotion_detection"]
            
            # Should contain audio settings
            assert "audio_settings" in data
            assert isinstance(data["audio_settings"], dict)
            assert data["audio_settings"]["noise_reduction"] == valid_streaming_data["audio_settings"]["noise_reduction"]
            
            # Should contain timestamps
            assert "created_at" in data
            assert "expires_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["expires_at"], str)
            
            # Should contain status
            assert "status" in data
            assert data["status"] in ["active", "connecting", "error", "expired"]
    
    @pytest.mark.asyncio
    async def test_start_streaming_minimal_data_success_returns_201(
        self, 
        base_url: str, 
        valid_access_token: str,
        minimal_streaming_data: Dict[str, Any]
    ):
        """Test streaming chat start with minimal data returns 201"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json=minimal_streaming_data,
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
            assert data["conversation_id"] == minimal_streaming_data["conversation_id"]
            assert data["companion_id"] == minimal_streaming_data["companion_id"]
            
            # Should have default values for optional fields
            assert "session_id" in data
            assert "websocket_url" in data
            assert "streaming_config" in data
            assert "audio_settings" in data
    
    @pytest.mark.asyncio
    async def test_start_streaming_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_streaming_data: Dict[str, Any]
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json=valid_streaming_data,
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
    async def test_start_streaming_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_streaming_data: Dict[str, Any]
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json=valid_streaming_data,
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
    async def test_start_streaming_invalid_data_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_streaming_data: Dict[str, Any]
    ):
        """Test invalid streaming data returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json=invalid_streaming_data,
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
    async def test_start_streaming_missing_required_fields_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test missing required fields returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
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
    async def test_start_streaming_nonexistent_conversation_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test starting streaming with non-existent conversation returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json={
                    "conversation_id": "nonexistent_conversation_456",
                    "companion_id": "companion_123"
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
    async def test_start_streaming_nonexistent_companion_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test starting streaming with non-existent companion returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json={
                    "conversation_id": "conversation_123",
                    "companion_id": "nonexistent_companion_456"
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
    async def test_start_streaming_unauthorized_conversation_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test starting streaming with conversation owned by another user returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json={
                    "conversation_id": "other_user_conversation_789",
                    "companion_id": "companion_123"
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
    async def test_start_streaming_device_not_available_returns_503(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test starting streaming with unavailable device returns 503 Service Unavailable"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json={
                    "conversation_id": "conversation_123",
                    "companion_id": "companion_456",
                    "device_id": "unavailable_device_999"
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 503 Service Unavailable
            assert response.status_code == 503
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0
    
    @pytest.mark.asyncio
    async def test_start_streaming_wrong_content_type_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_streaming_data: Dict[str, Any]
    ):
        """Test wrong content type returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                data=valid_streaming_data,  # Send as form data instead of JSON
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_start_streaming_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_streaming_data: Dict[str, Any]
    ):
        """Test streaming start response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json=valid_streaming_data,
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
                assert f"/streaming/chat/" in location
                
                # Should not expose sensitive headers
                assert "server" not in response.headers or "uvicorn" in response.headers.get("server", "")
    
    @pytest.mark.asyncio
    async def test_start_streaming_validation_rules(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test streaming start validation rules"""
        test_cases = [
            # Empty conversation ID
            {"conversation_id": "", "companion_id": "companion_123"},
            # Empty companion ID
            {"conversation_id": "conversation_123", "companion_id": ""},
            # Invalid streaming config values
            {"conversation_id": "conversation_123", "companion_id": "companion_456", "streaming_config": {"voice_enabled": "invalid"}},
            # Invalid audio settings values
            {"conversation_id": "conversation_123", "companion_id": "companion_456", "audio_settings": {"noise_reduction": "invalid"}},
        ]
        
        for test_data in test_cases:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/streaming/chat",
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
    async def test_start_streaming_subscription_limits(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_streaming_data: Dict[str, Any]
    ):
        """Test streaming start respects subscription limits"""
        # This test assumes the user has reached their streaming limit
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json=valid_streaming_data,
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
    async def test_start_streaming_duplicate_session(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_streaming_data: Dict[str, Any]
    ):
        """Test starting streaming with duplicate session"""
        async with httpx.AsyncClient() as client:
            # First request
            response1 = await client.post(
                f"{base_url}/streaming/chat",
                json=valid_streaming_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Second request with same data
            response2 = await client.post(
                f"{base_url}/streaming/chat",
                json=valid_streaming_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Either both succeed (if multiple sessions allowed) or second fails
            # This depends on implementation - both are valid approaches
            assert response1.status_code in [201, 409]
            assert response2.status_code in [201, 409]
    
    @pytest.mark.asyncio
    async def test_start_streaming_websocket_url_format(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_streaming_data: Dict[str, Any]
    ):
        """Test streaming start returns valid WebSocket URL"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json=valid_streaming_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                
                # WebSocket URL should be valid
                websocket_url = data["websocket_url"]
                assert websocket_url.startswith("ws://") or websocket_url.startswith("wss://")
                assert "streaming/chat/" in websocket_url
                
                # Should contain session ID in URL
                assert str(data["session_id"]) in websocket_url
    
    @pytest.mark.asyncio
    async def test_start_streaming_session_expiration(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_streaming_data: Dict[str, Any]
    ):
        """Test streaming session has proper expiration"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/chat",
                json=valid_streaming_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                
                # Should have expiration time
                assert "expires_at" in data
                assert isinstance(data["expires_at"], str)
                
                # Should be in the future
                from datetime import datetime
                expires_time = datetime.fromisoformat(data["expires_at"].replace('Z', '+00:00'))
                now = datetime.now(expires_time.tzinfo)
                assert expires_time > now
