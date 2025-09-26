"""
SubscriptionService - Business logic for managing Subscriptions
"""

from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.models.subscription import Subscription
from shared.src.enums.subscription_enums import SubscriptionStatus


class SubscriptionService:
    """Service for managing user subscriptions"""
    
    # Allowed fields for subscription updates
    ALLOWED_UPDATE_FIELDS = {"status", "end_date", "plan_name", "next_billing_date", "price", "currency"}
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_subscription(
        self, 
        user_id: UUID, 
        plan: str, 
        status: str = "active",
        expires_at: Optional[datetime] = None,
        price: Optional[float] = None,
        currency: str = "USD"
    ) -> Subscription:
        """
        Create a new subscription for a user.
        
        Args:
            user_id: ID of the user
            plan: Subscription plan name (e.g., "free", "pro_monthly")
            status: Subscription status (defaults to "active")
            expires_at: Optional expiration date (defaults to 30 days from now)
            price: Optional subscription price
            currency: Currency code (defaults to "USD")
            
        Returns:
            The created subscription
            
        Raises:
            HTTPException(400): If user already has an active subscription
            HTTPException(422): If required fields are missing
        """
        if not plan or not plan.strip():
            raise HTTPException(status_code=422, detail="Plan name is required")
        
        # Check for existing active subscription
        existing_stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.active
        )
        existing_result = await self.db.execute(existing_stmt)
        if existing_result.scalars().first():
            raise HTTPException(status_code=400, detail="User already has an active subscription")
        
        # Set default expiration date if not provided
        now = datetime.now(timezone.utc)
        if expires_at is None:
            expires_at = now + timedelta(days=30)
        
        # Convert status string to enum
        try:
            status_enum = SubscriptionStatus(status)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status: {status}")
        
        # Create new subscription
        subscription = Subscription(
            user_id=user_id,
            plan_name=plan,
            status=status_enum,
            start_date=now,
            end_date=expires_at,
            next_billing_date=expires_at,
            price=price,
            currency=currency,
            created_at=now,
            updated_at=now,
        )
        
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def get_subscription_by_id(self, user_id: UUID, subscription_id: UUID) -> Subscription:
        """
        Get a specific subscription by ID, ensuring ownership.
        
        Args:
            user_id: ID of the user requesting the subscription
            subscription_id: ID of the subscription to retrieve
            
        Returns:
            The requested subscription
            
        Raises:
            HTTPException(404): If subscription not found or not owned by user
        """
        stmt = select(Subscription).where(
            Subscription.id == subscription_id,
            Subscription.user_id == user_id
        )
        result = await self.db.execute(stmt)
        subscription = result.scalars().first()
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription

    async def list_subscriptions(
        self, 
        user_id: UUID, 
        status: Optional[str] = None
    ) -> List[Subscription]:
        """
        List subscriptions for a user with optional status filter.
        
        Args:
            user_id: ID of the user requesting subscriptions
            status: Optional status filter
            
        Returns:
            List of subscriptions for the user
        """
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        if status:
            try:
                status_enum = SubscriptionStatus(status)
                stmt = stmt.where(Subscription.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid status: {status}")
        
        stmt = stmt.order_by(Subscription.created_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_subscription(
        self, 
        user_id: UUID, 
        subscription_id: UUID, 
        update_data: dict
    ) -> Subscription:
        """
        Update a subscription's information.
        
        Args:
            user_id: ID of the user requesting the update
            subscription_id: ID of the subscription to update
            update_data: Dictionary of fields to update
            
        Returns:
            The updated subscription
            
        Raises:
            HTTPException(404): If subscription not found or not owned by user
            HTTPException(422): If no valid fields to update
        """
        # Filter allowed fields
        update_fields = {k: v for k, v in update_data.items() if k in self.ALLOWED_UPDATE_FIELDS}
        
        if not update_fields:
            raise HTTPException(
                status_code=422, 
                detail=f"No valid fields to update. Allowed fields: {', '.join(self.ALLOWED_UPDATE_FIELDS)}"
            )
        
        # Convert status string to enum if provided
        if "status" in update_fields:
            try:
                update_fields["status"] = SubscriptionStatus(update_fields["status"])
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid status: {update_fields['status']}")
        
        # Add updated_at timestamp
        update_fields["updated_at"] = datetime.now(timezone.utc)
        
        stmt = (
            update(Subscription)
            .where(Subscription.id == subscription_id, Subscription.user_id == user_id)
            .values(**update_fields)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Return updated subscription
        return await self.get_subscription_by_id(user_id, subscription_id)

    async def cancel_subscription(self, user_id: UUID, subscription_id: UUID) -> bool:
        """
        Cancel a subscription by updating its status to 'canceled'.
        
        Args:
            user_id: ID of the user requesting cancellation
            subscription_id: ID of the subscription to cancel
            
        Returns:
            True if subscription was canceled
            
        Raises:
            HTTPException(404): If subscription not found or not owned by user
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(Subscription)
            .where(Subscription.id == subscription_id, Subscription.user_id == user_id)
            .values(
                status=SubscriptionStatus.canceled,
                canceled_at=now,
                updated_at=now
            )
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return True

    async def delete_subscription(self, user_id: UUID, subscription_id: UUID) -> bool:
        """
        Delete a subscription permanently (internal use only).
        
        Args:
            user_id: ID of the user requesting deletion
            subscription_id: ID of the subscription to delete
            
        Returns:
            True if subscription was deleted
            
        Raises:
            HTTPException(404): If subscription not found or not owned by user
        """
        stmt = delete(Subscription).where(
            Subscription.id == subscription_id,
            Subscription.user_id == user_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return True

    async def get_active_subscription(self, user_id: UUID) -> Optional[Subscription]:
        """
        Get the currently active subscription for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Active subscription if found, None otherwise
        """
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.active
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def count_subscriptions(self, user_id: UUID, status: Optional[str] = None) -> int:
        """
        Count subscriptions for a user, optionally filtered by status.
        
        Args:
            user_id: ID of the user
            status: Optional status filter
            
        Returns:
            Number of subscriptions
        """
        stmt = select(func.count(Subscription.id)).where(Subscription.user_id == user_id)
        if status:
            try:
                status_enum = SubscriptionStatus(status)
                stmt = stmt.where(Subscription.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid status: {status}")
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def cleanup_expired_subscriptions(self) -> int:
        """
        Mark expired subscriptions as 'expired' status.
        This method can be called by a background task.
        
        Returns:
            Number of subscriptions that were marked as expired
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(Subscription)
            .where(
                Subscription.status == SubscriptionStatus.active,
                Subscription.end_date < now
            )
            .values(
                status=SubscriptionStatus.expired,
                updated_at=now
            )
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def get_subscription_stats(self, user_id: UUID) -> dict:
        """
        Get subscription statistics for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with subscription statistics
        """
        # Count by status
        status_counts = {}
        for status in SubscriptionStatus:
            count_stmt = select(func.count(Subscription.id)).where(
                Subscription.user_id == user_id,
                Subscription.status == status
            )
            result = await self.db.execute(count_stmt)
            status_counts[status.value] = result.scalar() or 0
        
        # Get active subscription info
        active_subscription = await self.get_active_subscription(user_id)
        
        return {
            "total_subscriptions": sum(status_counts.values()),
            "status_counts": status_counts,
            "has_active_subscription": active_subscription is not None,
            "active_plan": active_subscription.plan_name if active_subscription else None,
            "active_expires_at": active_subscription.end_date if active_subscription else None,
        }
