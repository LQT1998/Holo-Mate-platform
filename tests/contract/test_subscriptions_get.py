"""
Contract test for GET /subscriptions endpoint
Tests the subscriptions get API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any, List


class TestSubscriptionsGetContract:
    """Contract tests for GET /subscriptions endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for auth service"""
        return "http://localhost:8001/api/v1"
    
    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        return "valid_access_token_here"
    
    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return "invalid_access_token_here"
    
    @pytest.mark.asyncio
    async def test_get_subscriptions_success_returns_200_and_subscription_data(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test successful subscriptions retrieval returns 200 with subscription data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/subscriptions",
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
            
            # Should contain subscription data
            assert "id" in data
            assert isinstance(data["id"], (str, int))
            assert "user_id" in data
            assert isinstance(data["user_id"], (str, int))
            
            # Should contain plan info
            assert "plan" in data
            assert isinstance(data["plan"], dict)
            assert "id" in data["plan"]
            assert "name" in data["plan"]
            assert "price" in data["plan"]
            assert "currency" in data["plan"]
            assert "features" in data["plan"]
            
            # Should contain status and dates
            assert "status" in data
            assert isinstance(data["status"], str)
            assert data["status"] in ["active", "inactive", "cancelled", "past_due"]
            assert "start_date" in data
            assert "end_date" in data
            assert "next_billing_date" in data
            assert isinstance(data["start_date"], str)
            assert isinstance(data["end_date"], (str, type(None)))
            assert isinstance(data["next_billing_date"], (str, type(None)))
            
            # Should contain usage info
            assert "usage" in data
            assert isinstance(data["usage"], dict)
            assert "device_count" in data["usage"]
            assert "companion_count" in data["usage"]
            assert "streaming_minutes" in data["usage"]
    
    @pytest.mark.asyncio
    async def test_get_subscriptions_missing_auth_returns_401(
        self, 
        base_url: str
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/subscriptions",
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
    async def test_get_subscriptions_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/subscriptions",
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
    async def test_get_subscriptions_no_subscription_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test user with no subscription returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/subscriptions",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json",
                    "X-Test-No-Subscription": "true"
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
    async def test_get_subscriptions_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test subscriptions response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/subscriptions",
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
    async def test_get_subscriptions_data_structure_validation(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test subscription data structure is complete and properly formatted"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/subscriptions",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Required fields should be present
                required_fields = [
                    "id", "user_id", "plan", "status", 
                    "start_date", "end_date", "next_billing_date",
                    "usage"
                ]
                for field in required_fields:
                    assert field in data, f"Missing required field: {field}"
                
                # Plan should have required fields
                plan_fields = ["id", "name", "price", "currency", "features"]
                for field in plan_fields:
                    assert field in data["plan"], f"Missing plan field: {field}"
                
                # Usage should have required fields
                usage_fields = ["device_count", "companion_count", "streaming_minutes"]
                for field in usage_fields:
                    assert field in data["usage"], f"Missing usage field: {field}"
                
                # Data types should be correct
                assert isinstance(data["plan"], dict)
                assert isinstance(data["status"], str)
                assert isinstance(data["usage"], dict)
                assert isinstance(data["plan"]["features"], list)
                
                # Timestamps should be ISO format
                import re
                iso_pattern = r"\d{4}-\d{2}-\d{2}"
                assert re.match(iso_pattern, data["start_date"])
                if data["end_date"]:
                    assert re.match(iso_pattern, data["end_date"])
                if data["next_billing_date"]:
                    assert re.match(iso_pattern, data["next_billing_date"])
    
    @pytest.mark.asyncio
    async def test_get_subscriptions_caching_headers(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test that subscriptions response includes appropriate caching headers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/subscriptions",
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                # Should include cache control headers
                if "Cache-Control" in response.headers:
                    cache_control = response.headers["Cache-Control"]
                    # Should not cache subscription data (sensitive)
                    assert "no-cache" in cache_control or "no-store" in cache_control
                
                # Should include ETag for conditional requests
                if "ETag" in response.headers:
                    etag = response.headers["ETag"]
                    assert isinstance(etag, str)
                    assert len(etag) > 0
