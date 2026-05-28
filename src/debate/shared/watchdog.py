"""Watchdog — process monitoring with keep-alive ping mechanism.

Input: check_interval (float), timeout (float)
Output: is_alive() -> bool, check() triggers callback on death
Setup: ping() must be called regularly to stay alive
"""

import time
from collections.abc import Callable


class Watchdog:
    """
    Input: check_interval (float) — seconds between health checks
           timeout (float) — seconds without ping before death
    Output: is_alive() -> bool, check() -> None (fires callback if dead)
    Setup: ping() resets timer; set_on_death() registers callback
    """

    def __init__(self, check_interval: float = 1.0, timeout: float = 30.0) -> None:
        """Initialize watchdog with timing config.

        Args:
            check_interval: Seconds between health checks.
            timeout: Seconds without ping before considered dead.
        """
        self.check_interval = check_interval
        self.timeout = timeout
        self._last_ping = time.monotonic()
        self._on_death: Callable | None = None

    def ping(self) -> None:
        """Reset the watchdog timer."""
        self._last_ping = time.monotonic()

    def is_alive(self) -> bool:
        """Check if the watchdog has received a ping within timeout.

        Returns:
            True if last ping was within the timeout window.
        """
        elapsed = time.monotonic() - self._last_ping
        return elapsed < self.timeout

    def set_on_death(self, callback: Callable) -> None:
        """Register a callback to fire when watchdog times out.

        Args:
            callback: Zero-argument function to call on death.
        """
        self._on_death = callback

    def check(self) -> None:
        """Check health and fire on-death callback if timed out."""
        if not self.is_alive() and self._on_death is not None:
            self._on_death()
