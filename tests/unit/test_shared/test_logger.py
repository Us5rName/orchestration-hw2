"""Tests for LogManager."""

from pathlib import Path

import pytest

from debate.shared.logger import LogManager


@pytest.fixture
def log_config(tmp_path: Path) -> dict:
    """Return log config pointing to temp directory."""
    return {
        "log_directory": str(tmp_path / "logs"),
        "max_files": 3,
        "max_lines_per_file": 10,
        "level": "DEBUG",
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    }


class TestLogManagerInit:
    """Test LogManager initialization."""

    def test_creates_log_directory(self, log_config: dict) -> None:
        """LogManager creates log directory if missing."""
        LogManager(log_config)
        assert Path(log_config["log_directory"]).exists()

    def test_sets_log_level(self, log_config: dict) -> None:
        """LogManager sets the correct log level."""
        lm = LogManager(log_config)
        import logging

        assert lm.logger.level == logging.DEBUG


class TestLogManagerWrite:
    """Test LogManager logging."""

    def test_write_creates_file(self, log_config: dict) -> None:
        """Logging creates a log file."""
        lm = LogManager(log_config)
        lm.info("test message")
        log_files = list(Path(log_config["log_directory"]).glob("*.log"))
        assert len(log_files) >= 1

    def test_write_appends_message(self, log_config: dict) -> None:
        """Log message appears in the file."""
        lm = LogManager(log_config)
        lm.info("hello world")
        log_files = list(Path(log_config["log_directory"]).glob("*.log"))
        content = log_files[-1].read_text(encoding="utf-8")
        assert "hello world" in content


class TestLogManagerRotation:
    """Test FIFO log rotation."""

    def test_rotates_when_limit_reached(self, log_config: dict) -> None:
        """Old files removed when max_files exceeded."""
        lm = LogManager(log_config)
        for i in range(50):
            lm.info(f"message {i}")
        log_files = list(Path(log_config["log_directory"]).glob("*.log"))
        assert len(log_files) <= log_config["max_files"]
