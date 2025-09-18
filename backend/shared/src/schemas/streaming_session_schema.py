"""
Pydantic schemas for StreamingSession entity
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
import uuid


class StreamingSessionCreate(BaseModel):
    device_id: str = Field(..., description="Device identifier for the streaming session")
    settings: Optional[Dict[str, Any]] = None


class StreamingSessionRead(BaseModel):
    id: uuid.UUID
    device_id: str
    user_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    settings: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class StreamingSessionListResponse(BaseModel):
    sessions: List[StreamingSessionRead]
    total: int
    page: int
    per_page: int
    total_pages: int
