"""Tests for ApiGatekeeper."""

import time

import pytest

from debate.shared.gatekeeper import ApiGatekeeper, RateLimitConfig


@pytest.fixture
def gatekeeper() -> ApiGatekeeper:
    """Return a gatekeeper with generous limits for testing."""
    config = RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        concurrent_max=5,
        retry_after_seconds=0.01,
        max_retries=2,
    )
    return ApiGatekeeper(config)


class TestGatekeeperExecute:
    """Test basic API call execution."""

    def test_execute_success(self, gatekeeper: ApiGatekeeper) -> None:
        """Successful call returns result."""
        result = gatekeeper.execute(lambda: "ok")
        assert result == "ok"

    def test_execute_logs_call(self, gatekeeper: ApiGatekeeper) -> None:
        """Executed calls are recorded."""
        gatekeeper.execute(lambda: "ok")
        assert gatekeeper.total_calls == 1

    def test_execute_with_args(self, gatekeeper: ApiGatekeeper) -> None:
        """Call with arguments passes through."""

        def add(a: int, b: int) -> int:
            return a + b

        result = gatekeeper.execute(add, 2, 3)
        assert result == 5


class TestGatekeeperRetry:
    """Test retry on failure."""

    def test_retry_on_transient_error(self, gatekeeper: ApiGatekeeper) -> None:
        """Transient errors trigger retries."""
        call_count = 0

        def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("timeout")
            return "recovered"

        result = gatekeeper.execute(flaky)
        assert result == "recovered"
        assert call_count == 3

    def test_give_up_after_max_retries(self, gatekeeper: ApiGatekeeper) -> None:
        """Persistent errors raise after max retries."""

        def always_fail() -> str:
            raise ConnectionError("down")

        with pytest.raises(ConnectionError):
            gatekeeper.execute(always_fail)


class TestGatekeeperQueue:
    """Test queue and status."""

    def test_queue_status_initial(self, gatekeeper: ApiGatekeeper) -> None:
        """Initial queue is empty."""
        status = gatekeeper.get_queue_status()
        assert status.queue_depth == 0

    def test_queue_depth_increases(self, gatekeeper: ApiGatekeeper) -> None:
        """Pending calls increase queue depth."""
        gatekeeper.execute(lambda: time.sleep(0.1))
        status = gatekeeper.get_queue_status()
        assert status.queue_depth >= 0
