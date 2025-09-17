"""
Constants and mock data for contract tests
Centralized mock data to ensure consistency across all test files
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta


# === User Constants ===
DEV_OWNER_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")
DEV_OWNER_EMAIL = "test@example.com"
DEV_VALID_TOKEN = "valid_access_token_here"
DEV_INVALID_TOKEN = "invalid_access_token_here"

# === AI Companion Constants ===
DEV_KNOWN_COMPANION_ID = "companion_123"
DEV_FORBIDDEN_ID = "forbidden_999"
DEV_NONEXISTENT_PREFIX = "nonexistent"

# === Mock Data ===

# Mock Personality
MOCK_PERSONALITY = {
    "traits": ["friendly", "helpful", "curious"],
    "communication_style": "casual",
    "humor_level": 0.7,
    "empathy_level": 0.9,
}

# Mock Voice Profile
MOCK_VOICE_PROFILE = {
    "voice_id": "test_voice_1",
    "speed": 1.0,
    "pitch": 1.0,
    "volume": 0.8,
}

# Mock Character Asset
MOCK_CHARACTER_ASSET = {
    "model_id": "avatar_v1",
    "animations": ["idle", "talking", "listening"],
    "emotions": ["happy", "sad", "excited", "calm"],
}

# Mock Preferences
MOCK_PREFERENCES = {
    "conversation_topics": ["technology", "health", "travel"],
    "response_length": "medium",
    "formality_level": "neutral",
}

# Mock AI Companion (for GET responses)
MOCK_AI_COMPANION = {
    "id": DEV_KNOWN_COMPANION_ID,
    "user_id": str(DEV_OWNER_ID),
    "name": "Test Assistant",
    "description": "A helpful AI assistant for testing",
    "personality": MOCK_PERSONALITY,
    "voice_profile": MOCK_VOICE_PROFILE,
    "character_asset": MOCK_CHARACTER_ASSET,
    "preferences": MOCK_PREFERENCES,
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": datetime.now(timezone.utc).isoformat(),
}

# Mock User Data (for auth responses)
MOCK_USER_DATA = {
    "id": str(DEV_OWNER_ID),
    "email": DEV_OWNER_EMAIL,
    "first_name": "Test",
    "last_name": "User",
    "is_active": True,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
}

# === Test Data for Different Scenarios ===

# Valid update data for PUT tests
VALID_UPDATE_DATA = {
    "name": "Updated Assistant",
    "description": "An updated AI assistant for testing",
    "personality": {
        "traits": ["friendly", "helpful", "professional"],
        "communication_style": "formal",
        "humor_level": 0.5,
        "empathy_level": 0.8,
    },
    "preferences": {
        "conversation_topics": ["technology", "business", "science"],
        "response_length": "long",
        "formality_level": "formal",
    },
    "status": "active"
}

# Invalid update data for validation testing
INVALID_UPDATE_DATA = {
    "name": "",  # Empty name should fail validation
    "description": "A" * 1001,  # Too long description
    "personality": {
        "traits": [],  # Empty traits should fail
        "communication_style": "invalid_style",  # Invalid enum value
        "humor_level": 1.5,  # Out of range (0-1)
        "empathy_level": -0.1,  # Out of range (0-1)
    },
    "preferences": {
        "conversation_topics": [],  # Empty topics should fail
        "response_length": "invalid_length",  # Invalid enum value
        "formality_level": "invalid_level",  # Invalid enum value
    },
    "status": "invalid_status"  # Invalid enum value
}

# Restricted field data (should be rejected)
RESTRICTED_FIELD_DATA = {
    "name": "Updated Assistant",
    "description": "Updated description",
    "id": "new-id-123",  # Should be rejected
    "user_id": "new-user-id",  # Should be rejected
    "created_at": "2023-01-01T00:00:00Z",  # Should be rejected
    "updated_at": "2023-01-01T00:00:00Z",  # Should be rejected
}

# Partial update data (only some fields)
PARTIAL_UPDATE_DATA = {
    "name": "Partially Updated Assistant",
    "status": "inactive"
}

# Valid create data for POST tests
VALID_CREATE_DATA = {
    "name": "New AI Assistant",
    "description": "A brand new AI assistant for testing",
    "personality": MOCK_PERSONALITY,
    "voice_profile": MOCK_VOICE_PROFILE,
    "character_asset": MOCK_CHARACTER_ASSET,
    "preferences": MOCK_PREFERENCES,
    "status": "active"
}

# Invalid create data for validation testing
INVALID_CREATE_DATA = {
    "name": "",  # Empty name should fail validation
    "description": "A" * 1001,  # Too long description
    "personality": {
        "traits": [],  # Empty traits should fail
        "communication_style": "invalid_style",  # Invalid enum value
        "humor_level": 1.5,  # Out of range (0-1)
        "empathy_level": -0.1,  # Out of range (0-1)
    },
    "preferences": {
        "conversation_topics": [],  # Empty topics should fail
        "response_length": "invalid_length",  # Invalid enum value
        "formality_level": "invalid_level",  # Invalid enum value
    },
    "status": "invalid_status"  # Invalid enum value
}

# === JWT Token Helpers ===
def create_expired_token() -> str:
    """Create an expired JWT token for testing"""
    token_data = {
        "sub": DEV_OWNER_EMAIL,
        "user_id": str(DEV_OWNER_ID),
        "email": DEV_OWNER_EMAIL,
        "exp": datetime.now(timezone.utc) - timedelta(hours=1)  # Expired 1 hour ago
    }
    from backend.shared.src.security.security import jwt
    from backend.ai_service.src.config import settings
    secret = settings.JWT_SECRET or "dev-secret"
    return jwt.encode(token_data, secret, algorithm="HS256")

# === Base URLs ===
AUTH_SERVICE_URL = "http://localhost:8001"
AI_SERVICE_URL = "http://localhost:8002"
