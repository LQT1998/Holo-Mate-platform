"""
Pydantic schemas for HologramDevice entity
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid

from shared.src.enums.device_enums import DeviceStatus, DeviceType


class DeviceBase(BaseModel):
    """Base device schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    device_type: DeviceType
    device_model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, min_length=1, max_length=100)


class DeviceCreate(DeviceBase):
    """Schema for creating a new device"""
    firmware_version: Optional[str] = None
    hardware_info: Optional[Dict[str, Any]] = None


class DeviceUpdate(BaseModel):
    """Schema for updating device information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[DeviceStatus] = None
    settings: Optional[Dict[str, Any]] = None
    firmware_version: Optional[str] = None


class DeviceResponse(DeviceBase):
    """Schema for device response"""
    id: str
    user_id: str
    status: DeviceStatus
    last_seen_at: Optional[datetime]
    firmware_version: Optional[str]
    hardware_info: Optional[Dict[str, Any]]
    settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Schema for devices list response with pagination"""
    devices: List[DeviceResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
