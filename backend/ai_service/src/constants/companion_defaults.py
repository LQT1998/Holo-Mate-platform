"""Default values for AI Companion creation."""

# Default CharacterAsset values
DEFAULT_CHARACTER_ASSET = {
    "character_id": "default_avatar_v1",
    "animations_data": ["idle", "talking", "listening"],
    "emotions_data": ["neutral", "happy", "sad", "excited"],
}

# Default VoiceProfile values
DEFAULT_VOICE_PROFILE = {
    "provider_voice_id": "default_voice_en_us",
    "provider_name": "HoloMate",
    "settings": {
        "speed": 1.0,
        "pitch": 1.0,
        "volume": 1.0,
        "gender": "neutral"
    },
}
