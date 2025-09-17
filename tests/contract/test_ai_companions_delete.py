import pytest
import httpx
from typing import Dict, Any
import uuid
from datetime import datetime, timedelta, timezone

# Import JWT helpers for token generation
from backend.shared.src.security.security import create_access_token
from backend.shared.src.security.security import jwt
from backend.ai_service.src.config import settings
from backend.shared.src.constants import (
    DEV_KNOWN_COMPANION_ID,
    DEV_FORBIDDEN_ID,
    DEV_NONEXISTENT_PREFIX,
    DEV_VALID_TOKEN,
    DEV_INVALID_TOKEN,
    create_expired_token,
    AI_SERVICE_URL,
)


class TestDeleteAICompanions:
    """Contract tests for DELETE /ai-companions/{id} endpoint."""

    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for AI service"""
        return AI_SERVICE_URL
    
    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        return DEV_VALID_TOKEN
    
    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return DEV_INVALID_TOKEN
    
    @pytest.fixture
    def expired_access_token(self) -> str:
        """Expired access token for testing token expiration"""
        return create_expired_token()
    
    @pytest.fixture
    def valid_companion_id(self) -> str:
        """Valid companion ID for testing"""
        return DEV_KNOWN_COMPANION_ID
    
    @pytest.fixture
    def nonexistent_companion_id(self) -> str:
        """Non-existent companion ID for testing 404"""
        return f"{DEV_NONEXISTENT_PREFIX}_companion_456"
    
    @pytest.fixture
    def forbidden_companion_id(self) -> str:
        """Companion ID owned by another user for testing 403"""
        return DEV_FORBIDDEN_ID
    
    @pytest.fixture
    def invalid_companion_id(self) -> str:
        """Invalid companion ID format for testing 422"""
        return "invalid_id_format"

    @pytest.mark.asyncio
    async def test_delete_companion_success_returns_200(
        self,
        base_url: str,
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test successful companion deletion returns 200"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 200 OK
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "deleted_id" in data
            # In DEV mode, id is normalized to UUID
            expected_id = uuid.uuid5(uuid.NAMESPACE_URL, f"dev:ai-companion:{valid_companion_id}")
            assert data["deleted_id"] == str(expected_id)
            assert "deleted successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_delete_companion_not_found_returns_404(
        self,
        base_url: str,
        valid_access_token: str,
        nonexistent_companion_id: str
    ):
        """Test deleting non-existent companion returns 404"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{nonexistent_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 404 Not Found
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_companion_forbidden_returns_403(
        self,
        base_url: str,
        valid_access_token: str,
        forbidden_companion_id: str
    ):
        """Test deleting companion owned by another user returns 403"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{forbidden_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 403 Forbidden
            assert response.status_code == 403
            data = response.json()
            assert "detail" in data
            assert "forbidden" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_companion_missing_auth_returns_401(
        self,
        base_url: str,
        valid_companion_id: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={"Content-Type": "application/json"}
            )

            # Should return 401 Unauthorized (or 403 Forbidden for missing header)
            assert response.status_code in [401, 403]
            data = response.json()
            assert "detail" in data
            assert "unauthorized" in data["detail"].lower() or "not authenticated" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_companion_invalid_token_returns_401(
        self,
        base_url: str,
        invalid_access_token: str,
        valid_companion_id: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {invalid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 401 Unauthorized
            assert response.status_code == 401
            data = response.json()
            assert "detail" in data
            assert "unauthorized" in data["detail"].lower() or "invalid" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_companion_expired_token_returns_401(
        self,
        base_url: str,
        expired_access_token: str,
        valid_companion_id: str
    ):
        """Test expired access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {expired_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 401 Unauthorized
            assert response.status_code == 401
            data = response.json()
            assert "detail" in data
            assert "unauthorized" in data["detail"].lower() or "expired" in data["detail"].lower() or "invalid" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_companion_invalid_id_format_returns_422(
        self,
        base_url: str,
        valid_access_token: str,
        invalid_companion_id: str
    ):
        """Test invalid companion ID format returns 422 validation error"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{invalid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

            # Should return 404 Not Found (invalid format treated as non-existent in DEV mode)
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            # Should contain error message about companion not found
            assert isinstance(data["detail"], str) or isinstance(data["detail"], list)
            if isinstance(data["detail"], str):
                assert "not found" in data["detail"].lower()
            elif isinstance(data["detail"], list):
                error_messages = [err["msg"] for err in data["detail"]]
                assert any("invalid" in msg.lower() or "format" in msg.lower() for msg in error_messages)