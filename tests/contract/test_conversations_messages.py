"""
Contract tests for conversation messages endpoints.

Tests the /conversations/{id}/messages endpoint according to the API specification.
These tests define the expected behavior and should be written BEFORE implementation.
"""

import httpx
import pytest
from typing import Dict, Any


class TestConversationsMessagesContract:
    """Contract tests for conversation messages endpoints."""

    @pytest.mark.asyncio
    async def test_get_conversation_messages_success_returns_200_and_messages(
        self,
        ai_base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test successful retrieval of conversation messages returns 200 with message list"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/conversations/{valid_conversation_id}/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 200 OK
            assert response.status_code == 200
            
            data = response.json()
            assert "messages" in data
            assert isinstance(data["messages"], list)
            
            # Check message structure if messages exist
            if data["messages"]:
                message = data["messages"][0]
                assert "id" in message
                assert "role" in message
                assert "content" in message
                assert "created_at" in message
                assert message["role"] in ["user", "assistant", "system"]

    @pytest.mark.asyncio
    async def test_get_conversation_messages_missing_auth_returns_401(
        self,
        ai_base_url: str,
        valid_conversation_id: str
    ):
        """Test missing authentication returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/conversations/{valid_conversation_id}/messages"
            )

            # Should return 401 Unauthorized
            assert response.status_code == 401
            assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_conversation_messages_invalid_token_returns_401(
        self,
        ai_base_url: str,
        valid_conversation_id: str
    ):
        """Test invalid token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/conversations/{valid_conversation_id}/messages",
                headers={
                    "Authorization": "Bearer invalid_token",
                    "Content-Type": "application/json"
                }
            )

            # Should return 401 Unauthorized
            assert response.status_code == 401
            assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_conversation_messages_nonexistent_conversation_returns_404(
        self,
        ai_base_url: str,
        valid_access_token: str
    ):
        """Test nonexistent conversation returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/conversations/nonexistent_conversation_id/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 404 Not Found
            assert response.status_code == 404
            assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_conversation_messages_forbidden_conversation_returns_403(
        self,
        ai_base_url: str,
        valid_access_token: str
    ):
        """Test accessing another user's conversation returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/conversations/forbidden_conversation_id/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 403 Forbidden
            assert response.status_code == 403
            assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_conversation_messages_pagination_returns_200(
        self,
        ai_base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test pagination parameters work correctly"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/conversations/{valid_conversation_id}/messages",
                params={"limit": 10, "offset": 0},
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 200 OK
            assert response.status_code == 200
            
            data = response.json()
            assert "messages" in data
            assert len(data["messages"]) <= 10

    @pytest.mark.asyncio
    async def test_get_conversation_messages_response_headers(
        self,
        ai_base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test response headers are correct"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/conversations/{valid_conversation_id}/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 200 OK
            assert response.status_code == 200
            assert "Content-Type" in response.headers
            assert "application/json" in response.headers["Content-Type"]

    @pytest.mark.asyncio
    async def test_get_conversation_messages_data_structure_validation(
        self,
        ai_base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test message data structure validation"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/conversations/{valid_conversation_id}/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 200 OK
            assert response.status_code == 200
            
            data = response.json()
            assert "messages" in data
            assert isinstance(data["messages"], list)
            
            # Validate each message structure
            for message in data["messages"]:
                assert "id" in message
                assert "role" in message
                assert "content" in message
                assert "created_at" in message
                assert "updated_at" in message
                
                # Validate role values
                assert message["role"] in ["user", "assistant", "system"]
                
                # Validate content is not empty
                assert len(message["content"]) > 0
                
                # Validate timestamps are ISO format
                assert "T" in message["created_at"]
                assert "T" in message["updated_at"]

    @pytest.mark.asyncio
    async def test_get_conversation_messages_empty_conversation_returns_200(
        self,
        ai_base_url: str,
        valid_access_token: str
    ):
        """Test empty conversation returns 200 with empty message list"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/conversations/empty_conversation_id/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 200 OK
            assert response.status_code == 200
            
            data = response.json()
            assert "messages" in data
            assert data["messages"] == []

    @pytest.mark.asyncio
    async def test_get_conversation_messages_caching_headers(
        self,
        ai_base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test caching headers are present"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/conversations/{valid_conversation_id}/messages",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 200 OK
            assert response.status_code == 200
            
            # Check for caching headers
            assert "Cache-Control" in response.headers or "ETag" in response.headers