"""
Pydantic schemas for StreamingSession entity and chat status
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from pydantic import BaseModel, Field, UUID4


# ---------- Enum ----------

class SessionStatus(str, Enum):
    active = "active"
    connecting = "connecting"
    error = "error"
    expired = "expired"
    ended = "ended"


# ---------- Sub-schemas ----------

class StreamingConfig(BaseModel):
    transport: str = Field("websocket", description="Transport protocol (e.g. websocket, webrtc)")
    buffer_size: int = Field(4096, description="Buffer size in bytes")


class AudioSettings(BaseModel):
    sample_rate: int = Field(44100, ge=8000, le=48000, description="Audio sample rate in Hz")
    codec: str = Field("opus", description="Audio codec, e.g., opus, pcm16")
    channels: int = Field(1, description="Number of audio channels")
    noise_reduction: bool = Field(True, description="Apply noise reduction")
    echo_cancellation: bool = Field(True, description="Apply echo cancellation")
    auto_gain_control: bool = Field(True, description="Apply automatic gain control")


# ---------- Core Schemas ----------

class StreamingSessionCreate(BaseModel):
    conversation_id: UUID4
    companion_id: UUID4
    device_id: UUID4
    user_id: UUID4
    streaming_config: Optional[StreamingConfig] = None
    audio_settings: Optional[AudioSettings] = None


class StreamingSessionStatusRead(BaseModel):
    # DEV mode cho phép string, prod UUID
    session_id: Union[str, UUID4] = Field(..., description="Streaming session identifier (string in DEV, UUID in PROD)")
    conversation_id: UUID4
    companion_id: UUID4
    device_id: UUID4
    user_id: UUID4
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    websocket_url: str
    streaming_config: Optional[StreamingConfig]
    audio_settings: Optional[AudioSettings]
    metrics: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None

    model_config = {"from_attributes": True}


class StreamingSessionResponse(BaseModel):
    session_id: Union[str, UUID4]
    status: SessionStatus
    message: Optional[str] = None
