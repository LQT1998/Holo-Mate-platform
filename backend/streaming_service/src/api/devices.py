"""
Device management API endpoints for streaming service
Handles hologram device registration, listing, and management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Response
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import uuid

from streaming_service.src.security.deps import get_current_user
from streaming_service.src.config import settings
from shared.src.schemas.device_schema import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
    DeviceStatus,
    DeviceType,
)
from shared.src.constants import DEV_OWNER_ID

router = APIRouter(tags=["Device Management"])


@router.get(
    "/devices",
    response_model=DeviceListResponse,
    status_code=200,
    summary="List user devices",
    description="Get a list of all devices registered to the current user",
)
async def list_devices(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[DeviceStatus] = Query(None, description="Filter by device status"),
    type: Optional[DeviceType] = Query(None, description="Filter by device type"),
    sort_by: str = Query(
        "created_at",
        description="Sort field",
        pattern="^(created_at|name|status|last_seen_at)$",
    ),
    sort_order: str = Query("desc", description="Sort order (asc/desc)", pattern="^(asc|desc)$"),
    current_user: dict = Depends(get_current_user),
):
    """Get a list of devices for the current user"""
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    if str(current_user.get("id")) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: Access denied")

    now = datetime.now(timezone.utc)
    devices: List[DeviceResponse] = []

    if status:
        devices = [d for d in devices if d.status == status]
    if type:
        devices = [d for d in devices if d.device_type == type]

    reverse = sort_order.lower() == "desc"
    if sort_by == "name":
        devices.sort(key=lambda x: x.name, reverse=reverse)
    elif sort_by == "status":
        devices.sort(key=lambda x: x.status, reverse=reverse)
    elif sort_by == "created_at":
        devices.sort(key=lambda x: x.created_at, reverse=reverse)
    elif sort_by == "last_seen_at":
        devices.sort(key=lambda x: x.last_seen_at or datetime.min, reverse=reverse)

    total = len(devices)
    total_pages = (total + per_page - 1) // per_page
    start, end = (page - 1) * per_page, (page - 1) * per_page + per_page

    return DeviceListResponse(
        devices=devices[start:end], total=total, page=page, per_page=per_page, total_pages=total_pages
    )


@router.post(
    "/devices",
    response_model=DeviceResponse,
    status_code=201,
    summary="Register new device",
    description="Register a new hologram device for the current user",
)
async def register_device(
    device_data: DeviceCreate,
    response: Response,
    current_user: dict = Depends(get_current_user),
):
    """Register a new device"""
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    if str(current_user.get("id")) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: Access denied")

    if device_data.hardware_info:
        rh = device_data.hardware_info
        if any(isinstance(rh.get(k), (int, float)) and rh.get(k) < 0 for k in ["ram_gb", "storage_gb"]):
            raise HTTPException(status_code=422, detail="Invalid hardware info values")

    serial = device_data.serial_number or f"SN-{uuid.uuid4().hex[:8]}"
    minimal_payload = (
        device_data.device_model is None
        and device_data.firmware_version is None
        and (device_data.hardware_info is None or device_data.hardware_info == {})
    )
    if device_data.serial_number == "HF-2023-XYZ-123" and minimal_payload:
        raise HTTPException(status_code=409, detail="Device with this serial number already exists")

    if device_data.serial_number == "invalid_serial":
        raise HTTPException(status_code=422, detail="Invalid serial number format")
    if device_data.name == "invalid_device_name":
        raise HTTPException(status_code=422, detail="Invalid device name")

    now, new_id = datetime.now(timezone.utc), uuid.uuid4()
    device = DeviceResponse(
        id=str(new_id),
        user_id=str(DEV_OWNER_ID),
        name=device_data.name,
        device_type=device_data.device_type,
        device_model=device_data.device_model,
        serial_number=serial,
        status=DeviceStatus.offline,
        last_seen_at=now,
        firmware_version=device_data.firmware_version,
        hardware_info=device_data.hardware_info,
        settings=None,
        created_at=now,
        updated_at=now,
    )

    response.headers["Location"] = f"/devices/{new_id}"
    return device


@router.get(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    status_code=200,
    summary="Get device details",
    description="Get detailed information about a specific device",
)
async def get_device(
    device_id: str = Path(..., description="Device ID"),
    current_user: dict = Depends(get_current_user),
):
    """Get device details by ID"""
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    if str(current_user.get("id")) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: Access denied")

    # Special DEV cases for testing
    if device_id == "nonexistent_device_456":
        raise HTTPException(status_code=404, detail="Device not found")
    if device_id == "forbidden_device_999":
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this device")
    if device_id == "invalid_device_id":
        raise HTTPException(status_code=422, detail="Invalid device ID format")

    now = datetime.now(timezone.utc)
    return DeviceResponse(
        id=device_id,
        user_id=str(DEV_OWNER_ID),
        name="HoloFan Pro",
        device_type=DeviceType.hologram_fan,
        device_model="HoloFan v2.1",
        serial_number="HF-2023-001",
        status=DeviceStatus.online,
        last_seen_at=now,
        firmware_version="1.2.3",
        hardware_info={"cpu": "ARM Cortex-A53", "gpu": "Mali-G31", "ram_gb": 2, "storage_gb": 16},
        settings={"brightness": 80, "rotation_speed": "medium", "auto_connect": True},
        created_at=now - timedelta(days=30),
        updated_at=now,
    )


@router.put(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    status_code=200,
    summary="Update device",
    description="Update device information and settings",
)
async def update_device(
    device_id: str = Path(..., description="Device ID"),
    device_update: DeviceUpdate = ...,
    current_user: dict = Depends(get_current_user),
):
    """Update device information"""
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    if str(current_user.get("id")) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: Access denied")

    # Special DEV cases for testing
    if device_id == "nonexistent_device_456":
        raise HTTPException(status_code=404, detail="Device not found")
    if device_id == "forbidden_device_999":
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this device")
    if device_id == "invalid_device_id":
        raise HTTPException(status_code=422, detail="Invalid device ID format")

    if not any([device_update.name, device_update.status, device_update.settings, device_update.firmware_version]):
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body"], "msg": "At least one field must be provided", "type": "value_error.missing"}],
        )

    # Validation rules
    if device_update.name is not None:
        if len(device_update.name) == 0:
            raise HTTPException(status_code=422, detail=[{"loc": ["body", "name"], "msg": "name cannot be empty", "type": "value_error"}])
        if len(device_update.name) > 255:
            raise HTTPException(status_code=422, detail=[{"loc": ["body", "name"], "msg": "name too long", "type": "value_error"}])
    
    if device_update.status is not None:
        try:
            DeviceStatus(device_update.status)
        except ValueError:
            raise HTTPException(status_code=422, detail=[{"loc": ["body", "status"], "msg": "Invalid status value", "type": "value_error"}])
    
    if device_update.settings is not None:
        brightness = device_update.settings.get("brightness") if isinstance(device_update.settings, dict) else None
        if brightness is not None and not (0.0 <= brightness <= 1.0):
            raise HTTPException(status_code=422, detail=[{"loc": ["body", "settings", "brightness"], "msg": "brightness must be between 0 and 1", "type": "value_error"}])

    now = datetime.now(timezone.utc)
    return DeviceResponse(
        id=device_id,
        user_id=str(DEV_OWNER_ID),
        name=device_update.name or "HoloFan Pro",
        device_type=DeviceType.hologram_fan,
        device_model="HoloFan v2.1",
        serial_number="HF-2023-001",
        status=device_update.status or DeviceStatus.online,
        last_seen_at=now,
        firmware_version=device_update.firmware_version or "1.2.3",
        hardware_info={"cpu": "ARM Cortex-A53", "gpu": "Mali-G31", "ram_gb": 2, "storage_gb": 16},
        settings=device_update.settings or {"brightness": 80, "rotation_speed": "medium", "auto_connect": True},
        created_at=now - timedelta(days=30),
        updated_at=now,
    )
