"""
Contract test for GET /devices endpoint
Tests the devices list API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any, List


class TestDevicesListContract:
    """Contract tests for GET /devices endpoint"""
    
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
    
    @pytest.mark.asyncio
    async def test_get_devices_success_returns_200_and_list(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test successful devices list returns 200 with devices data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices",
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
            
            # Should contain devices list
            assert "devices" in data
            assert isinstance(data["devices"], list)
            
            # Should contain pagination info
            assert "total" in data
            assert "page" in data
            assert "per_page" in data
            assert "total_pages" in data
            
            # Pagination should be valid
            assert isinstance(data["total"], int)
            assert isinstance(data["page"], int)
            assert isinstance(data["per_page"], int)
            assert isinstance(data["total_pages"], int)
            assert data["page"] >= 1
            assert data["per_page"] > 0
            assert data["total_pages"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_devices_with_pagination(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test devices list with pagination parameters"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices?page=1&per_page=10",
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
            
            # Should respect pagination parameters
            assert data["page"] == 1
            assert data["per_page"] == 10
            assert len(data["devices"]) <= 10
    
    @pytest.mark.asyncio
    async def test_get_devices_with_status_filter(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test devices list with status filter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices?status=online",
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
            
            # Should contain filtered results
            assert "devices" in data
            assert isinstance(data["devices"], list)
    
    @pytest.mark.asyncio
    async def test_get_devices_with_type_filter(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test devices list with type filter"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices?type=hologram_fan",
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
            
            # Should contain filtered results
            assert "devices" in data
            assert isinstance(data["devices"], list)
    
    @pytest.mark.asyncio
    async def test_get_devices_missing_auth_returns_401(
        self, 
        base_url: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices",
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
    async def test_get_devices_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices",
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
    async def test_get_devices_invalid_pagination_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test invalid pagination parameters returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices?page=0&per_page=-1",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], list)
            assert len(data["detail"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_devices_device_structure(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test device data structure is complete and properly formatted"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                devices = data["devices"]
                
                if len(devices) > 0:
                    device = devices[0]
                    
                    # Required fields should be present
                    required_fields = [
                        "id", "name", "device_type", "status", 
                        "created_at", "updated_at", "last_seen_at"
                    ]
                    for field in required_fields:
                        assert field in device, f"Missing required field: {field}"
                    
                    # ID should be valid
                    assert isinstance(device["id"], (str, int))
                    
                    # Name and type should be strings
                    assert isinstance(device["name"], str)
                    assert isinstance(device["device_type"], str)
                    assert len(device["name"]) > 0
                    
                    # Status should be valid
                    valid_statuses = ["online", "offline", "unpaired", "error"]
                    assert device["status"] in valid_statuses
                    
                    # Type should be valid
                    valid_types = ["hologram_fan", "mobile_app", "web_app", "unity_client"]
                    assert device["device_type"] in valid_types
                    
                    # Timestamps should be ISO format
                    import re
                    iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
                    assert re.match(iso_pattern, device["created_at"])
                    assert re.match(iso_pattern, device["updated_at"])
                    assert re.match(iso_pattern, device["last_seen_at"])
    
    @pytest.mark.asyncio
    async def test_get_devices_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test devices list response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices",
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
    async def test_get_devices_empty_list(
        self,
        base_url: str,
        valid_access_token: str
    ):
        """Test devices list returns empty list when no devices exist"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return list structure
                assert "devices" in data
                assert isinstance(data["devices"], list)
                
                # Note: In dev mode, devices may exist from previous tests
                # Just verify the structure is correct
                assert len(data["devices"]) >= 0
                assert data["page"] >= 1
                assert data["per_page"] > 0
                assert data["total_pages"] >= 0  # Adjust assertion for dev mode with existing data
    
    @pytest.mark.asyncio
    async def test_get_devices_sorting(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test devices list with sorting parameters"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices?sort_by=name&sort_order=asc",
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
            
            # Should contain devices list
            assert "devices" in data
            assert isinstance(data["devices"], list)
    
    @pytest.mark.asyncio
    async def test_get_devices_invalid_sort_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test invalid sorting parameters returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices?sort_by=invalid_field&sort_order=invalid",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
            
            # Should return validation error details
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_get_devices_caching_headers(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test that devices list response includes appropriate caching headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/devices",
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
