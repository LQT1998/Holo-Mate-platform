"""
Contract test for PUT /devices/{id} endpoint
Tests the device update API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestDevicesUpdateContract:
    """Contract tests for PUT /devices/{id} endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for streaming service"""
        return "http://localhost:8003"
    
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
    
    @pytest.fixture
    def valid_update_data(self) -> Dict[str, Any]:
        """Valid device update request data"""
        return {
            "name": "My Updated Hologram Fan",
            "status": "online",
            "firmware_version": "1.2.4",
            "settings": {
                "brightness": 0.8,
                "volume": 0.9,
                "auto_power_off_minutes": 60
            }
        }
    
    @pytest.fixture
    def partial_update_data(self) -> Dict[str, Any]:
        """Partial device update request data"""
        return {
            "name": "New Device Name"
        }
    
    @pytest.fixture
    def invalid_update_data(self) -> Dict[str, Any]:
        """Invalid device update request data"""
        return {
            "name": "",  # Empty name
            "status": "invalid_status",  # Invalid status
            "settings": "invalid_json"  # Should be object
        }
    
    @pytest.mark.asyncio
    async def test_update_device_success_returns_200_and_updated_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test successful device update returns 200 with updated device data"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{valid_device_id}",
                json=valid_update_data,
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
            
            # Should contain updated data
            assert data["name"] == valid_update_data["name"]
            assert data["status"] == valid_update_data["status"]
            assert data["firmware_version"] == valid_update_data["firmware_version"]
            
            # Should contain updated settings data
            assert "settings" in data
            assert isinstance(data["settings"], dict)
            assert data["settings"]["brightness"] == valid_update_data["settings"]["brightness"]
            assert data["settings"]["volume"] == valid_update_data["settings"]["volume"]
            
            # Should contain timestamps
            assert "created_at" in data
            assert "updated_at" in data
            assert "last_seen_at" in data
            assert isinstance(data["created_at"], str)
            assert isinstance(data["updated_at"], str)
            assert isinstance(data["last_seen_at"], str)
    
    @pytest.mark.asyncio
    async def test_update_device_partial_success_returns_200(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str,
        partial_update_data: Dict[str, Any]
    ):
        """Test partial device update returns 200 with updated data"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{valid_device_id}",
                json=partial_update_data,
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
            
            # Should contain updated field
            assert data["name"] == partial_update_data["name"]
            
            # Other fields should remain unchanged
            assert "status" in data
            assert "settings" in data
            assert "firmware_version" in data
    
    @pytest.mark.asyncio
    async def test_update_device_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_device_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{valid_device_id}",
                json=valid_update_data,
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
    async def test_update_device_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_device_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{valid_device_id}",
                json=valid_update_data,
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
    async def test_update_device_nonexistent_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_device_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test updating non-existent device returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{nonexistent_device_id}",
                json=valid_update_data,
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
    async def test_update_device_unauthorized_access_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test updating device owned by another user returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{valid_device_id}",
                json=valid_update_data,
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
    async def test_update_device_invalid_data_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str,
        invalid_update_data: Dict[str, Any]
    ):
        """Test invalid update data returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{valid_device_id}",
                json=invalid_update_data,
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
    async def test_update_device_empty_request_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str
    ):
        """Test empty request body returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{valid_device_id}",
                json={},
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
    async def test_update_device_wrong_content_type_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test wrong content type returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{valid_device_id}",
                data=valid_update_data,  # Send as form data instead of JSON
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_device_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test device update response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{valid_device_id}",
                json=valid_update_data,
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
    async def test_update_device_immutable_fields(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str
    ):
        """Test that immutable fields cannot be updated"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{base_url}/devices/{valid_device_id}",
                json={
                    "id": "new_id",  # Should not be updatable
                    "created_at": "2023-01-01T00:00:00Z",  # Should not be updatable
                    "device_type": "new_type",  # Should not be updatable
                    "serial_number": "new_serial",  # Should not be updatable
                    "name": "UpdatedName"  # This should be updatable
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                # Immutable fields should not be changed
                assert data["id"] != "new_id"
                assert data["created_at"] != "2023-01-01T00:00:00Z"
                assert data["device_type"] != "new_type"
                assert data["serial_number"] != "new_serial"
                # Updatable field should be changed
                assert data["name"] == "UpdatedName"
    
    @pytest.mark.asyncio
    async def test_update_device_updated_at_timestamp(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str,
        valid_update_data: Dict[str, Any]
    ):
        """Test that updated_at timestamp is updated after successful update"""
        async with httpx.AsyncClient() as client:
            # First, get current device data
            get_response = await client.get(
                f"{base_url}/devices/{valid_device_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if get_response.status_code == 200:
                original_data = get_response.json()
                original_updated_at = original_data["updated_at"]
                
                # Update device
                update_response = await client.put(
                    f"{base_url}/devices/{valid_device_id}",
                    json=valid_update_data,
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if update_response.status_code == 200:
                    updated_data = update_response.json()
                    new_updated_at = updated_data["updated_at"]
                    
                    # Updated timestamp should be different
                    assert new_updated_at != original_updated_at
                    
                    # Should be more recent
                    from datetime import datetime
                    original_time = datetime.fromisoformat(original_updated_at.replace('Z', '+00:00'))
                    new_time = datetime.fromisoformat(new_updated_at.replace('Z', '+00:00'))
                    assert new_time > original_time
    
    @pytest.mark.asyncio
    async def test_update_device_validation_rules(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_device_id: str
    ):
        """Test device update validation rules"""
        test_cases = [
            # Empty name
            {"name": ""},
            # Name too long
            {"name": "x" * 256},
            # Invalid status
            {"status": "invalid_status"},
            # Invalid settings values
            {"settings": {"brightness": 2.0}},
        ]
        
        for test_data in test_cases:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{base_url}/devices/{valid_device_id}",
                    json=test_data,
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
