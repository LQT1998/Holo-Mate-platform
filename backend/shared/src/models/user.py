import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, GUID


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    ai_companions = relationship("AICompanion", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    devices = relationship("HologramDevice", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
