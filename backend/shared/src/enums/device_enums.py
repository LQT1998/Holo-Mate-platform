"""
Device-related enums
"""

from enum import Enum as PyEnum


class DeviceStatus(PyEnum):
    """Device status enum"""
    online = "online"
    offline = "offline"
    unpaired = "unpaired"
    error = "error"


class DeviceType(PyEnum):
    """Device type enum"""
    hologram_fan = "hologram_fan"
    mobile_app = "mobile_app"
    web_app = "web_app"
    unity_client = "unity_client"
