"""Tests for Watchdog."""

import time

import pytest

from debate.shared.watchdog import Watchdog


@pytest.fixture
def watchdog() -> Watchdog:
    """Return a watchdog with short intervals for testing."""
    return Watchdog(check_interval=0.05, timeout=0.2)


class TestWatchdogKeepAlive:
    """Test keep-alive ping mechanism."""

    def test_initially_alive(self, watchdog: Watchdog) -> None:
        """Watchdog is alive after creation."""
        assert watchdog.is_alive()

    def test_ping_resets_timer(self, watchdog: Watchdog) -> None:
        """Pinging keeps the watchdog alive."""
        watchdog.ping()
        assert watchdog.is_alive()

    def test_timeout_without_ping(self, watchdog: Watchdog) -> None:
        """Watchdog dies after timeout without ping."""
        time.sleep(0.3)
        assert not watchdog.is_alive()


class TestWatchdogCallback:
    """Test on-death callback."""

    def test_callback_on_death(self, watchdog: Watchdog) -> None:
        """Callback fires when watchdog times out."""
        callback_fired = False

        def on_death() -> None:
            nonlocal callback_fired
            callback_fired = True

        watchdog.set_on_death(on_death)
        time.sleep(0.3)
        watchdog.check()
        assert callback_fired
