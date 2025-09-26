"""
Tests for SubscriptionService
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

from auth_service.src.services.subscription_service import SubscriptionService
from shared.src.models.subscription import Subscription
from shared.src.enums.subscription_enums import SubscriptionStatus


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock async database session."""
    session = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def subscription_service(mock_db_session):
    """Fixture to create SubscriptionService with mock database session."""
    return SubscriptionService(mock_db_session)


@pytest.fixture
def sample_subscription_data():
    """Fixture for sample subscription data."""
    return {
        "plan": "pro_monthly",
        "status": "active",
        "price": 29.99,
        "currency": "USD"
    }


class TestSubscriptionServiceCreate:
    """Test cases for subscription creation"""

    @pytest.mark.asyncio
    async def test_create_subscription_success(self, subscription_service, mock_db_session, sample_subscription_data):
        """Test successful subscription creation"""
        user_id = uuid4()
        
        # Mock no existing active subscription
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Mock subscription creation
        mock_subscription = Subscription(
            id=uuid4(),
            user_id=user_id,
            plan_name=sample_subscription_data["plan"],
            status=SubscriptionStatus.active,
            price=sample_subscription_data["price"],
            currency=sample_subscription_data["currency"]
        )
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_subscription.id)
        
        result = await subscription_service.create_subscription(
            user_id=user_id,
            plan=sample_subscription_data["plan"],
            status=sample_subscription_data["status"],
            price=sample_subscription_data["price"],
            currency=sample_subscription_data["currency"]
        )
        
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_subscription_existing_active(self, subscription_service, mock_db_session, sample_subscription_data):
        """Test subscription creation when user already has active subscription"""
        user_id = uuid4()
        
        # Mock existing active subscription
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = Subscription()
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.create_subscription(
                user_id=user_id,
                plan=sample_subscription_data["plan"]
            )
        
        assert exc_info.value.status_code == 400
        assert "already has an active subscription" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_subscription_empty_plan(self, subscription_service, mock_db_session):
        """Test subscription creation with empty plan"""
        user_id = uuid4()
        
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.create_subscription(
                user_id=user_id,
                plan=""
            )
        
        assert exc_info.value.status_code == 422
        assert "Plan name is required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_subscription_invalid_status(self, subscription_service, mock_db_session):
        """Test subscription creation with invalid status"""
        user_id = uuid4()
        
        # Mock no existing active subscription
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.create_subscription(
                user_id=user_id,
                plan="pro_monthly",
                status="invalid_status"
            )
        
        assert exc_info.value.status_code == 422
        assert "Invalid status" in exc_info.value.detail


class TestSubscriptionServiceGet:
    """Test cases for getting subscriptions"""

    @pytest.mark.asyncio
    async def test_get_subscription_by_id_success(self, subscription_service, mock_db_session):
        """Test successful subscription retrieval by ID"""
        user_id = uuid4()
        subscription_id = uuid4()
        
        mock_subscription = Subscription(
            id=subscription_id,
            user_id=user_id,
            plan_name="pro_monthly",
            status=SubscriptionStatus.active
        )
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_subscription
        mock_db_session.execute.return_value = mock_result
        
        result = await subscription_service.get_subscription_by_id(user_id, subscription_id)
        
        assert result == mock_subscription

    @pytest.mark.asyncio
    async def test_get_subscription_by_id_not_found(self, subscription_service, mock_db_session):
        """Test subscription retrieval when subscription not found"""
        user_id = uuid4()
        subscription_id = uuid4()
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.get_subscription_by_id(user_id, subscription_id)
        
        assert exc_info.value.status_code == 404
        assert "Subscription not found" in exc_info.value.detail


