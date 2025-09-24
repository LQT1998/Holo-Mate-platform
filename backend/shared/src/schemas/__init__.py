"""
Shared Pydantic schemas for Holo-Mate platform
"""

# User schemas
from .user import UserBase, UserCreate, UserRead, UserUpdate
from .user_schema import (
    UserCreate as UserCreateSchema,
    UserUpdate as UserUpdateSchema,
    UserResponse,
    UserProfileUpdate,
    UserPreferencesUpdate,
    UserPreferencesResponse,
    UserPublic,
    UserProfileResponse,
)

# AI Companion schemas
from .ai_companion_schema import (
    AICompanionCreate,
    AICompanionUpdate,
    AICompanionResponse,
)

# Conversation schemas
from .conversation_schema import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
)

# Message schemas
from .message_schema import (
    MessageCreate,
    MessageResponse,
    MessageListResponse,
)

# Device schemas
from .device_schema import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
)

# Subscription schemas
from .subscription_schema import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
)

# Voice Profile schemas
from .voice_profile_schema import (
    VoiceProfileBase,
    VoiceProfileResponse,
    VoiceProfileListResponse,
    VoiceProfileCreate,
    VoiceProfileUpdate,
)

# Token / Auth schemas
from .token_schema import Token as TokenSchema, TokenData
from .auth import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    GoogleLoginRequest,
    Token,
)

from .streaming_session_schema import (
    StreamingSessionCreate,
    StreamingSessionRead,
    StreamingSessionListResponse,
)
from .streaming_chat_schema import (
    StreamingSessionStatusRead,
    StreamingSessionCreate,
    StreamingSessionResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "UserCreateSchema",
    "UserUpdateSchema",
    "UserResponse",
    "UserProfileUpdate",
    "UserPreferencesUpdate",
    "UserPreferencesResponse",
    "UserPublic",
    "UserProfileResponse",
    # AI Companion schemas
    "AICompanionCreate",
    "AICompanionUpdate",
    "AICompanionResponse",
    # Conversation schemas
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationResponse",
    # Message schemas
    "MessageCreate",
    "MessageResponse",
    "MessageListResponse",
    # Streaming Session Schemas
    "StreamingSessionCreate",
    "StreamingSessionRead",
    "StreamingSessionListResponse",
    # Streaming Chat Schemas
    "StreamingSessionStatusRead",
    "StreamingSessionCreate",
    "StreamingSessionResponse",
    # Device schemas
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceResponse",
    # Subscription schemas
    "SubscriptionCreate",
    "SubscriptionUpdate",
    "SubscriptionResponse",
    # Voice Profile schemas
    "VoiceProfileBase",
    "VoiceProfileResponse",
    "VoiceProfileListResponse",
    "VoiceProfileCreate",
    "VoiceProfileUpdate",
    # Token / Auth schemas
    "TokenSchema",
    "TokenData",
    "LoginRequest",
    "RegisterRequest",
    "RefreshTokenRequest",
    "GoogleLoginRequest",
    "Token",
]
