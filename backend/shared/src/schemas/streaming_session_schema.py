"""
Pydantic schemas for StreamingSession entity and status
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, UUID4
from uuid import UUID


# ---------- Enum ----------

class SessionStatus(str, Enum):
    active = "active"
    connecting = "connecting"
    error = "error"
    expired = "expired"
    ended = "ended"


# ---------- Config Sub-schemas ----------

class StreamingConfig(BaseModel):
    transport: str = Field("websocket", description="Transport protocol (e.g. websocket, webrtc)")
    buffer_size: int = Field(4096, description="Buffer size in bytes")
    voice_enabled: bool = Field(True, description="Is voice streaming enabled")
    emotion_detection: bool = Field(True, description="Is emotion detection enabled")
    response_format: str = Field("audio", description="Expected response format (e.g. audio, text)")
    quality: str = Field("high", description="Streaming quality (e.g. high, medium, low)")
    latency: str = Field("low", description="Streaming latency (e.g. low, medium, high)")


class AudioSettings(BaseModel):
    sample_rate: int = Field(44100, description="Audio sample rate in Hz")
    codec: str = Field("opus", description="Audio codec (e.g. opus, pcm16)")
    channels: int = Field(1, description="Number of audio channels")
    noise_reduction: bool = Field(True, description="Apply noise reduction")
    echo_cancellation: bool = Field(True, description="Apply echo cancellation")
    auto_gain_control: bool = Field(True, description="Apply automatic gain control")


# ---------- Core Schemas ----------

class StreamingSessionCreate(BaseModel):
    device_id: str = Field(..., description="Device identifier for the streaming session")
    settings: Optional[Dict[str, Any]] = None


class StreamingSessionRead(BaseModel):
    session_id: UUID
    device_id: UUID
    user_id: UUID
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    streaming_config: Optional[StreamingConfig] = None
    audio_settings: Optional[AudioSettings] = None

    model_config = ConfigDict(from_attributes=True)


class StreamingSessionListResponse(BaseModel):
    sessions: List[StreamingSessionRead]
    total: int
    page: int
    per_page: int
    total_pages: int


# ---------- Status Schema (used in /sessions/{id}/chat) ----------

class StreamingSessionStatusRead(BaseModel):
    # DEV mode cho phép string, nên để str thay vì UUID4
    session_id: str = Field(..., description="Streaming session identifier (DEV may be non-UUID)")
    conversation_id: UUID4
    companion_id: UUID4
    device_id: UUID4
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    websocket_url: str
    streaming_config: StreamingConfig
    audio_settings: AudioSettings
    metrics: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True)
