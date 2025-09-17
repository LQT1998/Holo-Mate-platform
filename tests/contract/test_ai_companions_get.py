"""
Contract test for GET /ai-companions/{id} endpoint
Tests the AI companion retrieval API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any
import uuid


class TestAICompanionsGetContract:
    """Contract tests for GET /ai-companions/{id} endpoint"""
    
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
    def valid_companion_id(self) -> str:
        """Valid companion ID for testing"""
        return "companion_123"
    
    @pytest.fixture
    def invalid_companion_id(self) -> str:
        """Invalid companion ID for testing"""
        return "invalid_companion_id"
    
    @pytest.fixture
    def nonexistent_companion_id(self) -> str:
        """Non-existent companion ID for testing"""
        return "nonexistent_companion_456"
    
    @pytest.mark.asyncio
    async def test_get_companion_success_returns_200_and_companion_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test successful AI companion retrieval returns 200 with companion data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
            
            # Should contain companion ID (normalized to UUID in DEV mode)
            assert "id" in data
            expected_id = uuid.uuid5(uuid.NAMESPACE_URL, f"dev:ai-companion:{valid_companion_id}")
            assert data["id"] == str(expected_id)
            
            # Should contain basic companion info
            assert "name" in data
            assert "description" in data
            assert isinstance(data["name"], str)
            assert isinstance(data["description"], str)
            assert len(data["name"]) > 0
            
            # Should contain personality data
            assert "personality" in data
            assert isinstance(data["personality"], dict)
            assert "traits" in data["personality"]
            assert "communication_style" in data["personality"]
            assert "humor_level" in data["personality"]
            assert "empathy_level" in data["personality"]
            
            # Should contain voice profile data
            assert "voice_profile" in data
            assert isinstance(data["voice_profile"], dict)
            assert "voice_id" in data["voice_profile"]
            assert "speed" in data["voice_profile"]
            assert "pitch" in data["voice_profile"]
            assert "volume" in data["voice_profile"]
            
            # Should contain character asset data
            assert "character_asset" in data
            assert isinstance(data["character_asset"], dict)
            assert "model_id" in data["character_asset"]
            assert "animations" in data["character_asset"]
            assert "emotions" in data["character_asset"]
            
            # Should contain preferences data
            assert "preferences" in data
            assert isinstance(data["preferences"], dict)
            assert "conversation_topics" in data["preferences"]
            assert "response_length" in data["preferences"]
            assert "formality_level" in data["preferences"]
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)
            
            # Should contain status
            assert "status" in data
            assert data["status"] in ["active", "inactive", "training", "error"]
    
    @pytest.mark.asyncio
    async def test_get_companion_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_companion_id: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_get_companion_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_companion_id: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_get_companion_nonexistent_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_companion_id: str
    ):
        """Test non-existent companion returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/ai-companions/{nonexistent_companion_id}",
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
    async def test_get_companion_invalid_id_format_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_companion_id: str
    ):
        """Test invalid companion ID format returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/ai-companions/{invalid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 404 Not Found (invalid format treated as non-existent in DEV mode)
            assert response.status_code == 404
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_get_companion_unauthorized_access_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test accessing companion owned by another user returns 403 Forbidden"""
        # Use forbidden_999 which should return 403
        forbidden_companion_id = "forbidden_999"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/ai-companions/{forbidden_companion_id}",
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
    async def test_get_companion_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion retrieval response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_get_companion_data_structure_validation(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion data structure is complete and properly formatted"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Required fields should be present
                required_fields = [
                    "id", "name", "description", "personality", 
                    "voice_profile", "character_asset", "preferences",
                    "status", "created_at", "updated_at"
                ]
                for field in required_fields:
                    assert field in data, f"Missing required field: {field}"
                
                # Personality should have required fields
                personality_fields = ["traits", "communication_style", "humor_level", "empathy_level"]
                for field in personality_fields:
                    assert field in data["personality"], f"Missing personality field: {field}"
                
                # Voice profile should have required fields
                voice_fields = ["voice_id", "speed", "pitch", "volume"]
                for field in voice_fields:
                    assert field in data["voice_profile"], f"Missing voice field: {field}"
                
                # Character asset should have required fields
                asset_fields = ["model_id", "animations", "emotions"]
                for field in asset_fields:
                    assert field in data["character_asset"], f"Missing asset field: {field}"
                
                # Preferences should have required fields
                pref_fields = ["conversation_topics", "response_length", "formality_level"]
                for field in pref_fields:
                    assert field in data["preferences"], f"Missing preference field: {field}"
                
                # Data types should be correct
                assert isinstance(data["name"], str)
                assert isinstance(data["description"], str)
                assert isinstance(data["personality"], dict)
                assert isinstance(data["voice_profile"], dict)
                assert isinstance(data["character_asset"], dict)
                assert isinstance(data["preferences"], dict)
                assert isinstance(data["status"], str)
    
    @pytest.mark.asyncio
    async def test_get_companion_timestamps_format(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion timestamps are in correct ISO format"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Timestamps should be ISO format
                import re
                iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
                assert re.match(iso_pattern, data["created_at"])
                assert re.match(iso_pattern, data["updated_at"])
                
                # Updated timestamp should be >= created timestamp
                from datetime import datetime
                created_time = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
                updated_time = datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
                assert updated_time >= created_time
    
    @pytest.mark.asyncio
    async def test_get_companion_caching_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test that companion retrieval response includes appropriate caching headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_get_companion_conditional_request(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test conditional request with If-None-Match header"""
        async with httpx.AsyncClient() as client:
            # First request to get ETag
            response1 = await client.get(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response1.status_code == 200 and "ETag" in response1.headers:
                etag = response1.headers["ETag"]
                
                # Second request with If-None-Match
                response2 = await client.get(
                    f"{base_url}/ai-companions/{valid_companion_id}",
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json",
                        "If-None-Match": etag
                    }
                )
                
                # Should return 304 Not Modified
                assert response2.status_code == 304
    
    @pytest.mark.asyncio
    async def test_get_companion_malformed_id_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test malformed companion ID returns 422 Validation Error"""
        malformed_ids = [
            "",  # Empty ID
            "   ",  # Whitespace only
            "id with spaces",  # Spaces in ID
            # Note: Removed newlines and tabs as they cause httpx.InvalidURL
        ]
        
        for malformed_id in malformed_ids:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url}/ai-companions/{malformed_id}",
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                # Should return 422 Validation Error
                assert response.status_code == 422
                
                # Should return validation error details
                data = response.json()
                assert isinstance(data, dict)
                assert "detail" in data
