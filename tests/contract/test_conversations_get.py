"""
Contract test for GET /conversations/{id} endpoint
Tests the conversation retrieval API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestConversationsGetContract:
    """Contract tests for GET /conversations/{id} endpoint"""
    
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
    
    @pytest.mark.asyncio
    async def test_get_conversation_success_returns_200_and_conversation_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test successful conversation retrieval returns 200 with conversation data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}",
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
            
            # Should contain conversation ID
            assert "id" in data
            assert data["id"] == valid_conversation_id
            
            # Should contain basic conversation info
            assert "title" in data
            assert "companion_id" in data
            assert "status" in data
            assert isinstance(data["title"], str)
            assert isinstance(data["companion_id"], (str, int))
            assert isinstance(data["status"], str)
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            assert "last_message_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)
            assert isinstance(data["last_message_at"], str)
            
            # Should contain settings
            assert "settings" in data
            assert isinstance(data["settings"], dict)
            assert "voice_enabled" in data["settings"]
            assert "emotion_detection" in data["settings"]
            assert "response_length" in data["settings"]
            assert "formality_level" in data["settings"]
            
            # Should contain message count
            assert "message_count" in data
            assert isinstance(data["message_count"], int)
            assert data["message_count"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_conversation_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_conversation_id: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}",
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
    async def test_get_conversation_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_conversation_id: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}",
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
    async def test_get_conversation_nonexistent_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_conversation_id: str
    ):
        """Test non-existent conversation returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{nonexistent_conversation_id}",
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
    async def test_get_conversation_unauthorized_access_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test accessing conversation owned by another user returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}",
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
    async def test_get_conversation_invalid_id_format_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_conversation_id: str
    ):
        """Test invalid conversation ID format returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{invalid_conversation_id}",
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
    async def test_get_conversation_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test conversation retrieval response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}",
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
    async def test_get_conversation_data_structure_validation(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test conversation data structure is complete and properly formatted"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Required fields should be present
                required_fields = [
                    "id", "title", "companion_id", "status", 
                    "created_at", "updated_at", "last_message_at",
                    "settings", "message_count"
                ]
                for field in required_fields:
                    assert field in data, f"Missing required field: {field}"
                
                # Settings should have required fields
                settings_fields = ["voice_enabled", "emotion_detection", "response_length", "formality_level"]
                for field in settings_fields:
                    assert field in data["settings"], f"Missing settings field: {field}"
                
                # Data types should be correct
                assert isinstance(data["title"], str)
                assert isinstance(data["companion_id"], (str, int))
                assert isinstance(data["status"], str)
                assert isinstance(data["settings"], dict)
                assert isinstance(data["message_count"], int)
                
                # Status should be valid
                valid_statuses = ["active", "paused", "ended", "archived"]
                assert data["status"] in valid_statuses
    
    @pytest.mark.asyncio
    async def test_get_conversation_timestamps_format(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test conversation timestamps are in correct ISO format"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}",
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
                assert re.match(iso_pattern, data["last_message_at"])
                
                # Updated timestamp should be >= created timestamp
                from datetime import datetime
                created_time = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
                updated_time = datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
                assert updated_time >= created_time
    
    @pytest.mark.asyncio
    async def test_get_conversation_caching_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test that conversation retrieval response includes appropriate caching headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                # Should include cache control headers
                if "Cache-Control" in response.headers:
                    cache_control = response.headers["Cache-Control"]
                    # Should cache for short period
                    assert "max-age" in cache_control or "no-cache" in cache_control
                
                # Should include ETag for conditional requests
                if "ETag" in response.headers:
                    etag = response.headers["ETag"]
                    assert isinstance(etag, str)
                    assert len(etag) > 0
    
    @pytest.mark.asyncio
    async def test_get_conversation_conditional_request(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test conditional request with If-None-Match header"""
        async with httpx.AsyncClient() as client:
            # First request to get ETag
            response1 = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response1.status_code == 200 and "ETag" in response1.headers:
                etag = response1.headers["ETag"]
                
                # Second request with If-None-Match
                response2 = await client.get(
                    f"{base_url}/conversations/{valid_conversation_id}",
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json",
                        "If-None-Match": etag
                    }
                )
                
                # Should return 304 Not Modified
                assert response2.status_code == 304
    
    @pytest.mark.asyncio
    async def test_get_conversation_malformed_id_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test malformed conversation ID returns 422 Validation Error"""
        malformed_ids = [
            "",  # Empty ID
            "   ",  # Whitespace only
            "id with spaces",  # Spaces in ID
            "id\nwith\nnewlines",  # Newlines in ID
            "id\twith\ttabs",  # Tabs in ID
        ]
        
        for malformed_id in malformed_ids:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url}/conversations/{malformed_id}",
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
    async def test_get_conversation_include_messages_parameter(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test conversation retrieval with include_messages parameter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}?include_messages=true",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should contain messages if requested
                assert "messages" in data
                assert isinstance(data["messages"], list)
                
                # Should contain message count
                assert "message_count" in data
                assert data["message_count"] == len(data["messages"])
    
    @pytest.mark.asyncio
    async def test_get_conversation_include_companion_parameter(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test conversation retrieval with include_companion parameter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}?include_companion=true",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should contain companion data if requested
                assert "companion" in data
                assert isinstance(data["companion"], dict)
                
                # Should contain companion basic info
                assert "id" in data["companion"]
                assert "name" in data["companion"]
                assert "description" in data["companion"]
    
    @pytest.mark.asyncio
    async def test_get_conversation_include_metadata_parameter(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test conversation retrieval with include_metadata parameter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}?include_metadata=true",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should contain metadata if requested
                assert "metadata" in data
                assert isinstance(data["metadata"], dict)
                
                # Should contain useful metadata
                assert "duration_seconds" in data["metadata"]
                assert "total_tokens" in data["metadata"]
                assert "average_response_time" in data["metadata"]
