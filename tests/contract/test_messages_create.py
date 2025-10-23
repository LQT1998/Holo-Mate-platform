"""
Contract tests for POST /messages endpoint
"""

import pytest
import httpx
import uuid
from datetime import datetime, timezone


class TestMessageCreate:
    """Test cases for POST /messages endpoint"""

    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for the API"""
        return "http://localhost:8002/api/v1"

    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authentication"""
        return "valid_access_token_here"

    @pytest.fixture
    def valid_conversation_id(self) -> str:
        """Valid conversation ID for testing"""
        return "conversation_123"

    @pytest.fixture
    def valid_message_data(self, valid_conversation_id: str) -> dict:
        """Valid message creation data"""
        return {
            "content": "Hello, this is a test message",
            "role": "user",
            "content_type": "text",
            "conversation_id": valid_conversation_id
        }

    @pytest.mark.asyncio
    async def test_create_message_success_returns_201(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str,
        valid_message_data: dict
    ):
        """Test creating a message successfully returns 201 Created"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                json=valid_message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            
            # Check response structure
            assert "id" in data
            assert "conversation_id" in data
            assert "role" in data
            assert "content" in data
            assert "content_type" in data
            assert "created_at" in data
            
            # Check Location header
            assert "Location" in response.headers
            assert f"/messages/{data['id']}" in response.headers["Location"]
            
            # Check data values
            assert data["role"] == "user"
            assert data["content"] == "Hello, this is a test message"
            assert data["content_type"] == "text"

    @pytest.mark.asyncio
    async def test_create_message_with_companion_role_returns_201(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test creating a message with companion role returns 201"""
        message_data = {
            "content": "Hi! This is a reply from companion",
            "role": "companion",
            "content_type": "text",
            "conversation_id": valid_conversation_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                json=message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["role"] == "companion"

    @pytest.mark.asyncio
    async def test_create_message_with_audio_content_type_returns_201(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test creating a message with audio content type returns 201"""
        message_data = {
            "content": "https://example.com/audio.mp3",
            "role": "user",
            "content_type": "audio_url",
            "conversation_id": valid_conversation_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                json=message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["content_type"] == "audio_url"

    @pytest.mark.asyncio
    async def test_create_message_missing_authorization_returns_401(
        self,
        base_url: str,
        valid_conversation_id: str,
        valid_message_data: dict
    ):
        """Test creating a message without authorization returns 401"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                json=valid_message_data,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_message_invalid_token_returns_401(
        self,
        base_url: str,
        valid_conversation_id: str,
        valid_message_data: dict
    ):
        """Test creating a message with invalid token returns 401"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                json=valid_message_data,
                headers={
                    "Authorization": "Bearer invalid_token",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_message_invalid_conversation_id_format_returns_422(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test creating a message with invalid conversation ID format returns 422"""
        message_data = {
            "content": "Hello",
            "role": "user",
            "content_type": "text",
            "conversation_id": "invalid_conversation_id"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/invalid_conversation_id/messages",
                json=message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_message_nonexistent_conversation_returns_404(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test creating a message for nonexistent conversation returns 404"""
        message_data = {
            "content": "Hello",
            "role": "user",
            "content_type": "text",
            "conversation_id": "nonexistent_conversation_456"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/nonexistent_conversation_456/messages",
                json=message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_message_forbidden_conversation_returns_403(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test creating a message for forbidden conversation returns 403"""
        message_data = {
            "content": "Hello",
            "role": "user",
            "content_type": "text",
            "conversation_id": "forbidden_999"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/forbidden_999/messages",
                json=message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_message_empty_content_returns_422(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test creating a message with empty content returns 422"""
        message_data = {
            "content": "",
            "role": "user",
            "content_type": "text",
            "conversation_id": valid_conversation_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                json=message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_message_invalid_role_returns_422(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test creating a message with invalid role returns 422"""
        message_data = {
            "content": "Hello",
            "role": "invalid_role",
            "content_type": "text",
            "conversation_id": valid_conversation_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                json=message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_message_invalid_content_type_returns_422(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test creating a message with invalid content type returns 422"""
        message_data = {
            "content": "Hello",
            "role": "user",
            "content_type": "invalid_type",
            "conversation_id": valid_conversation_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                json=message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_message_missing_required_fields_returns_422(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test creating a message with missing required fields returns 422"""
        message_data = {
            "content": "Hello"
            # Missing role, content_type, conversation_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                json=message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_message_long_content_returns_422(
        self,
        base_url: str,
        valid_access_token: str,
        valid_conversation_id: str
    ):
        """Test creating a message with content too long returns 422"""
        message_data = {
            "content": "x" * 10001,  # Exceeds 10000 character limit
            "role": "user",
            "content_type": "text",
            "conversation_id": valid_conversation_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/conversations/{valid_conversation_id}/messages",
                json=message_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 422
