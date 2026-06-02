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


class TestLogManagerPaths:
    """Test that LogManager resolves log paths correctly."""

    def test_log_dir_is_absolute_for_absolute_config(self, log_config: dict) -> None:
        """Absolute log_directory is stored as-is (absolute)."""
        lm = LogManager(log_config)
        assert lm.log_dir.is_absolute()
        assert lm.log_dir == Path(log_config["log_directory"])

    def test_log_file_is_absolute(self, log_config: dict) -> None:
        """log_file property returns an absolute Path."""
        lm = LogManager(log_config)
        assert lm.log_file.is_absolute()
        assert lm.log_file.name == "debate.log"

    def test_relative_log_dir_anchors_to_project_root(self) -> None:
        """Relative log_directory is resolved relative to PROJECT_ROOT."""
        from debate.shared.paths import PROJECT_ROOT

        cfg = {
            "log_directory": "logs",
            "max_files": 5,
            "max_lines_per_file": 100,
            "level": "INFO",
            "format": "%(message)s",
        }
        lm = LogManager(cfg)
        assert lm.log_dir == PROJECT_ROOT / "logs"
        assert lm.log_dir.is_absolute()

    def test_log_dir_preserves_absolute_path(self, tmp_path: Path) -> None:
        """Absolute log_directory from a different location is preserved."""
        cfg = {
            "log_directory": str(tmp_path / "custom_logs"),
            "max_files": 3,
            "max_lines_per_file": 50,
            "level": "INFO",
            "format": "%(message)s",
        }
        lm = LogManager(cfg)
        assert lm.log_dir == tmp_path / "custom_logs"
