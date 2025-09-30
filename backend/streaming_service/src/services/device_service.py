"""
DeviceService - Business logic for managing Hologram Devices
"""

from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from shared.src.models.hologram_device import HologramDevice
from shared.src.enums.device_enums import DeviceStatus, DeviceType


class DeviceService:
    """Service for managing hologram devices"""
    
    # Allowed fields for device updates
    ALLOWED_UPDATE_FIELDS = {"name", "status", "settings", "firmware_version", "device_model"}
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register_device(
        self, 
        user_id: UUID, 
        serial: str, 
        name: Optional[str] = None,
        device_type: str = "hologram_fan",
        device_model: Optional[str] = None,
        firmware_version: Optional[str] = None,
        hardware_info: Optional[Dict[str, Any]] = None
    ) -> HologramDevice:
        """
        Register a new hologram device for a user.
        
        Args:
            user_id: ID of the user registering the device
            serial: Serial number of the device (must be unique)
            name: Optional name for the device (defaults to serial if not provided)
            device_type: Type of device (defaults to "hologram_fan")
            device_model: Optional device model
            firmware_version: Optional firmware version
            hardware_info: Optional hardware information
            
        Returns:
            The registered device
            
        Raises:
            HTTPException(400): If serial number already exists
            HTTPException(422): If required fields are missing
        """
        if not serial or not serial.strip():
            raise HTTPException(status_code=422, detail="Serial number is required")
        
        # Create new device, rely on DB constraint for duplicate serial
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        # Convert string device_type to enum
        if isinstance(device_type, str):
            device_type_enum = DeviceType(device_type)
        else:
            device_type_enum = device_type
            
        device = HologramDevice(
            user_id=user_id,
            name=name or f"Device {serial}",
            device_type=device_type_enum,
            status=DeviceStatus.unpaired,
            serial_number=serial,
            device_model=device_model,
            firmware_version=firmware_version,
            hardware_info=hardware_info,
            last_seen_at=now,
            created_at=now,
            updated_at=now,
        )
        
        try:
            self.db.add(device)
            await self.db.commit()
            await self.db.refresh(device)
            return device
        except IntegrityError as e:
            await self.db.rollback()
            if "serial_number" in str(e) or "UNIQUE constraint failed" in str(e):
                raise HTTPException(status_code=400, detail="Device with this serial number already exists")
            raise HTTPException(status_code=500, detail="Failed to register device")

    async def get_device_by_id(self, user_id: UUID, device_id: UUID) -> HologramDevice:
        """
        Get a specific device by ID, ensuring ownership.
        
        Args:
            user_id: ID of the user requesting the device
            device_id: ID of the device to retrieve
            
        Returns:
            The requested device
            
        Raises:
            HTTPException(404): If device not found or not owned by user
        """
        stmt = select(HologramDevice).where(
            HologramDevice.id == device_id,
            HologramDevice.user_id == user_id
        )
        result = await self.db.execute(stmt)
        device = result.scalars().first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return device

    async def list_devices(
        self, 
        user_id: UUID, 
        status: Optional[DeviceStatus] = None,
        page: int = 1,
        per_page: int = 20
    ) -> List[HologramDevice]:
        """
        List devices for a user with pagination and optional status filter.
        
        Args:
            user_id: ID of the user requesting devices
            status: Optional status filter
            page: Page number (1-based)
            per_page: Number of devices per page
            
        Returns:
            List of devices for the user
        """
        stmt = select(HologramDevice).where(HologramDevice.user_id == user_id)
        if status:
            stmt = stmt.where(HologramDevice.status == status)
        stmt = stmt.order_by(HologramDevice.created_at.desc())
        
        # Add pagination
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_device(
        self, 
        user_id: UUID, 
        device_id: UUID, 
        update_data: Dict[str, Any]
    ) -> HologramDevice:
        """
        Update a device's information.
        
        Args:
            user_id: ID of the user requesting the update
            device_id: ID of the device to update
            update_data: Dictionary of fields to update
            
        Returns:
            The updated device
            
        Raises:
            HTTPException(404): If device not found or not owned by user
            HTTPException(422): If no valid fields to update
        """
        # Filter allowed fields
        update_fields = {k: v for k, v in update_data.items() if k in self.ALLOWED_UPDATE_FIELDS}
        
        if not update_fields:
            raise HTTPException(
                status_code=422, 
                detail="No valid fields to update. Allowed fields: name, status, settings, firmware_version, device_model"
            )
        
        # Add updated_at timestamp
        update_fields["updated_at"] = datetime.now(timezone.utc)
        
        stmt = (
            update(HologramDevice)
            .where(HologramDevice.id == device_id, HologramDevice.user_id == user_id)
            .values(**update_fields)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Return updated device
        return await self.get_device_by_id(user_id, device_id)

    async def delete_device(self, user_id: UUID, device_id: UUID) -> bool:
        """
        Delete a device permanently.
        
        Args:
            user_id: ID of the user requesting deletion
            device_id: ID of the device to delete
            
        Returns:
            True if device was deleted
            
        Raises:
            HTTPException(404): If device not found or not owned by user
        """
        stmt = delete(HologramDevice).where(
            HologramDevice.id == device_id,
            HologramDevice.user_id == user_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return True

    async def count_devices(self, user_id: UUID, status: Optional[DeviceStatus] = None) -> int:
        """
        Count devices for a user, optionally filtered by status.
        
        Args:
            user_id: ID of the user
            status: Optional status filter
            
        Returns:
            Number of devices
        """
        stmt = select(func.count(HologramDevice.id)).where(HologramDevice.user_id == user_id)
        if status:
            stmt = stmt.where(HologramDevice.status == status)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def update_device_status(self, device_id: UUID, new_status: DeviceStatus) -> bool:
        """
        Update device status (typically called by system/heartbeat).
        
        Args:
            device_id: ID of the device
            new_status: New status to set
            
        Returns:
            True if status was updated
            
        Raises:
            HTTPException(404): If device not found
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        stmt = (
            update(HologramDevice)
            .where(HologramDevice.id == device_id)
            .values(
                status=new_status,
                last_seen_at=now,
                updated_at=now
            )
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return True

    async def get_device_by_serial(self, serial: str) -> Optional[HologramDevice]:
        """
        Get device by serial number (for system operations).
        
        Args:
            serial: Serial number of the device
            
        Returns:
            Device if found, None otherwise
        """
        stmt = select(HologramDevice).where(HologramDevice.serial_number == serial)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_devices_by_status(self, user_id: UUID, status: DeviceStatus) -> List[HologramDevice]:
        """
        Get all devices for a user with specific status.
        
        Args:
            user_id: ID of the user
            status: Status to filter by
            
        Returns:
            List of devices with the specified status
        """
        stmt = select(HologramDevice).where(
            HologramDevice.user_id == user_id,
            HologramDevice.status == status
        ).order_by(HologramDevice.last_seen_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def cleanup_offline_devices(self, hours_threshold: int = 24) -> int:
        """
        Mark devices as offline if they haven't been seen for specified hours.
        This method can be called by a background task.
        
        Args:
            hours_threshold: Number of hours after which to mark as offline
            
        Returns:
            Number of devices marked as offline
        """
        from datetime import timedelta
        
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        threshold_time = now - timedelta(hours=hours_threshold)
        stmt = (
            update(HologramDevice)
            .where(
                HologramDevice.status == DeviceStatus.online,
                HologramDevice.last_seen_at < threshold_time
            )
            .values(
                status=DeviceStatus.offline,
                updated_at=now
            )
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
