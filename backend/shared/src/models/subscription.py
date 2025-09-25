import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship

from .base import Base, GUID


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_name = Column(String, nullable=False) # e.g., "free", "pro_monthly"
    status = Column(String, nullable=False, default="inactive") # "active", "inactive", "cancelled"
    
    start_date = Column(DateTime, default=func.now(), nullable=False)
    end_date = Column(DateTime)
    next_billing_date = Column(DateTime)
    
    price = Column(Numeric(10, 2))
    currency = Column(String(3))
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscription")
