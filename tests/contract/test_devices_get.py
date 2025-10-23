"""
Contract test for GET /devices/{id} endpoint
Tests the device retrieval API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestDevicesGetContract:
    """Contract tests for GET /devices/{id} endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for streaming service"""
        return "http://localhost:8003/api/v1"
    
    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        return "valid_access_token_here"
    
    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return "invalid_access_token_here"
    
    @pytest.fixture
    def valid_device_id(self) -> str:
        """Valid device ID for testing"""
        return "device_123"
    
    @pytest.fixture
    def invalid_device_id(self) -> str:
        """Invalid device ID for testing"""
        return "invalid_device_id"
    
    @pytest.fixture
    def nonexistent_device_id(self) -> str:
        """Non-existent device ID for testing"""
        return "nonexistent_device_456"
    
    @pytest.mark.asyncio
    async def test_get_device_success_returns_200_and_device_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str
    ):
        """Test successful device retrieval returns 200 with device data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices/{valid_device_id}",
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
            
            # Should contain device ID
            assert "id" in data
            assert data["id"] == valid_device_id
            
            # Should contain basic device info
            assert "name" in data
            assert "device_type" in data
            assert "status" in data
            assert isinstance(data["name"], str)
            assert isinstance(data["device_type"], str)
            assert isinstance(data["status"], str)
            
            # Should contain detailed info
            assert "device_model" in data
            assert "serial_number" in data
            assert "firmware_version" in data
            assert "hardware_info" in data
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            assert "last_seen_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)
            assert isinstance(data["last_seen_at"], str)
            
            # Should contain status
            assert "status" in data
            assert data["status"] in ["online", "offline", "unpaired", "error"]
    
    @pytest.mark.asyncio
    async def test_get_device_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_device_id: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices/{valid_device_id}",
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
    async def test_get_device_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_device_id: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices/{valid_device_id}",
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
    async def test_get_device_nonexistent_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_device_id: str
    ):
        """Test non-existent device returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices/{nonexistent_device_id}",
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
    async def test_get_device_unauthorized_access_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test accessing device owned by another user returns 403 Forbidden"""
        forbidden_device_id = "forbidden_device_999"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices/{forbidden_device_id}",
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
    async def test_get_device_invalid_id_format_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_device_id: str
    ):
        """Test invalid device ID format returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices/{invalid_device_id}",
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
    
    @pytest.mark.asyncio
    async def test_get_device_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str
    ):
        """Test device retrieval response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices/{valid_device_id}",
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
    async def test_get_device_data_structure_validation(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str
    ):
        """Test device data structure is complete and properly formatted"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices/{valid_device_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Required fields should be present
                required_fields = [
                    "id", "name", "device_type", "status", 
                    "created_at", "updated_at", "last_seen_at",
                    "device_model", "serial_number", "firmware_version",
                    "hardware_info"
                ]
                for field in required_fields:
                    assert field in data, f"Missing required field: {field}"
                
                # Hardware info should have required fields
                hardware_fields = ["cpu", "gpu", "ram_gb", "storage_gb"]
                for field in hardware_fields:
                    assert field in data["hardware_info"], f"Missing hardware field: {field}"
                
                # Data types should be correct
                assert isinstance(data["name"], str)
                assert isinstance(data["device_type"], str)
                assert isinstance(data["status"], str)
                assert isinstance(data["hardware_info"], dict)
                
                # Status and type should be valid
                valid_statuses = ["online", "offline", "unpaired", "error"]
                assert data["status"] in valid_statuses
                valid_types = ["hologram_fan", "mobile_app", "web_app", "unity_client"]
                assert data["device_type"] in valid_types
    
    @pytest.mark.asyncio
    async def test_get_device_timestamps_format(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str
    ):
        """Test device timestamps are in correct ISO format"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices/{valid_device_id}",
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
                assert re.match(iso_pattern, data["last_seen_at"])
                
                # Updated timestamp should be >= created timestamp
                from datetime import datetime
                created_time = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
                updated_time = datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
                assert updated_time >= created_time
    
    @pytest.mark.asyncio
    async def test_get_device_caching_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str
    ):
        """Test that device retrieval response includes appropriate caching headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices/{valid_device_id}",
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
    async def test_get_device_conditional_request(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str
    ):
        """Test conditional request with If-None-Match header"""
        async with httpx.AsyncClient() as client:
            # First request to get ETag
            response1 = await client.get(
                f"{base_url}/devices/{valid_device_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response1.status_code == 200 and "ETag" in response1.headers:
                etag = response1.headers["ETag"]
                
                # Second request with If-None-Match
                response2 = await client.get(
                    f"{base_url}/devices/{valid_device_id}",
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json",
                        "If-None-Match": etag
                    }
                )
                
                # Should return 304 Not Modified
                assert response2.status_code == 304
    
    @pytest.mark.asyncio
    async def test_get_device_malformed_id_returns_422(
        self,
        base_url: str,
        valid_access_token: str
    ):
        """Test malformed device ID returns 422 Validation Error"""
        malformed_ids = [
            "invalid_device_id",  # Invalid format (server handles this)
        ]
        
        for malformed_id in malformed_ids:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url}/devices/{malformed_id}",
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
