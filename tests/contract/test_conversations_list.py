"""
Contract test for GET /conversations endpoint
Tests the conversations list API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any, List


class TestConversationsListContract:
    """Contract tests for GET /conversations endpoint"""
    
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
    
    @pytest.mark.asyncio
    async def test_get_conversations_success_returns_200_and_list(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test successful conversations list returns 200 with conversations data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations",
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
            
            # Should contain conversations list
            assert "conversations" in data
            assert isinstance(data["conversations"], list)
            
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
    async def test_get_conversations_with_pagination(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list with pagination parameters"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?page=1&per_page=10",
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
            assert len(data["conversations"]) <= 10
    
    @pytest.mark.asyncio
    async def test_get_conversations_with_companion_filter(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list with companion filter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?companion_id=companion_123",
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
            assert "conversations" in data
            assert isinstance(data["conversations"], list)
    
    @pytest.mark.asyncio
    async def test_get_conversations_with_status_filter(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list with status filter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?status=active",
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
            assert "conversations" in data
            assert isinstance(data["conversations"], list)
    
    @pytest.mark.asyncio
    async def test_get_conversations_with_date_range(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list with date range filter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?start_date=2023-01-01&end_date=2023-12-31",
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
            assert "conversations" in data
            assert isinstance(data["conversations"], list)
    
    @pytest.mark.asyncio
    async def test_get_conversations_missing_auth_returns_401(
        self, 
        base_url: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations",
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
    async def test_get_conversations_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations",
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
    async def test_get_conversations_invalid_pagination_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test invalid pagination parameters returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?page=0&per_page=-1",
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
    async def test_get_conversations_invalid_date_format_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test invalid date format returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?start_date=invalid-date&end_date=also-invalid",
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
    async def test_get_conversations_conversation_structure(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversation data structure is complete and properly formatted"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                conversations = data["conversations"]
                
                if len(conversations) > 0:
                    conversation = conversations[0]
                    
                    # Required fields should be present
                    required_fields = [
                        "id", "title", "companion_id", "status", 
                        "created_at", "updated_at", "last_message_at"
                    ]
                    for field in required_fields:
                        assert field in conversation, f"Missing required field: {field}"
                    
                    # ID should be valid
                    assert isinstance(conversation["id"], (str, int))
                    
                    # Title should be string
                    assert isinstance(conversation["title"], str)
                    
                    # Companion ID should be valid
                    assert isinstance(conversation["companion_id"], (str, int))
                    
                    # Status should be valid
                    valid_statuses = ["active", "paused", "ended", "archived"]
                    assert conversation["status"] in valid_statuses
                    
                    # Timestamps should be ISO format
                    import re
                    iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
                    assert re.match(iso_pattern, conversation["created_at"])
                    assert re.match(iso_pattern, conversation["updated_at"])
                    assert re.match(iso_pattern, conversation["last_message_at"])
    
    @pytest.mark.asyncio
    async def test_get_conversations_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations",
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
    async def test_get_conversations_empty_list(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list returns empty list when no conversations exist"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return empty list structure
                assert "conversations" in data
                assert isinstance(data["conversations"], list)
                assert len(data["conversations"]) == 0
                
                # Pagination should still be valid
                assert data["total"] == 0
                assert data["page"] >= 1
                assert data["per_page"] > 0
                assert data["total_pages"] == 0
    
    @pytest.mark.asyncio
    async def test_get_conversations_sorting(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list with sorting parameters"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?sort_by=created_at&sort_order=desc",
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
            
            # Should contain conversations list
            assert "conversations" in data
            assert isinstance(data["conversations"], list)
    
    @pytest.mark.asyncio
    async def test_get_conversations_invalid_sort_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test invalid sorting parameters returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?sort_by=invalid_field&sort_order=invalid",
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
    async def test_get_conversations_caching_headers(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test that conversations list response includes appropriate caching headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations",
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
    async def test_get_conversations_search(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list with search parameter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?search=hello",
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
            assert "conversations" in data
            assert isinstance(data["conversations"], list)
    
    @pytest.mark.asyncio
    async def test_get_conversations_limit_parameter(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list with limit parameter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?limit=5",
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
            assert len(data["conversations"]) <= 5
    
    @pytest.mark.asyncio
    async def test_get_conversations_offset_parameter(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list with offset parameter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?offset=10&limit=5",
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
            
            # Should contain conversations list
            assert "conversations" in data
            assert isinstance(data["conversations"], list)
    
    @pytest.mark.asyncio
    async def test_get_conversations_include_metadata(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test conversations list includes metadata"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations?include_metadata=true",
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
            
            # Should contain conversations list
            assert "conversations" in data
            assert isinstance(data["conversations"], list)
            
            # Should contain metadata if requested
            if "include_metadata" in response.url.params:
                assert "metadata" in data
