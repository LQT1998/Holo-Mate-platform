from __future__ import annotations
import time
from typing import Dict, Tuple


class TypingDebounce:
    def __init__(self, min_interval_sec: float = 1.0) -> None:
        self.min_interval = min_interval_sec
        self.last_emit: Dict[Tuple[str, str], float] = {}

    def should_emit(self, user_id: str, cid: str) -> bool:
        now = time.monotonic()
        key = (user_id, cid)
        last = self.last_emit.get(key, 0.0)
        if now - last >= self.min_interval:
            self.last_emit[key] = now
            return True
        return False


typing_debounce = TypingDebounce()
