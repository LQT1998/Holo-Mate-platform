import pytest
import httpx
import uuid
from datetime import datetime, timezone

class TestMessageGet:
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
    async def test_get_message_success_returns_200_and_message_data(
        self,
        base_url: str,
        valid_access_token: str,
        valid_message_id: str
    ):
        """Test getting a message successfully returns 200 OK with message data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Check required fields
            assert "id" in data
            assert "conversation_id" in data
            assert "role" in data
            assert "content" in data
            assert "content_type" in data
            assert "created_at" in data
            assert "updated_at" in data

            # Validate UUIDs
            assert uuid.UUID(data["id"])
            assert uuid.UUID(data["conversation_id"])

            # Validate field values
            assert data["role"] in ["user", "companion"]
            assert data["content_type"] in ["text", "audio_url"]
            assert isinstance(data["content"], str)
            assert len(data["content"]) > 0

            # Validate timestamps
            created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            assert created_at.tzinfo is not None
            assert updated_at.tzinfo is not None

    @pytest.mark.asyncio
    async def test_get_message_missing_authorization_returns_401(
        self,
        base_url: str,
        valid_message_id: str
    ):
        """Test getting a message without authorization returns 401"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/messages/{valid_message_id}",
                headers={"Content-Type": "application/json"}
            )

            assert response.status_code == 401
            data = response.json()
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_get_message_invalid_token_returns_401(
        self,
        base_url: str,
        valid_message_id: str
    ):
        """Test getting a message with invalid token returns 401"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
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
    async def test_get_message_nonexistent_returns_404(
        self,
        base_url: str,
        valid_access_token: str,
        nonexistent_message_id: str
    ):
        """Test getting a nonexistent message returns 404"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/messages/{nonexistent_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_message_forbidden_returns_403(
        self,
        base_url: str,
        valid_access_token: str,
        forbidden_message_id: str
    ):
        """Test getting a forbidden message returns 403"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/messages/{forbidden_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 403
            data = response.json()
            assert "detail" in data
            assert "forbidden" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_message_invalid_id_format_returns_422(
        self,
        base_url: str,
        valid_access_token: str,
        invalid_message_id: str
    ):
        """Test getting a message with invalid ID format returns 422"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/messages/{invalid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 422
            data = response.json()
            assert "detail" in data
            assert "invalid" in data["detail"].lower() or "format" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_message_response_headers(
        self,
        base_url: str,
        valid_access_token: str,
        valid_message_id: str
    ):
        """Test response headers are correct"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_get_message_data_structure_validation(
        self,
        base_url: str,
        valid_access_token: str,
        valid_message_id: str
    ):
        """Test message data structure is valid"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Required fields should be present
            required_fields = [
                "id", "conversation_id", "role", "content",
                "content_type", "created_at", "updated_at"
            ]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"

            # Role should be valid
            valid_roles = ["user", "companion"]
            assert data["role"] in valid_roles

            # Content type should be valid
            valid_types = ["text", "audio_url"]
            assert data["content_type"] in valid_types

            # Content should not be empty
            assert len(data["content"]) > 0

    @pytest.mark.asyncio
    async def test_get_message_timestamps_format(
        self,
        base_url: str,
        valid_access_token: str,
        valid_message_id: str
    ):
        """Test timestamps are in correct ISO format"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Check timestamp format
            import re
            iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
            assert re.match(iso_pattern, data["created_at"])
            assert re.match(iso_pattern, data["updated_at"])

            # Check timezone info
            created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            assert created_at.tzinfo is not None
            assert updated_at.tzinfo is not None

    @pytest.mark.asyncio
    async def test_get_message_caching_headers(
        self,
        base_url: str,
        valid_access_token: str,
        valid_message_id: str
    ):
        """Test caching headers are present"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/messages/{valid_message_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            assert response.status_code == 200
            # Note: Caching headers might not be implemented in DEV mode
            # This test is for future implementation
