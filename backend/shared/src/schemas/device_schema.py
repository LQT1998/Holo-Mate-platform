"""
Pydantic schemas for HologramDevice entity
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class DeviceBase(BaseModel):
    """Base device schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    device_type: str = Field(..., pattern="^(hologram|projector|display)$")
    device_model: Optional[str] = Field(None, max_length=100)
    serial_number: str = Field(..., min_length=1, max_length=100)


class DeviceCreate(DeviceBase):
    """Schema for creating a new device"""
    pass


class DeviceUpdate(BaseModel):
    """Schema for updating device information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, pattern="^(online|offline|maintenance)$")
    settings: Optional[Dict[str, Any]] = None


class DeviceResponse(DeviceBase):
    """Schema for device response"""
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    last_seen_at: Optional[datetime]
    firmware_version: Optional[str]
    hardware_info: Optional[Dict[str, Any]]
    settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
