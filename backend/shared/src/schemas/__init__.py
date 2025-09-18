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
    VoiceProfileCreate,
    VoiceProfileUpdate,
    VoiceProfileResponse,
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
    # Device schemas
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceResponse",
    # Subscription schemas
    "SubscriptionCreate",
    "SubscriptionUpdate",
    "SubscriptionResponse",
    # Voice Profile schemas
    "VoiceProfileCreate",
    "VoiceProfileUpdate",
    "VoiceProfileResponse",
    # Token / Auth schemas
    "TokenSchema",
    "TokenData",
    "LoginRequest",
    "RegisterRequest",
    "RefreshTokenRequest",
    "GoogleLoginRequest",
    "Token",
]
