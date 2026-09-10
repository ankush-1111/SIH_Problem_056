"""Per-source polite request pacing."""

import time
from threading import Lock


class RateLimiter:
    def __init__(self, default_min_interval_seconds: float = 3.0):
        self.default_min_interval_seconds = default_min_interval_seconds
        self._last_request: dict[str, float] = {}
        self._lock = Lock()

    def wait_if_needed(self, source_name: str, min_interval_seconds: float | None = None) -> None:
        interval = min_interval_seconds or self.default_min_interval_seconds
        with self._lock:
            last = self._last_request.get(source_name)
            if last is not None:
                remaining = interval - (time.monotonic() - last)
                if remaining > 0:
                    time.sleep(remaining)
            self._last_request[source_name] = time.monotonic()


rate_limiter = RateLimiter()
