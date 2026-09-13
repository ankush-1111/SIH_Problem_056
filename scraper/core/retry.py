"""Small, explicit retry helper with safe error classification."""

from functools import wraps
import time
from typing import Callable, TypeVar, Any

from core.logger import get_logger

logger = get_logger("retry")

F = TypeVar("F", bound=Callable[..., Any])


class BlockedError(Exception):
    """Raised when access is blocked or a CAPTCHA/challenge is presented."""


class PermanentSourceError(Exception):
    """Raised for errors that should not be retried (for example 401/403)."""


def with_retry(max_attempts: int = 3, delay_seconds: float = 2.0):
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except (BlockedError, PermanentSourceError):
                    raise
                except Exception as exc:
                    last_error = exc
                    if attempt == max_attempts:
                        raise
                    sleep_for = delay_seconds * (2 ** (attempt - 1))
                    logger.warning(
                        f"{func.__qualname__} failed on attempt {attempt}/{max_attempts}: {exc}; "
                        f"retrying in {sleep_for:.1f}s"
                    )
                    time.sleep(sleep_for)
            raise last_error  # pragma: no cover

        return wrapper  # type: ignore[return-value]

    return decorator
