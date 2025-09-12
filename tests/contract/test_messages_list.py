"""
Contract test for GET /conversations/{id}/messages endpoint
Tests the messages list API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any, List


class TestMessagesListContract:
    """Contract tests for GET /conversations/{id}/messages endpoint"""
    
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
    async def test_get_messages_success_returns_200_and_list(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test successful messages list returns 200 with messages data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
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
            
            # Should contain messages list
            assert "messages" in data
            assert isinstance(data["messages"], list)
            
            # Should contain pagination info
            assert "total" in data
            assert "page" in data
            assert "per_page" in data
            assert "total_pages" in data
            
            # Pagination should be valid
            assert isinstance(data["total"], int)
            assert isinstance(data["page"], int)
            assert isinstance(data["per_page"], int)
            assert isinstance(data["total_pages"], int)
            assert data["page"] >= 1
            assert data["per_page"] > 0
            assert data["total_pages"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_messages_with_pagination(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test messages list with pagination parameters"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?page=1&per_page=10",
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
            
            # Should respect pagination parameters
            assert data["page"] == 1
            assert data["per_page"] == 10
            assert len(data["messages"]) <= 10
    
    @pytest.mark.asyncio
    async def test_get_messages_with_sender_filter(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test messages list with sender filter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?sender=user",
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
            
            # Should contain filtered results
            assert "messages" in data
            assert isinstance(data["messages"], list)
    
    @pytest.mark.asyncio
    async def test_get_messages_with_date_range(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test messages list with date range filter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?start_date=2023-01-01&end_date=2023-12-31",
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
            
            # Should contain filtered results
            assert "messages" in data
            assert isinstance(data["messages"], list)
    
    @pytest.mark.asyncio
    async def test_get_messages_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_conversation_id: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
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
    async def test_get_messages_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_conversation_id: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
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
    async def test_get_messages_nonexistent_conversation_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_conversation_id: str
    ):
        """Test getting messages for non-existent conversation returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{nonexistent_conversation_id}/messages",
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
    async def test_get_messages_unauthorized_access_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test accessing messages for conversation owned by another user returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
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
    async def test_get_messages_invalid_pagination_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test invalid pagination parameters returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?page=0&per_page=-1",
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
    async def test_get_messages_invalid_date_format_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test invalid date format returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?start_date=invalid-date&end_date=also-invalid",
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
    async def test_get_messages_message_structure(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test message data structure is complete and properly formatted"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data["messages"]
                
                if len(messages) > 0:
                    message = messages[0]
                    
                    # Required fields should be present
                    required_fields = [
                        "id", "content", "sender", "timestamp", 
                        "message_type", "conversation_id"
                    ]
                    for field in required_fields:
                        assert field in message, f"Missing required field: {field}"
                    
                    # ID should be valid
                    assert isinstance(message["id"], (str, int))
                    
                    # Content should be string
                    assert isinstance(message["content"], str)
                    assert len(message["content"]) > 0
                    
                    # Sender should be valid
                    valid_senders = ["user", "assistant", "system"]
                    assert message["sender"] in valid_senders
                    
                    # Message type should be valid
                    valid_types = ["text", "voice", "image", "file", "system"]
                    assert message["message_type"] in valid_types
                    
                    # Timestamp should be ISO format
                    import re
                    iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
                    assert re.match(iso_pattern, message["timestamp"])
    
    @pytest.mark.asyncio
    async def test_get_messages_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test messages list response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
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
    async def test_get_messages_empty_list(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test messages list returns empty list when no messages exist"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return empty list structure
                assert "messages" in data
                assert isinstance(data["messages"], list)
                assert len(data["messages"]) == 0
                
                # Pagination should still be valid
                assert data["total"] == 0
                assert data["page"] >= 1
                assert data["per_page"] > 0
                assert data["total_pages"] == 0
    
    @pytest.mark.asyncio
    async def test_get_messages_sorting(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test messages list with sorting parameters"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?sort_by=timestamp&sort_order=desc",
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
            
            # Should contain messages list
            assert "messages" in data
            assert isinstance(data["messages"], list)
    
    @pytest.mark.asyncio
    async def test_get_messages_invalid_sort_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test invalid sorting parameters returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?sort_by=invalid_field&sort_order=invalid",
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
    async def test_get_messages_caching_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test that messages list response includes appropriate caching headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
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
    async def test_get_messages_search(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test messages list with search parameter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?search=hello",
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
            
            # Should contain filtered results
            assert "messages" in data
            assert isinstance(data["messages"], list)
    
    @pytest.mark.asyncio
    async def test_get_messages_limit_parameter(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test messages list with limit parameter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?limit=5",
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
            
            # Should respect limit parameter
            assert len(data["messages"]) <= 5
    
    @pytest.mark.asyncio
    async def test_get_messages_offset_parameter(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test messages list with offset parameter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?offset=10&limit=5",
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
            
            # Should contain messages list
            assert "messages" in data
            assert isinstance(data["messages"], list)
    
    @pytest.mark.asyncio
    async def test_get_messages_include_metadata(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test messages list includes metadata"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?include_metadata=true",
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
            
            # Should contain messages list
            assert "messages" in data
            assert isinstance(data["messages"], list)
            
            # Should contain metadata if requested
            if "include_metadata" in response.url.params:
                assert "metadata" in data
