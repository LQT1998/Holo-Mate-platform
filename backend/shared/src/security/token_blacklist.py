"""
DEV-only token blacklist for immediate token revocation.
"""

from typing import Set

# DEV-only in-memory blacklist (per-process)
_BLACKLIST: Set[str] = set()

def dev_blacklist_add(token: str) -> None:
    """Add token to DEV blacklist."""
    _BLACKLIST.add(token)

def dev_blacklisted(token: str) -> bool:
    """Check if token is blacklisted in DEV mode."""
    return token in _BLACKLIST

def dev_blacklist_clear() -> None:
    """Clear DEV blacklist (for testing)."""
    _BLACKLIST.clear()
