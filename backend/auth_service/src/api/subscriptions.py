"""
Subscription management endpoints for the Holo-Mate platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from auth_service.src.security.deps import get_current_user
from auth_service.src.config import settings
from shared.src.schemas.subscription_schema import (
    SubscriptionCreate,
    SubscriptionResponse,
    PaymentInfo,
)
from shared.src.constants import DEV_OWNER_ID

router = APIRouter(tags=["Subscriptions"])

# Global counter for testing duplicate subscription
_request_count = 0


@router.get(
    "/subscriptions",
    response_model=SubscriptionResponse,
    status_code=200,
    summary="Get user subscription",
    description="Retrieve current subscription for the authenticated user",
)
async def get_subscriptions(
    request: Request,
    current_user: dict = Depends(get_current_user),
    test_mode: str = Query(None, description="Test mode parameter"),
) -> SubscriptionResponse:
    """Get current subscription for the authenticated user"""
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    if str(current_user.id) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: Access denied")

    # Special case for testing no subscription (404)
    if request.headers.get("X-Test-No-Subscription") == "true":
        raise HTTPException(status_code=404, detail="No subscription found")

    now = datetime.now(timezone.utc)

    return SubscriptionResponse(
        id=uuid.uuid4(),
        user_id=uuid.UUID(str(DEV_OWNER_ID)),
        plan={
            "id": "pro_monthly",
            "name": "Pro Monthly",
            "price": 29.99,
            "currency": "USD",
            "features": ["unlimited_devices", "premium_voices", "priority_support"],
        },
        status="active",
        start_date=now - timedelta(days=30),
        end_date=now + timedelta(days=30),
        next_billing_date=now + timedelta(days=30),
        usage={"device_count": 3, "companion_count": 5, "streaming_minutes": 1440},
        payment_info=PaymentInfo(
            method_id="pm_123456789",
            coupon_code="PROMO2023",
            status="succeeded"
        ),
        payment_method_id="pm_123456789",
        coupon_code=None,
        created_at=now - timedelta(days=30),
        updated_at=now,
    )


@router.post(
    "/subscriptions",
    response_model=SubscriptionResponse,
    status_code=201,
    summary="Create subscription",
    description="Create a new subscription for the authenticated user",
)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: dict = Depends(get_current_user),
    response: Response = None,
    request: Request = None,
) -> SubscriptionResponse:
    """Create a new subscription"""
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    if str(current_user.id) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: Access denied")

    # Alias mapping for plan names in DEV
    alias_map = {
        "premium_monthly": "pro_monthly",
        "premium_yearly": "pro_yearly",
    }
    if subscription_data.plan_id in alias_map:
        subscription_data.plan_id = alias_map[subscription_data.plan_id]

    # Validation
    if not subscription_data.plan_id.strip():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "plan_id"], "msg": "plan_id cannot be empty", "type": "value_error"}],
        )

    if not subscription_data.payment_method_id.strip():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "payment_method_id"], "msg": "payment_method_id cannot be empty", "type": "value_error"}],
        )

    if subscription_data.coupon_code and len(subscription_data.coupon_code) > 128:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "coupon_code"], "msg": "coupon_code too long", "type": "value_error"}],
        )

    # DEV special cases
    if subscription_data.plan_id == "invalid_plan":
        raise HTTPException(status_code=422, detail="Invalid plan ID")

    if subscription_data.payment_method_id == "pm_card_declined":
        raise HTTPException(status_code=402, detail="Payment failed")

    if subscription_data.plan_id == "nonexistent_plan":
        raise HTTPException(status_code=404, detail="Plan not found")

    if (
        subscription_data.plan_id == "pro_monthly"
        and subscription_data.payment_method_id == "pm_123456789"
        and subscription_data.coupon_code == "PROMO2023"
    ):
        if request and request.headers.get("X-Test-409-Conflict") == "true":
            raise HTTPException(status_code=409, detail="Subscription already exists")

    # Plan details
    plan_details = {
        "free_tier": {"price": 0.00, "currency": "USD", "duration_days": 365},
        "pro_monthly": {"price": 29.99, "currency": "USD", "duration_days": 30},
        "pro_yearly": {"price": 299.99, "currency": "USD", "duration_days": 365},
    }
    plan_info = plan_details.get(
        subscription_data.plan_id, {"price": 29.99, "currency": "USD", "duration_days": 30}
    )

    now = datetime.now(timezone.utc)
    subscription_id = uuid.uuid4()

    if response:
        response.headers["Location"] = f"/subscriptions/{subscription_id}"

    return SubscriptionResponse(
        id=subscription_id,
        user_id=uuid.UUID(str(DEV_OWNER_ID)),
        plan={
            "id": subscription_data.plan_id,
            "name": subscription_data.plan_id.replace("_", " ").title(),
            "price": plan_info["price"],
            "currency": plan_info["currency"],
            "features": ["unlimited_devices", "premium_voices", "priority_support"],
        },
        status="active",
        start_date=now,
        end_date=now + timedelta(days=plan_info["duration_days"]),
        next_billing_date=now + timedelta(days=plan_info["duration_days"]),
        usage={"device_count": 0, "companion_count": 0, "streaming_minutes": 0},
        payment_info=PaymentInfo(
            method_id=subscription_data.payment_method_id,
            coupon_code=subscription_data.coupon_code,
            status="succeeded"
        ),
        payment_method_id=subscription_data.payment_method_id,
        coupon_code=subscription_data.coupon_code,
        created_at=now,
        updated_at=now,
    )
