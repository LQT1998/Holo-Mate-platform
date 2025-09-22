"""
Pydantic schemas for Subscription entity
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
import uuid


class PaymentInfo(BaseModel):
    """Nested schema for payment information"""
    method_id: str
    coupon_code: Optional[str]
    status: str


class SubscriptionCreate(BaseModel):
    """Schema for creating a new subscription"""
    plan_id: str = Field(..., min_length=1, max_length=50, description="Subscription plan identifier")
    payment_method_id: str = Field(..., min_length=1, max_length=100, description="Payment method identifier")
    coupon_code: Optional[str] = Field(None, max_length=128, description="Optional coupon code for discount")


class SubscriptionUpdate(BaseModel):
    """Schema for updating subscription information"""
    status: Optional[str] = Field(None, pattern="^(active|inactive|cancelled)$")


class SubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    id: uuid.UUID
    user_id: uuid.UUID
    plan: dict  # Will accept dict automatically
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    next_billing_date: Optional[datetime]
    usage: dict  # Will accept dict automatically
    payment_info: PaymentInfo
    payment_method_id: str
    coupon_code: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
