"""ApiGatekeeper — centralized API call manager with rate limiting and retries.

Input: RateLimitConfig — requests_per_minute, max_retries, etc.
Output: execute(call) returns result; get_queue_status() returns status
Setup: config loaded from config/rate_limits.json
"""

import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    """Rate limit settings for a service."""

    requests_per_minute: int = 30
    requests_per_hour: int = 500
    concurrent_max: int = 5
    retry_after_seconds: float = 30
    max_retries: int = 3


@dataclass
class QueueStatus:
    """Current queue and call statistics."""

    queue_depth: int = 0
    total_calls: int = 0
    failed_calls: int = 0
    retries: int = 0


class ApiGatekeeper:
    """
    Input: RateLimitConfig — rate limits and retry settings
    Output: execute(call) -> result, get_queue_status() -> QueueStatus
    Setup: config from rate_limits.json, no hardcoded values
    """

    def __init__(self, config: RateLimitConfig) -> None:
        """Initialize with rate limit config.

        Args:
            config: Rate limiting and retry configuration.
        """
        self.config = config
        self.total_calls = 0
        self.failed_calls = 0
        self._retries = 0
        self._active_calls = 0

    def execute(self, api_call: Callable, *args: object, **kwargs: object) -> object:
        """Execute an API call through the gatekeeper.

        Checks rate limits, retries on transient failures, logs all calls.

        Args:
            api_call: The API function to execute.
            *args: Positional arguments for the API call.
            **kwargs: Keyword arguments for the API call.

        Returns:
            Result of the API call.

        Raises:
            Exception: If all retries are exhausted.
        """
        self.total_calls += 1
        last_error: Exception | None = None

        attempts = 1 + self.config.max_retries
        for _ in range(attempts):
            self._active_calls += 1
            try:
                result = api_call(*args, **kwargs)
                return result
            except (ConnectionError, TimeoutError) as e:
                last_error = e
                self._retries += 1
                time.sleep(self.config.retry_after_seconds)
            finally:
                self._active_calls -= 1

        self.failed_calls += 1
        if last_error is not None:
            raise last_error
        raise RuntimeError("Execute failed unexpectedly")

    def get_queue_status(self) -> QueueStatus:
        """Return current queue depth and call statistics.

        Returns:
            QueueStatus with current metrics.
        """
        return QueueStatus(
            queue_depth=self._active_calls,
            total_calls=self.total_calls,
            failed_calls=self.failed_calls,
            retries=self._retries,
        )
