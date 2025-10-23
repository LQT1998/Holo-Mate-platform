"""
Contract test for GET /streaming/sessions/{id}/chat endpoint
Tests the streaming chat status API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestStreamingStatusContract:
    """Contract tests for GET /streaming/sessions/{id}/chat endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for streaming service"""
        return "http://localhost:8003/api/v1"
    
    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        return "valid_access_token_here"
    
    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return "invalid_access_token_here"
    
    @pytest.fixture
    def valid_session_id(self) -> str:
        """Valid session ID for testing"""
        return "session_123"
    
    @pytest.fixture
    def invalid_session_id(self) -> str:
        """Invalid session ID for testing"""
        return "invalid_session_id"
    
    @pytest.fixture
    def nonexistent_session_id(self) -> str:
        """Non-existent session ID for testing"""
        return "nonexistent_session_456"
    
    @pytest.mark.asyncio
    async def test_get_streaming_status_success_returns_200_and_status_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_session_id: str
    ):
        """Test successful streaming status retrieval returns 200 with status data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{valid_session_id}/chat",
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
            
            # Should contain session ID
            assert "session_id" in data
            assert data["session_id"] == valid_session_id
            
            # Should contain basic session info
            assert "conversation_id" in data
            assert "companion_id" in data
            assert "device_id" in data
            assert isinstance(data["conversation_id"], (str, int))
            assert isinstance(data["companion_id"], (str, int))
            assert isinstance(data["device_id"], (str, int))
            
            # Should contain status
            assert "status" in data
            assert isinstance(data["status"], str)
            assert data["status"] in ["active", "connecting", "error", "expired", "ended"]
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            assert "expires_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)
            assert isinstance(data["expires_at"], str)
            
            # Should contain streaming info
            assert "websocket_url" in data
            assert isinstance(data["websocket_url"], str)
            assert data["websocket_url"].startswith("ws://") or data["websocket_url"].startswith("wss://")
            
            # Should contain streaming config
            assert "streaming_config" in data
            assert isinstance(data["streaming_config"], dict)
            assert "voice_enabled" in data["streaming_config"]
            assert "emotion_detection" in data["streaming_config"]
            assert "response_format" in data["streaming_config"]
            
            # Should contain audio settings
            assert "audio_settings" in data
            assert isinstance(data["audio_settings"], dict)
            assert "noise_reduction" in data["audio_settings"]
            assert "echo_cancellation" in data["audio_settings"]
    
    @pytest.mark.asyncio
    async def test_get_streaming_status_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_session_id: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{valid_session_id}/chat",
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
    async def test_get_streaming_status_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_session_id: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{valid_session_id}/chat",
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
    async def test_get_streaming_status_nonexistent_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_session_id: str
    ):
        """Test non-existent session returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{nonexistent_session_id}/chat",
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
    async def test_get_streaming_status_unauthorized_access_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test accessing session owned by another user returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/forbidden_999/chat",
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
    async def test_get_streaming_status_invalid_id_format_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_session_id: str
    ):
        """Test invalid session ID format returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{invalid_session_id}/chat",
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
    async def test_get_streaming_status_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_session_id: str
    ):
        """Test streaming status response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{valid_session_id}/chat",
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
    async def test_get_streaming_status_data_structure_validation(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_session_id: str
    ):
        """Test streaming status data structure is complete and properly formatted"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{valid_session_id}/chat",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Required fields should be present
                required_fields = [
                    "session_id", "conversation_id", "companion_id", "device_id",
                    "status", "created_at", "updated_at", "expires_at",
                    "websocket_url", "streaming_config", "audio_settings"
                ]
                for field in required_fields:
                    assert field in data, f"Missing required field: {field}"
                
                # Streaming config should have required fields
                config_fields = ["voice_enabled", "emotion_detection", "response_format"]
                for field in config_fields:
                    assert field in data["streaming_config"], f"Missing config field: {field}"
                
                # Audio settings should have required fields
                audio_fields = ["noise_reduction", "echo_cancellation", "auto_gain_control"]
                for field in audio_fields:
                    assert field in data["audio_settings"], f"Missing audio field: {field}"
                
                # Data types should be correct
                assert isinstance(data["session_id"], (str, int))
                assert isinstance(data["conversation_id"], (str, int))
                assert isinstance(data["companion_id"], (str, int))
                assert isinstance(data["device_id"], (str, int))
                assert isinstance(data["status"], str)
                assert isinstance(data["streaming_config"], dict)
                assert isinstance(data["audio_settings"], dict)
                
                # Status should be valid
                valid_statuses = ["active", "connecting", "error", "expired", "ended"]
                assert data["status"] in valid_statuses
    
    @pytest.mark.asyncio
    async def test_get_streaming_status_timestamps_format(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_session_id: str
    ):
        """Test streaming status timestamps are in correct ISO format"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{valid_session_id}/chat",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Timestamps should be ISO format
                import re
                iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
                assert re.match(iso_pattern, data["created_at"])
                assert re.match(iso_pattern, data["updated_at"])
                assert re.match(iso_pattern, data["expires_at"])
                
                # Updated timestamp should be >= created timestamp
                from datetime import datetime
                created_time = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
                updated_time = datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
                assert updated_time >= created_time
    
    @pytest.mark.asyncio
    async def test_get_streaming_status_caching_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_session_id: str
    ):
        """Test that streaming status response includes appropriate caching headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{valid_session_id}/chat",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                # Should include cache control headers
                if "Cache-Control" in response.headers:
                    cache_control = response.headers["Cache-Control"]
                    # Should not cache streaming status (real-time data)
                    assert "no-cache" in cache_control or "no-store" in cache_control
                
                # Should include ETag for conditional requests
                if "ETag" in response.headers:
                    etag = response.headers["ETag"]
                    assert isinstance(etag, str)
                    assert len(etag) > 0
    
    @pytest.mark.asyncio
    async def test_get_streaming_status_conditional_request(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_session_id: str
    ):
        """Test conditional request with If-None-Match header"""
        async with httpx.AsyncClient() as client:
            # First request to get ETag
            response1 = await client.get(
                f"{base_url}/streaming/sessions/{valid_session_id}/chat",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response1.status_code == 200 and "ETag" in response1.headers:
                etag = response1.headers["ETag"]
                
                # Second request with If-None-Match
                response2 = await client.get(
                    f"{base_url}/streaming/sessions/{valid_session_id}/chat",
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json",
                        "If-None-Match": etag
                    }
                )
                
                # Should return 304 Not Modified
                assert response2.status_code == 304
    
    @pytest.mark.asyncio
    async def test_get_streaming_status_malformed_id_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test malformed session ID returns 422 Validation Error"""
        malformed_ids = [
            "   ",  # Whitespace only
            "id with spaces",  # Spaces in ID
        ]
        
        for malformed_id in malformed_ids:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url}/streaming/sessions/{malformed_id}/chat",
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
    async def test_get_streaming_status_expired_session(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test getting status for expired session"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/expired_session_test/chat",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should indicate expired status
                assert data["status"] == "expired"
                
                # Should have expiration time in the past
                from datetime import datetime
                expires_time = datetime.fromisoformat(data["expires_at"].replace('Z', '+00:00'))
                now = datetime.now(expires_time.tzinfo)
                assert expires_time < now
            else:
                # Or 410 Gone if expired sessions are not returned
                assert response.status_code == 410
    
    @pytest.mark.asyncio
    async def test_get_streaming_status_include_metrics(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_session_id: str
    ):
        """Test streaming status includes metrics if requested"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{valid_session_id}/chat?include_metrics=true",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should contain metrics if requested
                assert "metrics" in data
                assert isinstance(data["metrics"], dict)
                
                # Should contain useful metrics
                assert "bytes_transferred" in data["metrics"]
                assert "messages_sent" in data["metrics"]
                assert "uptime_seconds" in data["metrics"]
                assert "connection_quality" in data["metrics"]
    
    @pytest.mark.asyncio
    async def test_get_streaming_status_include_errors(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_session_id: str
    ):
        """Test streaming status includes errors if requested"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/streaming/sessions/{valid_session_id}/chat?include_errors=true",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should contain errors if requested
                assert "errors" in data
                assert isinstance(data["errors"], list)
                
                # Should contain error details
                for error in data["errors"]:
                    assert "code" in error
                    assert "message" in error
                    assert "timestamp" in error
