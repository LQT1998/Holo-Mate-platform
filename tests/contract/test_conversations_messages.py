"""
Contract tests for GET /conversations/{conversation_id}/messages endpoint
"""

import pytest
import httpx
from typing import Dict, Any


class TestConversationMessages:
    """Test cases for GET /conversations/{conversation_id}/messages endpoint"""

    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for AI service"""
        return "http://localhost:8002"

    @pytest.fixture
    def valid_conversation_id(self) -> str:
        """Valid conversation ID for testing"""
        return "conversation_123"

    @pytest.fixture
    def nonexistent_conversation_id(self) -> str:
        """Non-existent conversation ID for testing 404"""
        return "nonexistent_conversation_456"

    @pytest.fixture
    def forbidden_conversation_id(self) -> str:
        """Conversation ID owned by another user for testing 403"""
        return "forbidden_999"

    @pytest.fixture
    def invalid_conversation_id(self) -> str:
        """Invalid conversation ID format for testing 422"""
        return "invalid_conversation_id"

    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for testing"""
        return "valid_access_token_here"

    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing 401"""
        return "invalid_token"

    @pytest.mark.asyncio
    async def test_get_conversation_messages_success_returns_200_and_messages(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test getting conversation messages returns 200 and correct message data"""
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
            
            # Should return message list with pagination
            data = response.json()
            assert isinstance(data, dict)
            assert "messages" in data
            assert "total" in data
            assert "page" in data
            assert "per_page" in data
            assert "total_pages" in data
            
            # Check messages structure
            messages = data["messages"]
            assert isinstance(messages, list)
            assert len(messages) > 0
            
            # Check first message structure
            first_message = messages[0]
            assert "id" in first_message
            assert "conversation_id" in first_message
            assert "sender_type" in first_message
            assert "content" in first_message
            assert "content_type" in first_message
            assert "created_at" in first_message
            
            # Check pagination
            assert data["total"] > 0
            assert data["page"] == 1
            assert data["per_page"] == 20
            assert data["total_pages"] >= 1

    @pytest.mark.asyncio
    async def test_get_conversation_messages_with_pagination_returns_correct_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test getting conversation messages with pagination parameters"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{valid_conversation_id}/messages?page=1&per_page=2",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 200 OK
            assert response.status_code == 200
            
            # Should return paginated data
            data = response.json()
            assert data["page"] == 1
            assert data["per_page"] == 2
            assert len(data["messages"]) <= 2

    @pytest.mark.asyncio
    async def test_get_conversation_messages_unauthorized_returns_401(
        self, 
        base_url: str, 
        valid_conversation_id: str
    ):
        """Test getting conversation messages without token returns 401"""
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
    async def test_get_conversation_messages_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_conversation_id: str
    ):
        """Test getting conversation messages with invalid token returns 401"""
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
    async def test_get_conversation_messages_nonexistent_conversation_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_conversation_id: str
    ):
        """Test getting messages for non-existent conversation returns 404"""
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
    async def test_get_conversation_messages_forbidden_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str,
        forbidden_conversation_id: str
    ):
        """Test getting messages for conversation owned by another user returns 403"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{forbidden_conversation_id}/messages",
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
    async def test_get_conversation_messages_invalid_id_format_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_conversation_id: str
    ):
        """Test getting messages with invalid conversation ID format returns 422"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/{invalid_conversation_id}/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0

    @pytest.mark.asyncio
    async def test_get_conversation_messages_invalid_pagination_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test getting messages with invalid pagination parameters returns 422"""
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
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            # FastAPI validation errors can be either string or list
            assert isinstance(data["detail"], (str, list))
            if isinstance(data["detail"], list):
                assert len(data["detail"]) > 0
            else:
                assert len(data["detail"]) > 0

    @pytest.mark.asyncio
    async def test_get_conversation_messages_empty_conversation_returns_empty_list(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test getting messages for conversation with no messages returns empty list"""
        # This test assumes there's a conversation with no messages
        # In DEV mode, we'll use a special conversation ID
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/conversations/empty_conversation_789/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 200 OK (conversation exists but no messages)
            assert response.status_code == 200
            
            # Should return empty message list
            data = response.json()
            assert isinstance(data, dict)
            assert "messages" in data
            assert isinstance(data["messages"], list)
            assert len(data["messages"]) == 0
            assert data["total"] == 0
            assert data["page"] == 1
            assert data["per_page"] == 20
            assert data["total_pages"] == 0
