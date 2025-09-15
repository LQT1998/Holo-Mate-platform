import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base, GUID


class HologramDevice(Base):
    __tablename__ = "hologram_devices"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False) # "hologram_fan", "mobile_app", etc.
    status = Column(String, nullable=False, default="offline") # "online", "offline", "unpaired"
    
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
