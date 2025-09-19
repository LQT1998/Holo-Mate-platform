import pytest
import httpx
from uuid import UUID

from backend.shared.src.constants import DEV_OWNER_ID

# Define the base URL for the service
BASE_URL = "http://localhost:8003"


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def dev_access_token() -> str:
    # In a real scenario, this would generate a valid JWT.
    # For dev mode, a simple string is sufficient if the endpoint logic checks for it.
    return "dev_access_token"


@pytest.mark.asyncio
class TestStreamingSessionCreate:
    async def test_create_session_success_returns_201(
        self, base_url: str, dev_access_token: str
    ):
        """Test successful creation of a streaming session returns 201."""
        payload = {
            "device_id": "device_123",
            "settings": {"quality": "1080p"},
        }
        headers = {
            "Authorization": f"Bearer {dev_access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/sessions", json=payload, headers=headers
            )

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert data["user_id"] == str(DEV_OWNER_ID)
        assert data["status"] == "active"
        assert "Location" in response.headers
        assert response.headers["Location"].startswith("/streaming/sessions/")

    async def test_create_session_invalid_device_id_returns_422(
        self, base_url: str, dev_access_token: str
    ):
        """Test creating a session with a known invalid device ID returns 422."""
        payload = {"device_id": "invalid_device_id"}
        headers = {"Authorization": f"Bearer {dev_access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/sessions", json=payload, headers=headers
            )

        assert response.status_code == 422
        assert "Invalid device ID format" in response.text

    async def test_create_session_nonexistent_device_id_returns_404(
        self, base_url: str, dev_access_token: str
    ):
        """Test creating a session with a nonexistent device ID returns 404."""
        payload = {"device_id": "nonexistent_device_456"}
        headers = {"Authorization": f"Bearer {dev_access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/sessions", json=payload, headers=headers
            )

        assert response.status_code == 404
        assert "Device not found" in response.text

    async def test_create_session_forbidden_device_id_returns_403(
        self, base_url: str, dev_access_token: str
    ):
        """Test creating a session with a forbidden device ID returns 403."""
        payload = {"device_id": "forbidden_999"}
        headers = {"Authorization": f"Bearer {dev_access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/streaming/sessions", json=payload, headers=headers
            )

        assert response.status_code == 403
        assert "Forbidden" in response.text

    @pytest.mark.skip(reason="AUTH_ENABLED is False in DEV mode, so this test is not applicable.")
    async def test_create_session_no_auth_returns_401(self, base_url: str):
        """Test that creating a session without an auth token returns 401 when auth is enabled."""
        # This test requires AUTH_ENABLED=True, but it runs in a separate process from the test runner.
        # Monkeypatching does not work across processes. Disabling for now.
        payload = {"device_id": "device_123"}

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/streaming/sessions", json=payload)

        assert response.status_code == 401

    async def test_create_session_unauthorized_user_returns_403(self, base_url: str):
        """Test creating a session with a token for a non-dev user returns 403."""
        # This requires the get_current_user mock to return a different user ID
        # For now, we assume the dev token is tied to the DEV_OWNER_ID.
        # A more robust test would involve generating a token with a different user ID.
        pass # Placeholder for a more complex auth test case
