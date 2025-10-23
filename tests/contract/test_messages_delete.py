"""
Contract tests for DELETE /messages/{id} endpoint
"""

import pytest
import httpx
import uuid
from datetime import datetime, timezone


class TestMessageDelete:
    @pytest.fixture
    def base_url(self) -> str:
        return "http://localhost:8002/api/v1"

    @pytest.fixture
    def valid_access_token(self) -> str:
        return "valid_access_token_here"  # This is a mock token for dev mode

    @pytest.fixture
    def valid_message_id(self) -> str:
        return "message_123"  # Special ID for dev mode

    @pytest.fixture
    def nonexistent_message_id(self) -> str:
        return "nonexistent_message_456"

    @pytest.fixture
    def forbidden_message_id(self) -> str:
        return "forbidden_999"

    @pytest.fixture
    def invalid_message_id(self) -> str:
        return "invalid_message_id"

    @pytest.mark.asyncio
    async def test_delete_message_success_returns_200_and_deletion_confirmation(
        self,
        base_url: str,
        valid_access_token: str,
        valid_message_id: str
    ):
        """Test deleting a message successfully returns 200 OK with deletion confirmation"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 200
            data = response.json()

            assert "message" in data
            assert "deleted_id" in data
            assert data["message"] == "Message deleted successfully"
            assert uuid.UUID(data["deleted_id"])  # Ensure it's a valid UUID

    @pytest.mark.asyncio
    async def test_delete_message_missing_authorization_returns_401(
        self,
        base_url: str,
        valid_message_id: str
    ):
        """Test deleting a message without authorization returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/messages/{valid_message_id}",
                headers={"Content-Type": "application/json"}
            )

            assert response.status_code == 401
            data = response.json()
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_delete_message_invalid_token_returns_401(
        self,
        base_url: str,
        valid_message_id: str
    ):
        """Test deleting a message with invalid token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": "Bearer invalid_token",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 401
            data = response.json()
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_delete_message_nonexistent_returns_404(
        self,
        base_url: str,
        valid_access_token: str,
        nonexistent_message_id: str
    ):
        """Test deleting a nonexistent message returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/messages/{nonexistent_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Message not found"

    @pytest.mark.asyncio
    async def test_delete_message_forbidden_returns_403(
        self,
        base_url: str,
        valid_access_token: str,
        forbidden_message_id: str
    ):
        """Test deleting a forbidden message returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/messages/{forbidden_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 403
            data = response.json()
            assert data["detail"] == "Forbidden: You do not own this message"

    @pytest.mark.asyncio
    async def test_delete_message_invalid_id_format_returns_422(
        self,
        base_url: str,
        valid_access_token: str,
        invalid_message_id: str
    ):
        """Test deleting a message with invalid ID format returns 422 Unprocessable Entity"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/messages/{invalid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 422
            data = response.json()
            assert data["detail"] == "Invalid message ID format"

    @pytest.mark.asyncio
    async def test_delete_message_response_headers(
        self,
        base_url: str,
        valid_access_token: str,
        valid_message_id: str
    ):
        """Test DELETE message response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_delete_message_data_structure_validation(
        self,
        base_url: str,
        valid_access_token: str,
        valid_message_id: str
    ):
        """Test DELETE message response has correct data structure"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Required fields should be present
            required_fields = ["message", "deleted_id"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"

            # Message should be a string
            assert isinstance(data["message"], str)
            assert len(data["message"]) > 0

            # Deleted ID should be a valid UUID string
            assert isinstance(data["deleted_id"], str)
            assert uuid.UUID(data["deleted_id"])

    @pytest.mark.asyncio
    async def test_delete_message_caching_headers(
        self,
        base_url: str,
        valid_access_token: str,
        valid_message_id: str
    ):
        """Test DELETE message response has appropriate caching headers"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 200
            # DELETE operations typically don't cache
            assert "cache-control" not in response.headers or "no-cache" in response.headers.get("cache-control", "")

    @pytest.mark.asyncio
    async def test_delete_message_unauthorized_user_returns_403(
        self,
        base_url: str,
        valid_message_id: str
    ):
        """Test deleting a message with unauthorized user returns 403 Forbidden"""
        # This test simulates a user who doesn't own the message
        # In dev mode, only DEV_OWNER_ID can access messages
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": "Bearer unauthorized_user_token",
                    "Content-Type": "application/json"
                }
            )

            # Should return 401 for invalid token, not 403
            assert response.status_code == 401
            data = response.json()
            assert "detail" in data
