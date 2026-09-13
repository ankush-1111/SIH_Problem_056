import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from .retry import BlockedError, PermanentSourceError

logger = logging.getLogger("resilience")

def is_retryable_exception(exception):
    return not isinstance(exception, (BlockedError, PermanentSourceError))

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info("Circuit breaker state: HALF-OPEN")
                self.state = "HALF-OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF-OPEN" or self.failures > 0:
                 logger.info("Circuit breaker state: CLOSED")
            self.failures = 0
            self.state = "CLOSED"
            return result
        except (BlockedError, PermanentSourceError):
            # Don't increment failure count for these
            raise
        except Exception as e:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
                self.last_failure_time = time.time()
                logger.error(f"Circuit breaker state: OPEN. Failures: {self.failures}")
            raise e

def with_retry(func):
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(is_retryable_exception)
    )(func)
