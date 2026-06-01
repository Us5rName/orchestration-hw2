"""Tests for DebateSDK."""

from unittest.mock import MagicMock, patch

import pytest

from debate.sdk.sdk import DebateSDK


@pytest.fixture
def mock_config_data() -> dict:
    """Return valid config data."""
    return {
        "version": "1.00",
        "debate": {
            "topic": "AI is beneficial",
            "max_rounds": 3,
            "request_timeout_seconds": 60,
        },
        "agents": {
            "judge": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.3},
            "pro": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.7},
            "con": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.7},
        },
        "gatekeeper": {
            "requests_per_minute": 30,
            "requests_per_hour": 500,
            "max_retries": 3,
            "retry_delay_seconds": 5,
        },
        "logging": {
            "log_directory": "logs",
            "max_files": 20,
            "max_lines_per_file": 500,
        },
    }


@pytest.fixture
def sdk(mock_config_data: dict) -> DebateSDK:
    """Return a DebateSDK instance with mocked config."""

    def mock_get(key: str, default=None):
        return mock_config_data.get(key, default)

    with patch("debate.sdk.sdk.ConfigManager") as mock_cm:
        mock_cm.return_value.get = MagicMock(side_effect=mock_get)
        return DebateSDK(config_path="config/setup.json")


class TestSDKInit:
    """Test DebateSDK initialization."""

    def test_creates_logger(self, sdk: DebateSDK) -> None:
        """SDK initializes a logger."""
        assert sdk.logger is not None

    def test_creates_gatekeeper(self, sdk: DebateSDK) -> None:
        """SDK initializes a gatekeeper."""
        assert sdk.gatekeeper is not None

    def test_creates_watchdog(self, sdk: DebateSDK) -> None:
        """SDK initializes a watchdog."""
        assert sdk.watchdog is not None


class TestSDKRunDebate:
    """Test running a debate via SDK."""

    def test_run_debate_returns_result(self, sdk: DebateSDK) -> None:
        """run_debate returns a verdict dict."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.run.return_value = {
            "winner": "pro",
            "pro_score": 80,
            "con_score": 70,
            "justification": "Better arguments",
            "history": [],
        }
        with patch.object(sdk, "_create_orchestrator", return_value=mock_orchestrator):
            result = sdk.run_debate()
        assert result["winner"] == "pro"


class TestSDKGetLogs:
    """Test log retrieval."""

    def test_get_logs_no_file(self, sdk: DebateSDK) -> None:
        """get_logs returns message when no log file exists."""
        with patch("pathlib.Path.exists", return_value=False):
            result = sdk.get_logs()
        assert result == ["No log file found."]

    def test_get_logs_with_file(self, sdk: DebateSDK) -> None:
        """get_logs returns lines from existing log file."""
        fake_lines = ["line1", "line2", "line3"]
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.read_text", return_value="\n".join(fake_lines)),
        ):
            result = sdk.get_logs(count=2)
        assert result == ["line2", "line3"]
