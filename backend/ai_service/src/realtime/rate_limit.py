from __future__ import annotations
import time
from dataclasses import dataclass


@dataclass
class TokenBucket:
    capacity: int
    refill_tokens: int
    refill_seconds: float
    tokens: float
    last_refill: float

    @classmethod
    def per_10s(cls, capacity: int) -> "TokenBucket":
        return cls(
            capacity=capacity,
            refill_tokens=capacity,
            refill_seconds=10.0,
            tokens=float(capacity),
            last_refill=time.monotonic(),
        )

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        if elapsed <= 0:
            return
        add = (elapsed / self.refill_seconds) * self.refill_tokens
        self.tokens = min(self.capacity, self.tokens + add)
        self.last_refill = now

    def consume(self, amount: float = 1.0) -> bool:
        self._refill()
        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False


