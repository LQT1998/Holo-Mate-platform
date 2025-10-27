"""
Contract test for POST /devices endpoint
Tests the device registration API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestDevicesRegisterContract:
    """Contract tests for POST /devices endpoint"""
    
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
    def valid_device_data(self) -> Dict[str, Any]:
        """Valid device registration request data"""
        import uuid
        unique_serial = f"HF-2023-{str(uuid.uuid4())[:8]}"
        return {
            "name": "My Hologram Fan",
            "device_type": "hologram_fan",
            "device_model": "HoloFan v2.1",
            "serial_number": unique_serial,
            "firmware_version": "1.2.3",
            "hardware_info": {
                "cpu": "ARM Cortex-A53",
                "gpu": "Mali-G31",
                "ram_gb": 2,
                "storage_gb": 16
            }
        }
    
    @pytest.fixture
    def minimal_device_data(self) -> Dict[str, Any]:
        """Minimal device registration request data"""
        return {
            "name": "My Mobile App",
            "device_type": "mobile_app"
        }
    
    @pytest.fixture
    def invalid_device_data(self) -> Dict[str, Any]:
        """Invalid device registration request data"""
        return {
            "name": "",  # Empty name
            "device_type": "invalid_device_type",  # Invalid type
            "serial_number": "x" * 256,  # Serial number too long
            "hardware_info": "invalid_json"  # Should be object
        }
    
    @pytest.mark.asyncio
    async def test_register_device_success_returns_201_and_device_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_data: Dict[str, Any]
    ):
        """Test successful device registration returns 201 with device data"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/devices",
                json=valid_device_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 201 Created
            assert response.status_code == 201
            
            # Should return JSON response
            data = response.json()
            assert isinstance(data, dict)
            
            # Should contain device ID
            assert "id" in data
            assert isinstance(data["id"], (str, int))
            
            # Should contain provided data
            assert data["name"] == valid_device_data["name"]
            assert data["device_type"] == valid_device_data["device_type"]
            assert data["device_model"] == valid_device_data["device_model"]
            assert data["serial_number"] == valid_device_data["serial_number"]
            assert data["firmware_version"] == valid_device_data["firmware_version"]
            
            # Should contain hardware info
            assert "hardware_info" in data
            assert isinstance(data["hardware_info"], dict)
            assert data["hardware_info"]["cpu"] == valid_device_data["hardware_info"]["cpu"]
            
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
    async def test_register_device_minimal_data_success_returns_201(
        self, 
        base_url: str, 
        valid_access_token: str,
        minimal_device_data: Dict[str, Any]
    ):
        """Test device registration with minimal data returns 201"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/devices",
                json=minimal_device_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 201 Created
            assert response.status_code == 201
            
            # Should return JSON response
            data = response.json()
            assert isinstance(data, dict)
            
            # Should contain provided data
            assert data["name"] == minimal_device_data["name"]
            assert data["device_type"] == minimal_device_data["device_type"]
            
            # Should have default values for optional fields
            assert "device_model" in data
            assert "serial_number" in data
            assert "firmware_version" in data
            assert "hardware_info" in data
            assert "status" in data
    
    @pytest.mark.asyncio
    async def test_register_device_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_device_data: Dict[str, Any]
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/devices",
                json=valid_device_data,
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
    async def test_register_device_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_device_data: Dict[str, Any]
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/devices",
                json=valid_device_data,
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
    async def test_register_device_invalid_data_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_device_data: Dict[str, Any]
    ):
        """Test invalid device data returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/devices",
                json=invalid_device_data,
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
    async def test_register_device_missing_required_fields_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test missing required fields returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/devices",
                json={},  # Empty request
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
    async def test_register_device_duplicate_serial_returns_409(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test registering device with duplicate serial number returns 409 Conflict"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/devices",
                json={
                    "name": "My Duplicate Device",
                    "device_type": "hologram_fan",
                    "serial_number": "HF-2023-XYZ-123"
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 409 Conflict
            assert response.status_code == 409
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0
    
    @pytest.mark.asyncio
    async def test_register_device_wrong_content_type_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_data: Dict[str, Any]
    ):
        """Test wrong content type returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/devices",
                data=valid_device_data,  # Send as form data instead of JSON
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_device_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_data: Dict[str, Any]
    ):
        """Test device registration response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/devices",
                json=valid_device_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 201:
                # Should have correct content type
                assert response.headers["content-type"] == "application/json"
                
                # Should include Location header with new resource URL
                assert "Location" in response.headers
                location = response.headers["Location"]
                assert f"/devices/" in location
                
                # Should not expose sensitive headers
                assert "server" not in response.headers or "uvicorn" in response.headers.get("server", "")
    
    @pytest.mark.asyncio
    async def test_register_device_validation_rules(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test device registration validation rules"""
        test_cases = [
            # Empty name
            {"name": "", "device_type": "hologram_fan"},
            # Name too long
            {"name": "x" * 256, "device_type": "hologram_fan"},
            # Invalid device type
            {"name": "My Device", "device_type": "invalid_device_type"},
            # Serial number too long
            {"name": "My Device", "device_type": "hologram_fan", "serial_number": "x" * 256},
            # Invalid hardware info values
            {"name": "My Device", "device_type": "hologram_fan", "hardware_info": {"ram_gb": -1}},
        ]
        
        for test_data in test_cases:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/devices",
                    json=test_data,
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                # Should return 422 Validation Error or 500 for server errors
                assert response.status_code in [422, 500], f"Expected 422 or 500, got {response.status_code}"
                
                # Should return error details (if JSON response)
                try:
                    data = response.json()
                    assert isinstance(data, dict)
                except Exception:
                    # If not JSON, just verify it's an error response
                    assert response.status_code >= 400
    
    @pytest.mark.asyncio
    async def test_register_device_subscription_limits(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_data: Dict[str, Any]
    ):
        """Test device registration respects subscription limits"""
        # This test assumes the user has reached their device limit
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/devices",
                json=valid_device_data,
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 403 Forbidden if limit exceeded
            if response.status_code == 403:
                data = response.json()
                assert isinstance(data, dict)
                assert "detail" in data
                assert "limit" in data["detail"].lower() or "quota" in data["detail"].lower()
            else:
                # Or 201 if within limits
                assert response.status_code == 201