class TestSubscriptionServiceList:
    """Test cases for listing subscriptions"""

    @pytest.mark.asyncio
    async def test_list_subscriptions_success(self, subscription_service, mock_db_session):
        """Test successful subscription listing"""
        user_id = uuid4()
        
        mock_subscriptions = [
            Subscription(id=uuid4(), user_id=user_id, plan_name="pro_monthly", status=SubscriptionStatus.active),
            Subscription(id=uuid4(), user_id=user_id, plan_name="free", status=SubscriptionStatus.inactive)
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_subscriptions
        mock_db_session.execute.return_value = mock_result
        
        result = await subscription_service.list_subscriptions(user_id)
        
        assert len(result) == 2
        assert result == mock_subscriptions

    @pytest.mark.asyncio
    async def test_list_subscriptions_with_status_filter(self, subscription_service, mock_db_session):
        """Test subscription listing with status filter"""
        user_id = uuid4()
        
        mock_subscriptions = [
            Subscription(id=uuid4(), user_id=user_id, plan_name="pro_monthly", status=SubscriptionStatus.active)
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_subscriptions
        mock_db_session.execute.return_value = mock_result
        
        result = await subscription_service.list_subscriptions(user_id, status="active")
        
        assert len(result) == 1
        assert result == mock_subscriptions

    @pytest.mark.asyncio
    async def test_list_subscriptions_invalid_status(self, subscription_service, mock_db_session):
        """Test subscription listing with invalid status filter"""
        user_id = uuid4()
        
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.list_subscriptions(user_id, status="invalid_status")
        
        assert exc_info.value.status_code == 422
        assert "Invalid status" in exc_info.value.detail


class TestSubscriptionServiceUpdate:
    """Test cases for updating subscriptions"""

    @pytest.mark.asyncio
    async def test_update_subscription_success(self, subscription_service, mock_db_session):
        """Test successful subscription update"""
        user_id = uuid4()
        subscription_id = uuid4()
        
        # Mock update result
        mock_update_result = Mock()
        mock_update_result.rowcount = 1
        mock_db_session.execute.return_value = mock_update_result
        
        # Mock get_subscription_by_id call
        mock_subscription = Subscription(
            id=subscription_id,
            user_id=user_id,
            plan_name="pro_monthly",
            status=SubscriptionStatus.active
        )
        
        # Mock the get_subscription_by_id call
        mock_get_result = Mock()
        mock_get_result.scalars.return_value.first.return_value = mock_subscription
        mock_db_session.execute.side_effect = [mock_update_result, mock_get_result]
        
        update_data = {"status": "canceled", "plan_name": "free"}
        result = await subscription_service.update_subscription(user_id, subscription_id, update_data)
        
        assert result == mock_subscription
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_subscription_not_found(self, subscription_service, mock_db_session):
        """Test subscription update when subscription not found"""
        user_id = uuid4()
        subscription_id = uuid4()
        
        # Mock update result with no rows affected
        mock_update_result = Mock()
        mock_update_result.rowcount = 0
        mock_db_session.execute.return_value = mock_update_result
        
        update_data = {"status": "canceled"}
        
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.update_subscription(user_id, subscription_id, update_data)
        
        assert exc_info.value.status_code == 404
        assert "Subscription not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_subscription_empty_payload(self, subscription_service, mock_db_session):
        """Test subscription update with empty payload"""
        user_id = uuid4()
        subscription_id = uuid4()
        
        update_data = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.update_subscription(user_id, subscription_id, update_data)
        
        assert exc_info.value.status_code == 422
        assert "No valid fields to update" in exc_info.value.detail


class TestSubscriptionServiceCancel:
    """Test cases for canceling subscriptions"""

    @pytest.mark.asyncio
    async def test_cancel_subscription_success(self, subscription_service, mock_db_session):
        """Test successful subscription cancellation"""
        user_id = uuid4()
        subscription_id = uuid4()
        
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result
        
        result = await subscription_service.cancel_subscription(user_id, subscription_id)
        
        assert result is True
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_subscription_not_found(self, subscription_service, mock_db_session):
        """Test subscription cancellation when subscription not found"""
        user_id = uuid4()
        subscription_id = uuid4()
        
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.cancel_subscription(user_id, subscription_id)
        
        assert exc_info.value.status_code == 404
        assert "Subscription not found" in exc_info.value.detail


class TestSubscriptionServiceDelete:
    """Test cases for deleting subscriptions"""

    @pytest.mark.asyncio
    async def test_delete_subscription_success(self, subscription_service, mock_db_session):
        """Test successful subscription deletion"""
        user_id = uuid4()
        subscription_id = uuid4()
        
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result
        
        result = await subscription_service.delete_subscription(user_id, subscription_id)
        
        assert result is True
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_subscription_not_found(self, subscription_service, mock_db_session):
        """Test subscription deletion when subscription not found"""
        user_id = uuid4()
        subscription_id = uuid4()
        
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await subscription_service.delete_subscription(user_id, subscription_id)
        
        assert exc_info.value.status_code == 404
        assert "Subscription not found" in exc_info.value.detail


class TestSubscriptionServiceUtility:
    """Test cases for utility methods"""

    @pytest.mark.asyncio
    async def test_get_active_subscription_success(self, subscription_service, mock_db_session):
        """Test successful active subscription retrieval"""
        user_id = uuid4()
        
        mock_subscription = Subscription(
            id=uuid4(),
            user_id=user_id,
            plan_name="pro_monthly",
            status=SubscriptionStatus.active
        )
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_subscription
        mock_db_session.execute.return_value = mock_result
        
        result = await subscription_service.get_active_subscription(user_id)
        
        assert result == mock_subscription

    @pytest.mark.asyncio
    async def test_get_active_subscription_none(self, subscription_service, mock_db_session):
        """Test active subscription retrieval when no active subscription exists"""
        user_id = uuid4()
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await subscription_service.get_active_subscription(user_id)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_count_subscriptions_success(self, subscription_service, mock_db_session):
        """Test successful subscription counting"""
        user_id = uuid4()
        
        mock_result = Mock()
        mock_result.scalar.return_value = 3
        mock_db_session.execute.return_value = mock_result
        
        result = await subscription_service.count_subscriptions(user_id)
        
        assert result == 3

    @pytest.mark.asyncio
    async def test_cleanup_expired_subscriptions_success(self, subscription_service, mock_db_session):
        """Test successful cleanup of expired subscriptions"""
        mock_result = Mock()
        mock_result.rowcount = 2
        mock_db_session.execute.return_value = mock_result
        
        result = await subscription_service.cleanup_expired_subscriptions()
        
        assert result == 2
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_subscription_stats_success(self, subscription_service, mock_db_session):
        """Test successful subscription statistics retrieval"""
        user_id = uuid4()
        
        # Mock count queries for each status
        mock_count_results = [Mock(scalar=Mock(return_value=1)) for _ in range(5)]
        mock_db_session.execute.side_effect = mock_count_results
        
        # Mock active subscription query
        mock_active_result = Mock()
        mock_active_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.side_effect = mock_count_results + [mock_active_result]
        
        result = await subscription_service.get_subscription_stats(user_id)
        
        assert "total_subscriptions" in result
        assert "status_counts" in result
        assert "has_active_subscription" in result
        assert "active_plan" in result
        assert "active_expires_at" in result
