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
    plan_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Subscription plan identifier")
    plan_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Subscription plan name (alias for plan_id)")
    payment_method_id: Optional[str] = Field(None, min_length=1, max_length=100, description="Payment method identifier")
    payment_token: Optional[str] = Field(None, min_length=1, max_length=100, description="Payment token (alias for payment_method_id)")
    coupon_code: Optional[str] = Field(None, max_length=128, description="Optional coupon code for discount")
    
    def model_post_init(self, __context) -> None:
        """Normalize plan_name to plan_id and payment_token to payment_method_id"""
        if self.plan_name and not self.plan_id:
            self.plan_id = self.plan_name
        if self.payment_token and not self.payment_method_id:
            self.payment_method_id = self.payment_token
        
        # Ensure at least one plan identifier is provided
        if not self.plan_id and not self.plan_name:
            raise ValueError("Either plan_id or plan_name must be provided")
        if not self.payment_method_id and not self.payment_token:
            raise ValueError("Either payment_method_id or payment_token must be provided")


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
