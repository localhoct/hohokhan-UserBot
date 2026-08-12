from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from time import monotonic


@dataclass(slots=True)
class RateLimitResult:
    allowed: bool
    retry_after: int = 0


class RateLimiter:
    """In-memory sliding-window limiter; it never stores message contents."""

    def __init__(self, messages: int, window_seconds: int, penalty_seconds: int) -> None:
        self.messages = messages
        self.window_seconds = window_seconds
        self.penalty_seconds = penalty_seconds
        self._events: dict[int, deque[float]] = defaultdict(deque)
        self._blocked_until: dict[int, float] = {}

    def check(self, user_id: int, now: float | None = None) -> RateLimitResult:
        current = monotonic() if now is None else now
        blocked_until = self._blocked_until.get(user_id, 0.0)
        if blocked_until > current:
            return RateLimitResult(False, max(1, int(blocked_until - current)))
        self._blocked_until.pop(user_id, None)

        queue = self._events[user_id]
        cutoff = current - self.window_seconds
        while queue and queue[0] <= cutoff:
            queue.popleft()
        queue.append(current)

        if len(queue) > self.messages:
            queue.clear()
            self._blocked_until[user_id] = current + self.penalty_seconds
            return RateLimitResult(False, self.penalty_seconds)
        return RateLimitResult(True)
