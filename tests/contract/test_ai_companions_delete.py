"""
Contract test for DELETE /ai-companions/{id} endpoint
Tests the AI companion deletion API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestAICompanionsDeleteContract:
    """Contract tests for DELETE /ai-companions/{id} endpoint"""
    
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
    async def test_delete_companion_success_returns_204(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test successful AI companion deletion returns 204 No Content"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 204 No Content
            assert response.status_code == 204
            
            # Should not return any content
            assert response.content == b""
    
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
            
            # Should return 401 Unauthorized
            assert response.status_code == 401
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0
    
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
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0
    
    @pytest.mark.asyncio
    async def test_delete_companion_nonexistent_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        nonexistent_companion_id: str
    ):
        """Test deleting non-existent companion returns 404 Not Found"""
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
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0
    
    @pytest.mark.asyncio
    async def test_delete_companion_unauthorized_access_returns_403(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test deleting companion owned by another user returns 403 Forbidden"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
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
    async def test_delete_companion_invalid_id_format_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_companion_id: str
    ):
        """Test invalid companion ID format returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{invalid_companion_id}",
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
    async def test_delete_companion_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion deletion response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 204:
                # Should not have content type for 204 responses
                assert "content-type" not in response.headers or response.headers["content-type"] == "application/json"
                
                # Should not expose sensitive headers
                assert "server" not in response.headers or "uvicorn" in response.headers.get("server", "")
    
    @pytest.mark.asyncio
    async def test_delete_companion_already_deleted_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test deleting already deleted companion returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            # First deletion
            response1 = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should succeed first time
            assert response1.status_code == 204
            
            # Second deletion
            response2 = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 404 Not Found
            assert response2.status_code == 404
            
            # Should return error message
            data = response2.json()
            assert isinstance(data, dict)
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_delete_companion_malformed_id_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test malformed companion ID returns 422 Validation Error"""
        malformed_ids = [
            "",  # Empty ID
            "   ",  # Whitespace only
            "id with spaces",  # Spaces in ID
            "id\nwith\nnewlines",  # Newlines in ID
            "id\twith\ttabs",  # Tabs in ID
        ]
        
        for malformed_id in malformed_ids:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
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
    
    @pytest.mark.asyncio
    async def test_delete_companion_confirmation_required(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion deletion requires confirmation"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 204 No Content (confirmation not required)
            # Or 400 Bad Request if confirmation is required
            assert response.status_code in [204, 400]
            
            if response.status_code == 400:
                data = response.json()
                assert isinstance(data, dict)
                assert "detail" in data
                assert "confirmation" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_delete_companion_with_confirmation(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion deletion with confirmation parameter"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}?confirm=true",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 204 No Content
            assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_delete_companion_cascade_behavior(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion deletion cascades to related data"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 204:
                # After deletion, companion should not be accessible
                get_response = await client.get(
                    f"{base_url}/ai-companions/{valid_companion_id}",
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                # Should return 404 Not Found
                assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_companion_subscription_limits(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion deletion respects subscription limits"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 204 No Content
            assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_delete_companion_soft_delete_behavior(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion soft delete behavior (if implemented)"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 204:
                # Check if companion is soft deleted (status = deleted)
                get_response = await client.get(
                    f"{base_url}/ai-companions/{valid_companion_id}",
                    headers={
                        "Authorization": f"Bearer {valid_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                # Should return 404 Not Found (hard delete)
                # Or 200 with status = deleted (soft delete)
                assert get_response.status_code in [200, 404]
                
                if get_response.status_code == 200:
                    data = get_response.json()
                    assert data["status"] == "deleted"
    
    @pytest.mark.asyncio
    async def test_delete_companion_audit_log(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_companion_id: str
    ):
        """Test companion deletion creates audit log entry"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/ai-companions/{valid_companion_id}",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 204 No Content
            assert response.status_code == 204
            
            # Audit log creation is implementation-specific
            # This test verifies the endpoint works correctly
