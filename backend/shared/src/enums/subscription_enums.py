"""
Subscription-related enums
"""

from enum import Enum as PyEnum


class SubscriptionStatus(PyEnum):
    """Subscription status enum"""
    active = "active"
    inactive = "inactive"
    canceled = "canceled"
    expired = "expired"
    pending = "pending"


class SubscriptionPlan(PyEnum):
    """Subscription plan enum"""
    free = "free"
    basic_monthly = "basic_monthly"
    basic_yearly = "basic_yearly"
    pro_monthly = "pro_monthly"
    pro_yearly = "pro_yearly"
    enterprise = "enterprise"
