"""
Pydantic schemas for Subscription entity
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
import uuid


class SubscriptionCreate(BaseModel):
    """Schema for creating a new subscription"""
    plan_name: str = Field(..., min_length=1, max_length=50)
    price: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=3)


class SubscriptionUpdate(BaseModel):
    """Schema for updating subscription information"""
    status: Optional[str] = Field(None, pattern="^(active|inactive|cancelled)$")


class SubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    id: uuid.UUID
    user_id: uuid.UUID
    plan_name: str
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    next_billing_date: Optional[datetime]
    price: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
