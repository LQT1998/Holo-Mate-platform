"""
Contract test for POST /subscriptions endpoint
Tests the subscription creation API contract before implementation
"""

import pytest
import httpx
from typing import Dict, Any


class TestSubscriptionsCreateContract:
    """Contract tests for POST /subscriptions endpoint"""
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for auth service"""
        return "http://localhost:8001"
    
    @pytest.fixture
    def valid_access_token(self) -> str:
        """Valid access token for authenticated requests"""
        return "valid_access_token_here"
    
    @pytest.fixture
    def invalid_access_token(self) -> str:
        """Invalid access token for testing unauthorized access"""
        return "invalid_access_token_here"
    
    @pytest.fixture
    def valid_subscription_data(self) -> Dict[str, Any]:
        """Valid subscription creation request data"""
        return {
            "plan_id": "pro_monthly",
            "payment_method_id": "pm_123456789",
            "coupon_code": "PROMO2023"
        }
    
    @pytest.fixture
    def minimal_subscription_data(self) -> Dict[str, Any]:
        """Minimal subscription creation request data"""
        return {
            "plan_id": "free_tier",
            "payment_method_id": "pm_987654321"
        }
    
    @pytest.fixture
    def invalid_subscription_data(self) -> Dict[str, Any]:
        """Invalid subscription creation request data"""
        return {
            "plan_id": "",  # Empty plan ID
            "payment_method_id": "",  # Empty payment method ID
            "coupon_code": "x" * 129  # Coupon code too long
        }
    
    @pytest.mark.asyncio
    async def test_create_subscription_success_returns_201_and_subscription_data(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_subscription_data: Dict[str, Any]
    ):
        """Test successful subscription creation returns 201 with subscription data"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
                json=valid_subscription_data,
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
            
            # Should contain subscription ID
            assert "id" in data
            assert isinstance(data["id"], (str, int))
            
            # Should contain plan info
            assert "plan" in data
            assert isinstance(data["plan"], dict)
            assert data["plan"]["id"] == valid_subscription_data["plan_id"]
            
            # Should contain status and dates
            assert "status" in data
            assert data["status"] == "active"
            assert "start_date" in data
            assert "next_billing_date" in data
            
            # Should contain payment info
            assert "payment_info" in data
            assert isinstance(data["payment_info"], dict)
            assert "status" in data["payment_info"]
            assert data["payment_info"]["status"] in ["succeeded", "pending", "failed"]
    
    @pytest.mark.asyncio
    async def test_create_subscription_minimal_data_success_returns_201(
        self, 
        base_url: str, 
        valid_access_token: str,
        minimal_subscription_data: Dict[str, Any]
    ):
        """Test subscription creation with minimal data returns 201"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
                json=minimal_subscription_data,
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
            
            # Should contain plan info
            assert "plan" in data
            assert data["plan"]["id"] == minimal_subscription_data["plan_id"]
    
    @pytest.mark.asyncio
    async def test_create_subscription_missing_auth_returns_401(
        self, 
        base_url: str,
        valid_subscription_data: Dict[str, Any]
    ):
        """Test missing authorization header returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
                json=valid_subscription_data,
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
    async def test_create_subscription_invalid_token_returns_401(
        self, 
        base_url: str, 
        invalid_access_token: str,
        valid_subscription_data: Dict[str, Any]
    ):
        """Test invalid access token returns 401 Unauthorized"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
                json=valid_subscription_data,
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
    async def test_create_subscription_invalid_data_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        invalid_subscription_data: Dict[str, Any]
    ):
        """Test invalid subscription data returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
                json=invalid_subscription_data,
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
    async def test_create_subscription_missing_required_fields_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test missing required fields returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
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
    async def test_create_subscription_already_exists_returns_409(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_subscription_data: Dict[str, Any]
    ):
        """Test creating subscription when user already has one returns 409 Conflict"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
                json=valid_subscription_data,
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
    async def test_create_subscription_payment_failed_returns_402(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test payment failure returns 402 Payment Required"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
                json={
                    "plan_id": "pro_monthly",
                    "payment_method_id": "pm_card_declined"
                },
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 402 Payment Required
            assert response.status_code == 402
            
            # Should return error message
            data = response.json()
            assert isinstance(data, dict)
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0
    
    @pytest.mark.asyncio
    async def test_create_subscription_invalid_plan_returns_404(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test invalid plan ID returns 404 Not Found"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
                json={
                    "plan_id": "nonexistent_plan",
                    "payment_method_id": "pm_123456789"
                },
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
    async def test_create_subscription_wrong_content_type_returns_422(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_subscription_data: Dict[str, Any]
    ):
        """Test wrong content type returns 422 Validation Error"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
                data=valid_subscription_data,  # Send as form data instead of JSON
                headers={
                    "Authorization": f"Bearer {valid_access_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_subscription_response_headers(
        self, 
        base_url: str, 
        valid_access_token: str,
        valid_subscription_data: Dict[str, Any]
    ):
        """Test subscription creation response has correct headers"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/subscriptions",
                json=valid_subscription_data,
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
                assert f"/subscriptions" in location
                
                # Should not expose sensitive headers
                assert "server" not in response.headers or "uvicorn" in response.headers.get("server", "")
    
    @pytest.mark.asyncio
    async def test_create_subscription_validation_rules(
        self, 
        base_url: str, 
        valid_access_token: str
    ):
        """Test subscription creation validation rules"""
        test_cases = [
            # Empty plan ID
            {"plan_id": "", "payment_method_id": "pm_123"},
            # Empty payment method ID
            {"plan_id": "pro_monthly", "payment_method_id": ""},
            # Coupon code too long
            {"plan_id": "pro_monthly", "payment_method_id": "pm_123", "coupon_code": "x" * 129},
        ]
        
        for test_data in test_cases:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/subscriptions",
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
