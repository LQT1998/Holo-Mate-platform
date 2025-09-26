"""
Voice Profile related enums
"""

from enum import Enum as PyEnum


class VoiceProfileStatus(PyEnum):
    """Voice profile status enum"""
    active = "active"
    inactive = "inactive"
    archived = "archived"


class VoiceProvider(PyEnum):
    """Voice provider enum"""
    elevenlabs = "elevenlabs"
    azure = "azure"
    google = "google"
    amazon = "amazon"
    openai = "openai"
    custom = "custom"
