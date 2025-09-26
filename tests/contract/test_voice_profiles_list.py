"""
Contract tests for GET /voice-profiles endpoint

Tests the voice profiles listing functionality according to API contract.
"""

import pytest
import httpx
from typing import Dict, Any


class TestVoiceProfilesListContract:
    """Contract tests for voice profiles listing endpoint"""

    @pytest.mark.asyncio
    async def test_get_voice_profiles_success_returns_200_and_list(
        self, ai_base_url: str, valid_access_token: str
    ):
        """Test successful retrieval of voice profiles returns 200 and list data."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "voice_profiles" in data
        assert isinstance(data["voice_profiles"], list)
        assert len(data["voice_profiles"]) > 0

        # Check voice profile structure
        voice_profile = data["voice_profiles"][0]
        required_fields = ["id", "name", "language", "gender", "sample_url", "created_at", "updated_at"]
        for field in required_fields:
            assert field in voice_profile

        # Validate field types and values
        assert isinstance(voice_profile["id"], str)  # UUID as string
        assert isinstance(voice_profile["name"], str)
        assert isinstance(voice_profile["language"], str)
        assert isinstance(voice_profile["gender"], str)
        assert isinstance(voice_profile["sample_url"], str)
        assert voice_profile["name"]  # Not empty
        assert voice_profile["language"]  # Not empty
        assert voice_profile["gender"]  # Not empty
        assert voice_profile["sample_url"].startswith("http")  # Valid URL

    @pytest.mark.asyncio
    async def test_get_voice_profiles_missing_auth_returns_401(
        self, ai_base_url: str
    ):
        """Test missing authorization returns 401."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={"Content-Type": "application/json"}
            )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_get_voice_profiles_invalid_token_returns_401(
        self, ai_base_url: str
    ):
        """Test invalid token returns 401."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={
                    "Authorization": "Bearer invalid_token",
                    "Content-Type": "application/json"
                }
            )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Invalid authentication credentials"

    @pytest.mark.asyncio
    async def test_get_voice_profiles_unauthorized_user_returns_401(
        self, ai_base_url: str, invalid_access_token: str
    ):
        """Test unauthorized user returns 401 (invalid token)."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={
                    "Authorization": f"Bearer {invalid_access_token}",
                    "Content-Type": "application/json"
                }
            )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid authentication credentials" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_voice_profiles_response_headers(
        self, ai_base_url: str, valid_access_token: str
    ):
        """Test response headers are correct."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_get_voice_profiles_data_structure_validation(
        self, ai_base_url: str, valid_access_token: str
    ):
        """Test voice profile data structure validation."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

        assert response.status_code == 200
        data = response.json()
        
        # Validate each voice profile in the list
        for profile in data["voice_profiles"]:
            # Check required fields exist
            assert "id" in profile
            assert "name" in profile
            assert "language" in profile
            assert "gender" in profile
            assert "sample_url" in profile
            assert "created_at" in profile
            assert "updated_at" in profile

            # Check field constraints
            assert len(profile["name"]) >= 1
            assert len(profile["name"]) <= 100
            assert len(profile["language"]) >= 2
            assert len(profile["language"]) <= 10
            assert len(profile["gender"]) >= 1
            assert len(profile["gender"]) <= 20

    @pytest.mark.asyncio
    async def test_get_voice_profiles_timestamps_format(
        self, ai_base_url: str, valid_access_token: str
    ):
        """Test timestamp format in voice profiles."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

        assert response.status_code == 200
        data = response.json()
        
        # Check timestamp format (ISO 8601)
        for profile in data["voice_profiles"]:
            created_at = profile["created_at"]
            updated_at = profile["updated_at"]
            
            # Should be ISO 8601 format
            assert "T" in created_at
            assert "T" in updated_at
            assert created_at.endswith("Z") or "+" in created_at
            assert updated_at.endswith("Z") or "+" in updated_at

    @pytest.mark.asyncio
    async def test_get_voice_profiles_caching_headers(
        self, ai_base_url: str, valid_access_token: str
    ):
        """Test caching headers for voice profiles."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

        assert response.status_code == 200
        
        # Check for caching headers (if implemented)
        cache_headers = ["cache-control", "etag", "last-modified"]
        for header in cache_headers:
            if header in response.headers:
                assert response.headers[header]  # Not empty

    @pytest.mark.asyncio
    async def test_get_voice_profiles_empty_list_returns_200(
        self, ai_base_url: str, valid_access_token: str
    ):
        """Test empty voice profiles list returns 200 with empty array."""
        # This test assumes the endpoint can return empty list
        # In DEV mode, it always returns mock data, so this tests the structure
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert "voice_profiles" in data
        assert isinstance(data["voice_profiles"], list)

    @pytest.mark.asyncio
    async def test_get_voice_profiles_language_diversity(
        self, ai_base_url: str, valid_access_token: str
    ):
        """Test voice profiles include diverse languages."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

        assert response.status_code == 200
        data = response.json()
        
        # Check for language diversity
        languages = [profile["language"] for profile in data["voice_profiles"]]
        assert len(set(languages)) > 1  # Multiple languages
        assert any("en" in lang for lang in languages)  # At least one English

    @pytest.mark.asyncio
    async def test_get_voice_profiles_gender_diversity(
        self, ai_base_url: str, valid_access_token: str
    ):
        """Test voice profiles include diverse genders."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ai_base_url}/voice-profiles",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )

        assert response.status_code == 200
        data = response.json()
        
        # Check for gender diversity
        genders = [profile["gender"] for profile in data["voice_profiles"]]
        assert len(set(genders)) > 1  # Multiple genders
        assert "female" in genders or "male" in genders  # At least one common gender

    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        return "valid_access_token_here"

    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return "invalid_access_token_here"
