import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship

from .base import Base, GUID
from shared.src.enums.device_enums import DeviceStatus, DeviceType


class HologramDevice(Base):
    __tablename__ = "hologram_devices"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    device_type = Column(SAEnum(DeviceType, name="device_type_enum"), nullable=False)
    status = Column(SAEnum(DeviceStatus, name="device_status_enum"), nullable=False, default=DeviceStatus.offline)
    
    last_seen_at = Column(DateTime, default=func.now(), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    device_model = Column(String)
    serial_number = Column(String, unique=True)
    firmware_version = Column(String)
    hardware_info = Column(JSON)
    settings = Column(JSON)

    # Relationships
    user = relationship("User", back_populates="devices")
    streaming_sessions = relationship("StreamingSession", back_populates="device", cascade="all, delete-orphan")
